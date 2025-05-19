import os
import django
import psycopg2
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
import json
import logging
from django.db import transaction
from django.conf import settings

# Django 설정 로드
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from mynews.models import NewsArticle

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_db_connection():
    """PostgreSQL 데이터베이스 연결"""
    return psycopg2.connect(
        dbname=settings.DATABASES['default']['NAME'],
        user=settings.DATABASES['default']['USER'],
        password=settings.DATABASES['default']['PASSWORD'],
        host=settings.DATABASES['default']['HOST'],
        port=settings.DATABASES['default']['PORT']
    )

def get_es_client():
    """Elasticsearch 클라이언트 생성"""
    return Elasticsearch(
        hosts=[settings.ELASTICSEARCH_HOST],
        basic_auth=(settings.ELASTICSEARCH_USER, settings.ELASTICSEARCH_PASSWORD)
    )

def prepare_es_document(article):
    """Elasticsearch 문서 형식으로 변환"""
    return {
        'title': article['title'],
        'content': article['content'],
        'writer': article['writer'],
        'category': article['category'],
        'keywords': article['keywords'] if article['keywords'] else [],
        'write_date': article['write_date'].isoformat() if article['write_date'] else None,
        'url': article['url']
    }

def sync_to_elasticsearch(article_id=None):
    """PostgreSQL의 변경된 데이터를 Elasticsearch에 동기화"""
    try:
        # 데이터베이스 연결
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Elasticsearch 클라이언트 생성
        es = get_es_client()
        
        # 쿼리 조건 설정
        if article_id:
            cursor.execute("""
                SELECT id, title, writer, write_date, category, content, url, 
                       keywords
                FROM news_article
                WHERE id = %s
            """, (article_id,))
        else:
            cursor.execute("""
                SELECT id, title, writer, write_date, category, content, url, 
                       keywords
                FROM news_article
                WHERE updated_at > now() - interval '10 minutes'
            """)
        
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        # Elasticsearch에 문서 업데이트
        for row in rows:
            article = dict(zip(columns, row))
            es_doc = prepare_es_document(article)
            
            # 문서 업데이트 또는 생성
            es.update(
                index='news',
                id=str(article['id']),
                body={
                    'doc': es_doc,
                    'doc_as_upsert': True
                }
            )
        
        logger.info(f"동기화 완료: {len(rows)}개의 문서 처리됨")
        
    except Exception as e:
        logger.error(f"동기화 중 오류 발생: {str(e)}")
        raise
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def full_sync():
    """전체 데이터 동기화"""
    try:
        # 데이터베이스 연결
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Elasticsearch 클라이언트 생성
        es = get_es_client()
        
        # 모든 데이터 조회
        cursor.execute("""
            SELECT id, title, writer, write_date, category, content, url, 
                   keywords
            FROM news_article
        """)
        
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        # Elasticsearch에 문서 업데이트
        for row in rows:
            article = dict(zip(columns, row))
            es_doc = prepare_es_document(article)
            
            # 문서 업데이트 또는 생성
            es.update(
                index='news',
                id=str(article['id']),
                body={
                    'doc': es_doc,
                    'doc_as_upsert': True
                }
            )
        
        logger.info(f"전체 동기화 완료: {len(rows)}개의 문서 처리됨")
        
    except Exception as e:
        logger.error(f"동기화 중 오류 발생: {str(e)}")
        raise
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@transaction.atomic
def sync_new_article(article_data):
    """새로운 기사 동기화"""
    try:
        # PostgreSQL에 저장
        article = NewsArticle.objects.create(**article_data)
        
        # Elasticsearch에 동기화
        sync_to_elasticsearch(article.id)
        
        logger.info(f"새로운 기사 동기화 완료: {article.title}")
        return article
        
    except Exception as e:
        logger.error(f"새로운 기사 동기화 중 오류 발생: {str(e)}")
        raise

if __name__ == '__main__':
    # 전체 동기화 실행
    full_sync() 