# 뉴스 기사 검색 시스템

## 1. 시스템 개요

이 프로젝트는 뉴스 데이터를 다음 구성으로 처리합니다

```
[Kafka] → [Flink 실시간 처리]
             └→ PostgreSQL (정형 데이터 저장)
             └→ Elasticsearch (검색용 저장)
                    ↑
         [Airflow 배치 동기화 (보조)]
```

- 실시간 수집: Kafka → Flink → PostgreSQL + Elasticsearch
- 주기적 동기화: Airflow가 PostgreSQL의 수정 데이터를 Elasticsearch로 반영
- 검색 API: Django REST Framework로 구현
- 검색 UI: Vue.js 기반으로 사용자 인터페이스 제공
- 시각화: Kibana로 검색 지표 및 트렌드 시각화

---

## 2. 실시간 수집 및 저장 (Flink + PostgreSQL + Elasticsearch)

### 테이블 구조

```sql
CREATE TABLE news_article (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    writer VARCHAR(255) NOT NULL,
    write_date TIMESTAMP NOT NULL,
    category VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    url VARCHAR(200) UNIQUE NOT NULL,
    keywords JSON DEFAULT '[]'::json,
    embedding VECTOR(1536) NOT NULL,
    updated_at TIMESTAMP DEFAULT now()  -- 갱신 시점 자동 기록을 위한 추가 컬럼
);
```

> `updated_at`은 `ON CONFLICT` 시점마다 `now()`로 갱신되도록 코드에서 업데이트 필요

---

### Elasticsearch 인덱스 매핑 예시

- 색인에는 검색에 필요한 필드만 포함

```json
PUT /news
{
  "mappings": {
    "properties": {
      "title":     { "type": "text" },     // 검색 대상
      "content":   { "type": "text" },     // 검색 대상
      "writer":    { "type": "text" },     // 검색 대상
      "category":  { "type": "keyword" },  // 필터링용
      "keywords":  { "type": "keyword" },  // 필터/정렬용
      "write_date":{ "type": "date" }      // 정렬 및 기간 필터
    }
  }
}
```

> 검색 대상 필드: title, content, writer  
> 필터링용 필드: category, keywords  
> 정렬/범위 필터용 필드: write_date  

---

### 코드 예시 (flink에서의 실시간 처리용 INSERT 쿼리)

```python
# PostgreSQL + Elasticsearch 데이터 저장 예시 (중복 방지 및 갱신 포함)

import psycopg2
from elasticsearch import Elasticsearch, helpers
import json

# PostgreSQL 연결 설정
pg_conn = psycopg2.connect(
    host="localhost",
    dbname="news",
    user="ssafyuser",
    password="ssafy"
)
pg_cursor = pg_conn.cursor()

# Elasticsearch 클라이언트
es = Elasticsearch("http://localhost:9200")
index_name = "news"

# 샘플 데이터
article = {
    "title": "AI Regulation in 2025",
    "writer": "hsj",
    "write_date": "2025-05-14T09:00:00",
    "category": "IT",
    "content": "AI regulations...",
    "url": "https://ai.com/articles/16852",
    "keywords": ["AI", "regulation", "policy"],
    "embedding": [0.01] * 1536  # 예시 벡터
}

# PostgreSQL 저장 쿼리
insert_query = """
INSERT INTO news_article (
    title, writer, write_date, category, content, url, keywords, embedding, updated_at
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, now())
ON CONFLICT (url) DO UPDATE SET
    title = EXCLUDED.title,
    writer = EXCLUDED.writer,
    write_date = EXCLUDED.write_date,
    category = EXCLUDED.category,
    content = EXCLUDED.content,
    keywords = EXCLUDED.keywords,
    embedding = EXCLUDED.embedding,
    updated_at = now()
"""

pg_cursor.execute(insert_query, (
    article["title"], article["writer"], article["write_date"],
    article["category"], article["content"], article["url"],
    json.dumps(article["keywords"]), article["embedding"]
))
pg_conn.commit()

# Elasticsearch upsert 처리 예시
es_doc = {
    "title": article["title"],
    "content": article["content"],
    "writer": article["writer"],
    "category": article["category"],
    "keywords": article["keywords"],
    "write_date": article["write_date"]
}

es.update(
    index=index_name,
    id=article["url"],
    body={
        "doc": es_doc,           # 있으면 이 내용으로 갱신
        "doc_as_upsert": True    # 없으면 새로 생성
    }
)


```

### 설명

- `url` 기준 중복 방지 (UNIQUE)
- 충돌 시 `updated_at` 포함 전체 컬럼 업데이트
- Elasticsearch에는 동일 데이터를 `id=url`로 upsert할 수 있음

---


## 3. 뉴스 검색 API (Django + Elasticsearch) 예시시

### 구성
사용자가 입력한 검색어를 기반으로 Elasticsearch에서 `title`, `content`, `writer` 필드를 대상으로 다양한 형태의 검색으로 최적화 가능

### 코드 예시

```python
# 1단계: Elasticsearch에서 URL만 추출
res = es.search(index="news", query={
    "bool": {
        "should": [
            {"match": {"title": q}},
            {"match": {"content": q}},
            {"match": {"writer": q}},
            {"term": {"keywords": q}}
        ]
    }
})
urls = [hit["_id"] for hit in res["hits"]["hits"]]  # _id = URL

# 2단계: PostgreSQL에서 전체 필드 조회
pg_cursor.execute("""
    SELECT id, title, writer, write_date, category, content, url, keywords, embedding
    FROM news_article
    WHERE url = ANY(%s)
""", (urls,))
results = pg_cursor.fetchall()
```

> endpoint: GET /news/search/
> 고려해야할 부분 
- Elasticsearch는 검색 대상 필터링만 담당하고, 실제 사용자에게 제공되는 전체 데이터는 url을 기준으로 PostgreSQL에서 다시 조회하여 구성합니다.
- 이러한 구조는 검색 성능과 데이터 정합성의 균형을 맞추기 위한 일반적인 분리 구조입니다.

### 검색 결과 예시

```json
{
  "message": "검색 결과입니다",
  "data": [
    {
      "id": 1,
      "title": "AI Regulation in 2025",
      "writer": "hsj",
      "write_date": "2025-05-14T09:00:00",
      "category": "IT",
      "content": "AI regulation details...",
      "url": "https://ai.com/articles/16852",
      "keywords": ["AI", "regulation", "policy"],
      "embedding": [0.01, 0.02, 0.03]
    }
  ]
}
```

---

## 4. 주기적 동기화 (Airflow DAG)

### 개념
누락되거나 갱신되지 못한 데이터를 PostgreSQL에서 기준 시점 이후 변경된 데이터만 추출하여 Elasticsearch에 다시 upsert

### 코드(script) 예시

```python
# PostgreSQL 연결
    pg_conn = psycopg2.connect(
        host="localhost",
        dbname="news",
        user="ssafyuser",
        password="ssafy"
    )
    pg_cursor = pg_conn.cursor()

    # Elasticsearch 연결
    es = Elasticsearch("http://localhost:9200")
    index_name = "news"

    # updated_at 기준 최근 10분 이내 변경된 문서 조회
    pg_cursor.execute("""
        SELECT title, writer, write_date, category, content, url, keywords, embedding
        FROM news_article
        WHERE updated_at > now() - interval '10 minutes'
    """)
    rows = pg_cursor.fetchall()
    columns = [desc[0] for desc in pg_cursor.description]

    # Elasticsearch에 문서 upsert
    for row in rows:
        article = dict(zip(columns, row))
        es_doc = {
            "title": article["title"],
            "content": article["content"],
            "writer": article["writer"],
            "category": article["category"],
            "keywords": article["keywords"],
            "write_date": article["write_date"]
        }

        es.update(
            index=index_name,
            id=article["url"],  # URL을 고유 ID로 사용
            body={
                "doc": es_doc,
                "doc_as_upsert": True
            }
        )
```

### 설명  
- `updated_at`이 최근 10분 이내인 문서만 추출하여 Elasticsearch에 upsert
- 중복 저장이 아닌 **최신 문서 보정용 보조 동기화 작업**

---

## 5. 검색 UI (Vue.js)

- Django 검색 API를 호출하여 사용자 입력에 따른 실시간 검색 결과 출력
- 검색어 입력 → 결과 리스트 표시
- 자동완성, 필터, 정렬 기능 등 향후 확장 가능

---

## 6. Kibana 시각화 (선택)

- Elasticsearch 인덱스를 Kibana에 연결하여 주요 검색 지표 시각화
- 기사 카테고리별 분포, 키워드 트렌드, 작성일 기준 타임라인 분석

---

## 7. 전체 흐름 요약

| 구성 요소 | 설명 |
|------------|------|
| Kafka → Flink | 뉴스 수집 및 실시간 처리 |
| Flink → PostgreSQL | 정형 DB에 저장 및 갱신 처리 |
| Flink → Elasticsearch | 검색용 저장소로 즉시 반영 |
| Airflow | (예시: 10분) 배치 형태로 주기적 데이터 정합성 보완 |
| Django API | 검색 기능 REST API 제공 |
| Vue.js | 사용자 검색 UI |
| Kibana | 검색 트렌드 등 시각화를 통한 모니터링 및 분석 |

---
