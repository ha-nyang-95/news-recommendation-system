import os
import json
import requests
from elasticsearch import Elasticsearch
from django.conf import settings

def setup_kibana_dashboard():
    """Kibana 대시보드 설정"""
    try:
        # Elasticsearch 클라이언트 생성
        es = Elasticsearch(
            hosts=[settings.ELASTICSEARCH_HOST],
            basic_auth=(settings.ELASTICSEARCH_USER, settings.ELASTICSEARCH_PASSWORD)
        )

        # Kibana API 엔드포인트
        kibana_url = settings.ELASTICSEARCH_HOST.replace('9200', '5601')
        
        # 대시보드 설정 파일 읽기
        dashboard_path = os.path.join(os.path.dirname(__file__), 'kibana_dashboard.json')
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            dashboard_config = json.load(f)

        # 대시보드 설정 API 호출
        response = requests.post(
            f"{kibana_url}/api/saved_objects/_import",
            headers={
                'kbn-xsrf': 'true',
                'Content-Type': 'application/json'
            },
            json=dashboard_config
        )

        if response.status_code == 200:
            print("Kibana 대시보드 설정이 완료되었습니다.")
        else:
            print(f"대시보드 설정 중 오류 발생: {response.text}")

    except Exception as e:
        print(f"Kibana 설정 중 오류 발생: {str(e)}")

if __name__ == '__main__':
    # Django 설정 로드
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
    import django
    django.setup()
    
    # 대시보드 설정 실행
    setup_kibana_dashboard() 