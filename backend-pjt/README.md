# SSAFY PJT - Custom News Backend

**사용자 맞춤형 뉴스 추천 시스템을 위한 백엔드 서비스**

-----

## 프로젝트 개요

본 프로젝트는 RSS 기반 뉴스 수집 데이터를 활용하여 사용자 관심사에 맞춘 뉴스 추천 기능을 제공하는 백엔드 시스템입니다.  
Django REST Framework 기반으로 API 서버를 구축하였으며 이후, PostgreSQL과 pgvector를 활용한 벡터 기반 뉴스 유사도 추천 기능을 포함하게 됩니다.

---

## 시작하기

### 1. 가상환경 설정

```bash
python3.10 -m venv ~/venvs/backend-pjt
source ~/venvs/backend-pjt/bin/activate
pip install -r requirements.txt
```

---

### 2. Django 설정

`myproject/settings.py` 내 `DATABASES` 설정

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

---

### 3. 마이그레이션 및 서버 실행

```bash
python manage.py migrate
python manage.py runserver
```

---

## 주요 기능

### 1. 뉴스 목록 제공
- RSS를 통해 수집된 뉴스 데이터 제공
- 좋아요 기능

### 2. 개인화 대시보드
- 뉴스 소비 패턴 시각화
- 관심 분야 기반 트렌드 분석
- 직관적인 사용자 인터페이스 제공

### 3. 사용자 계정 관리
- 회원가입 및 로그인 기능
- 인증

---

## 기술 스택

- Python 3.10
- Django
- PostgreSQL
- 인증: JWT(해당 코드 기준) or Session(코드 변경)

---

## 참고용 API 명세
JWT를 안 쓴다면 "Authorization 헤더만 빠지고, 나머지 요청 형식(API URL, Method, Body, Response 등)은 동일하게 참고 가능

- 해당 레포지토리의 API_Sheet.pdf 참고

---

## 프로젝트 구조 예시

```
backend/
├── README.md
├── manage.py
├── mynews
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── enums.py
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   ├── __init__.py
│   └── mocking.py
├── myproject
│   ├── __init__.py
│   ├── asgi.py
│   ├── response.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── requirements.txt
```
---
