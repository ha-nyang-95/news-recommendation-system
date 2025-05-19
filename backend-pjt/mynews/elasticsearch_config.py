from elasticsearch import Elasticsearch
from django.conf import settings

# Elasticsearch 클라이언트 설정
es_client = Elasticsearch(
    hosts=[settings.ELASTICSEARCH_HOST],
    basic_auth=(settings.ELASTICSEARCH_USER, settings.ELASTICSEARCH_PASSWORD)
)

# 뉴스 인덱스 매핑 설정
NEWS_INDEX_MAPPING = {
    "mappings": {
        "properties": {
            "title": {
                "type": "text",
                "analyzer": "korean",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    },
                    "suggest": {
                        "type": "completion",
                        "analyzer": "simple",
                        "preserve_separators": True,
                        "preserve_position_increments": True,
                        "max_input_length": 50
                    }
                }
            },
            "content": {
                "type": "text",
                "analyzer": "korean",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                }
            },
            "writer": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                }
            },
            "category": {
                "type": "keyword"
            },
            "keywords": {
                "type": "keyword",
                "fields": {
                    "suggest": {
                        "type": "completion",
                        "analyzer": "simple",
                        "preserve_separators": True,
                        "preserve_position_increments": True,
                        "max_input_length": 50
                    }
                }
            },
            "write_date": {"type": "date"},
            "url": {"type": "keyword"},
            "view_count": {"type": "integer"},
            "search_count": {"type": "integer"},
            "is_active": {"type": "boolean"}
        }
    },
    "settings": {
        "analysis": {
            "analyzer": {
                "korean": {
                    "type": "custom",
                    "tokenizer": "nori_tokenizer",
                    "filter": [
                        "nori_readingform",
                        "lowercase",
                        "trim",
                        "nori_number"
                    ]
                }
            },
            "tokenizer": {
                "nori_tokenizer": {
                    "type": "nori_tokenizer",
                    "decompound_mode": "mixed"
                }
            }
        },
        "index": {
            "number_of_shards": 3,
            "number_of_replicas": 1,
            "refresh_interval": "1s"
        }
    }
}

def create_news_index():
    """뉴스 인덱스 생성"""
    if not es_client.indices.exists(index="news"):
        es_client.indices.create(index="news", body=NEWS_INDEX_MAPPING)
        print("뉴스 인덱스가 생성되었습니다.")
    else:
        print("뉴스 인덱스가 이미 존재합니다.")

def update_index_settings():
    """인덱스 설정 업데이트"""
    if es_client.indices.exists(index="news"):
        es_client.indices.put_settings(
            index="news",
            body=NEWS_INDEX_MAPPING["settings"]
        )
        print("인덱스 설정이 업데이트되었습니다.")
    else:
        print("인덱스가 존재하지 않습니다.") 