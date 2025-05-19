from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from mynews.sync_script import sync_to_elasticsearch

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'news_sync',
    default_args=default_args,
    description='PostgreSQL에서 Elasticsearch로 뉴스 데이터 동기화',
    schedule_interval=timedelta(minutes=10),
    start_date=datetime(2024, 1, 1),
    catchup=False
)

sync_task = PythonOperator(
    task_id='sync_to_elasticsearch',
    python_callable=sync_to_elasticsearch,
    dag=dag
) 