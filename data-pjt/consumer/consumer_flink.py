from elasticsearch import Elasticsearch
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream.connectors import FlinkKafkaConsumer
from datetime import datetime

import os
import json
from preprocess import transform_extract_keywords, transform_to_embedding, transform_classify_category
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Kafka 설정
env = StreamExecutionEnvironment.get_execution_environment()

# Kafka connector JAR 등록
kafka_connector_path = os.getenv("KAFKA_CONNECTOR_PATH")
env.add_jars(f"file://{kafka_connector_path}")

# Kafka Consumer 설정
kafka_props = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'flink_consumer_group'
}

consumer = FlinkKafkaConsumer(
    topics='news',
    deserialization_schema=SimpleStringSchema(),
    properties=kafka_props
)

# Kafka에서 메시지 수신
stream = env.add_source(consumer)

# JSON 파일 저장 디렉토리 설정
JSON_OUTPUT_DIR = "../batch/data/realtime"
os.makedirs(JSON_OUTPUT_DIR, exist_ok=True)


# ES 클라이언트 초기화 (전역에서 한 번만 생성)
es = Elasticsearch("http://localhost:9200")
index_name = "news"

def save_to_elasticsearch(article):
    try:
        es_doc = {
            "title": article["title"],
            "content": article["content"],
            "writer": article.get("writer", "알 수 없음"),
            "category": article["category"],
            "keywords": article["keywords"],
            "write_date": article.get("write_date", "2025-01-01")
        }

        es.update(
            index=index_name,
            id=article["link"],  # ID로 URL 또는 링크 사용
            body={
                "doc": es_doc,
                "doc_as_upsert": True
            }
        )
        print(f"[ES 업서트 완료] {article['title']}")

    except Exception as e:
        print(f"[ES 업서트 오류] {e}")


# DB 저장 함수
def save_to_postgres(article):
    try:
        conn = psycopg2.connect(
            dbname="news",
            user=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
            host="localhost",
            port="5432"
        )
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO news_article (title, writer, write_date, category, content, url, keywords, embedding)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                article["title"],
                article.get("writer", "알 수 없음"),
                article.get("write_date", "2025-01-01"),
                article["category"],
                article["content"],
                article["link"],
                json.dumps(article["keywords"], ensure_ascii=False),
                article["embedding"]
            )
        )
        conn.commit()
        cur.close()
        conn.close()
        print(f"[저장 완료] {article['title']}")
    except Exception as e:
        print(f"[DB 오류] {e}")



# JSON 파일 저장 함수

def save_to_json(data):
    try:

        # 파일명에 타임스탬프 추가 (예: news_20250502123456.json)
        timestamp = datetime.now().strftime("%Y%m%d%H%M")
        filename = f"news_{timestamp}.json"
        filepath = os.path.join(JSON_OUTPUT_DIR, filename)

        # 데이터 형식 변환
        formatted_data = {
            "write_date": data.get("write_date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "keywords": data.get("keywords", [])
        }

        # 기존 파일이 있으면 읽어서 추가, 없으면 새 리스트 생성
        existing_data = []
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
                if not isinstance(existing_data, list):
                    existing_data = [existing_data]
            except json.JSONDecodeError:
                existing_data = []

        # 새로운 데이터 추가
        existing_data.append(formatted_data)

        # JSON 파일로 저장
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=4)
        print(f"[JSON 저장 완료] {filepath}")

    except Exception as e:
        print(f"[JSON 저장 오류] {e}")

# Flink에서 처리할 함수
def process_and_save(json_str):
    try:
        data = json.loads(json_str)

        content = data.get("content", "")
        if not content or content == "[본문 없음]":
            return

        # 전처리
        keywords = transform_extract_keywords(content)
        embedding = transform_to_embedding(content)
        category = transform_classify_category(content)

        data["keywords"] = keywords
        data["embedding"] = embedding
        data["category"] = category

        # print(data)

        save_to_postgres(data)
        save_to_json(data)
        save_to_elasticsearch(data)


    except Exception as e:
        print(f"[처리 오류] {e}")


def update_missing_embeddings():
    try:
        conn = psycopg2.connect(
            dbname="news",
            user=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
            host="localhost",
            port="5432"
        )
        cur = conn.cursor()

        # embedding이 NULL인 기사 가져오기
        cur.execute("SELECT id, content FROM news_article WHERE embedding IS NULL")
        rows = cur.fetchall()
        print(f"[임베딩 업데이트 대상] {len(rows)}건")

        for id_, content in rows:
            if not content or content == "[본문 없음]":
                continue
            try:
                embedding = transform_to_embedding(content)
                if embedding and len(embedding) == 1536:
                    cur.execute(
                        "UPDATE news_article SET embedding = %s WHERE id = %s",
                        (embedding, id_)
                    )
                    print(f"[업데이트 완료] ID: {id_}")
                else:
                    print(f"[스킵] 차원 오류 또는 빈 임베딩: ID {id_}")
            except Exception as inner_e:
                print(f"[임베딩 생성 실패] ID: {id_} → {inner_e}")

        conn.commit()
        cur.close()
        conn.close()
        print("[✅ 누락 임베딩 업데이트 완료]")

    except Exception as e:
        print(f"[DB 연결 오류] {e}")


# Flink 내에서 각 메시지를 처리
stream.map(process_and_save)

update_missing_embeddings()

env.execute("Flink Kafka Consumer Job")

