# SSAFY PJT - Custom News Backend

**사용자 맞춤형 뉴스 추천 시스템을 위한 백엔드 서비스**

-----

## 프로젝트 개요

RSS 기반으로 수집·전처리된 뉴스 데이터를 활용하여 사용자 관심사에 맞춘 뉴스 추천과 검색 기능을 제공하는 백엔드 시스템입니다.
Django REST Framework 기반으로 API 서버를 구축하였으며, **PostgreSQL + pgvector**를 활용한 벡터 기반 유사도 추천과 **Elasticsearch**를 활용한 텍스트 검색 기능을 함께 제공합니다.

> 상위 프로젝트(모노레포) 개요는 [`../README.md`](../README.md)를 참고하세요.

---

## 기술 스택

| 범주 | 기술 |
| --- | --- |
| 언어 | Python 3.10 |
| 프레임워크 | Django 5.1, Django REST Framework 3.15 |
| 데이터베이스 | PostgreSQL + pgvector (벡터 유사도 검색) |
| 검색 엔진 | Elasticsearch 8.17 (+ django-elasticsearch-dsl) |
| 인증 | JWT — djangorestframework-simplejwt 5.3, dj-rest-auth 6.0, django-allauth 65.1 |
| AI | OpenAI 1.52, LangChain 0.3 |
| 기타 | django-cors-headers, django-health-check, gunicorn |

> 전체 의존성은 [`requirements.txt`](./requirements.txt) 참고.

---

## 시작하기

### 1. 가상환경 설정

```bash
python3.10 -m venv ~/venvs/backend-pjt
source ~/venvs/backend-pjt/bin/activate
pip install -r requirements.txt
```

### 2. 환경 변수 (`.env`)

OpenAI API 키 등 민감 정보는 `.env`로 관리합니다.

```env
OPENAI_API_KEY=your_openai_api_key
```

### 3. Django 데이터베이스 설정

`myproject/settings.py` 내 `DATABASES` 설정 (PostgreSQL)

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "news",
        "USER": "ssafyuser",
        "PASSWORD": "ssafy",
        "HOST": "localhost",
        "PORT": 5432,
    }
}
```

> pgvector 확장이 필요합니다. PostgreSQL에서 `CREATE EXTENSION IF NOT EXISTS vector;` 를 먼저 실행하세요.

### 4. Elasticsearch 설정

`settings.py`의 기본값은 다음과 같습니다. 로컬에 Elasticsearch 8.17이 기동 중이어야 검색 기능이 동작합니다.

```python
ELASTICSEARCH_HOST = 'http://localhost:9200'
ELASTICSEARCH_USER = 'elastic'
ELASTICSEARCH_PASSWORD = 'changeme'
```

### 5. 마이그레이션 및 서버 실행

```bash
python manage.py migrate
python manage.py runserver
```

---

## 주요 기능

### 1. 사용자 계정 관리 (`accounts`)
- 회원가입, 로그인(JWT 토큰 발급), 토큰 갱신
- 내 정보 조회(`/me/`)

### 2. 뉴스 목록 및 상세 (`mynews`)
- 수집된 뉴스 목록 / 상세 제공
- 기사 좋아요
- 관련 뉴스(`/<id>/related/`) 제공

### 3. 추천 (`mynews`)
- **pgvector 기반 벡터 유사도 추천**: 임베딩 컬럼에 대한 `<->` 거리 연산으로 유사 기사 추천 (`/<id>/recommend/`)
- 자세한 내용은 [`vector_search.md`](./vector_search.md) 참고

### 4. 검색 (Elasticsearch)
- 텍스트 검색(`/search/`): 카테고리 / 날짜 필터 지원
- 자동완성 / 추천어(`/suggest/`, `/related-keywords/`)
- `more_like_this` 기반 유사 문서 검색
- 자세한 내용은 [`text_search.md`](./text_search.md) 참고

### 5. 대시보드
- 사용자 뉴스 소비 패턴 / 관심 분야 기반 데이터 제공

> 추천 시스템 설계 배경은 [`맞춤형 큐레이션을 위한 추천 시스템 구현 보고서.md`](./맞춤형%20큐레이션을%20위한%20추천%20시스템%20구현%20보고서.md) 참고.

---

## 인증 방식

본 백엔드는 **JWT 인증**을 사용합니다 (`settings.py`에서 확정).

- `REST_FRAMEWORK.DEFAULT_AUTHENTICATION_CLASSES = JWTAuthentication`
- `REST_AUTH.USE_JWT = True` (dj-rest-auth + allauth 연동)
- Access 토큰 1일 / Refresh 토큰 5일 (`SIMPLE_JWT`)
- 인증이 필요한 요청은 `Authorization: Bearer <access_token>` 헤더 사용

---

## API 명세

- 레포지토리 내 [`API_Sheet.pdf`](./API_Sheet.pdf) 참고

---

## 프로젝트 구조

```
backend-pjt/
├── manage.py
├── requirements.txt
├── API_Sheet.pdf
├── vector_search.md                 # pgvector 벡터 검색 문서
├── text_search.md                   # Elasticsearch 텍스트 검색 문서
├── 맞춤형 큐레이션을 위한 추천 시스템 구현 보고서.md
├── accounts/                        # 사용자 계정 / 인증
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── mynews/                          # 뉴스 / 검색 / 추천
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── enums.py
│   ├── elasticsearch_config.py      # Elasticsearch 클라이언트 설정
│   ├── sync_script.py               # DB → Elasticsearch 동기화
│   ├── setup_kibana.py              # Kibana 대시보드 셋업
│   ├── kibana_dashboard.json
│   ├── mocking.py
│   └── dags/
│       └── news_sync_dag.py         # 뉴스 동기화 Airflow DAG
└── myproject/
    ├── settings.py
    ├── urls.py
    ├── response.py
    ├── asgi.py
    └── wsgi.py
```
