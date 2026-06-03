# news-recommendation-system

## 프로젝트 개요
이 프로젝트는 뉴스 데이터를 수집·처리·분석하여 사용자에게 맞춤형 뉴스 큐레이션 서비스를 제공하는 종합 플랫폼입니다. 프론트엔드, 백엔드, 데이터 파이프라인으로 구성된 모노레포 형태의 풀스택 애플리케이션입니다.

## 시스템 아키텍처

### 1. 프론트엔드 ([front-pjt](./front-pjt/README.md))
- **기술 스택**: Vue 3, Vite, Pinia, Vue Router, Chart.js
- **주요 기능**:
  - 회원가입 / 로그인 (JWT 기반 인증)
  - 맞춤형 뉴스 큐레이팅 및 추천 피드
  - 뉴스 상세 / 좋아요 / 관련 뉴스
  - 사용자 활동 시각화 대시보드 (Chart.js)
  - 뉴스 검색

### 2. 백엔드 ([backend-pjt](./backend-pjt/README.md))
- **기술 스택**: Python 3.10, Django 5.1 + Django REST Framework, PostgreSQL + pgvector, Elasticsearch 8.17, OpenAI / LangChain
- **인증**: JWT (djangorestframework-simplejwt + dj-rest-auth + django-allauth)
- **주요 기능**:
  - RESTful API 서비스
  - 사용자 인증 및 계정 관리
  - 뉴스 데이터 제공 및 좋아요
  - pgvector 기반 벡터(의미) 검색 및 유사 기사 추천
  - Elasticsearch 기반 텍스트 검색 / 추천 / 자동완성

### 3. 데이터 파이프라인 ([data-pjt](./data-pjt/README.md))
- **기술 스택**: Apache Kafka, Apache Flink(PyFlink), Apache Spark, Apache Airflow, OpenAI API
- **주요 구성요소**:
  - **Producer**: 매일경제 RSS 수집 후 Kafka 전송
  - **Consumer**: Kafka → Flink 실시간 수신 → OpenAI 전처리(키워드/임베딩/분류) → PostgreSQL + Elasticsearch 저장
  - **Batch**: Airflow + Spark 기반 일일 리포트 배치 환경 ([data-pjt/batch](./data-pjt/batch/README.md))

## 주요 기능
1. **맞춤형 뉴스 큐레이션**
   - 사용자 관심사 기반 뉴스 추천
   - 실시간 뉴스 수집 및 업데이트
   - 개인화된 뉴스 피드 및 대시보드

2. **고급 검색 기능**
   - pgvector 기반 벡터(의미) 검색
   - Elasticsearch 기반 텍스트(키워드) 검색
   - 카테고리 / 날짜 필터링 및 정렬

3. **데이터 처리 및 분석**
   - Kafka + Flink 실시간 스트리밍 처리
   - OpenAI(gpt-4o-mini, text-embedding-3-small) 기반 전처리
   - Airflow + Spark 기반 배치 처리 환경

## 기술적 특징
- **실시간 처리**: Kafka + Flink(PyFlink)를 통한 스트리밍 데이터 처리
- **AI 전처리**: OpenAI API 기반 키워드 추출 · 임베딩 · 카테고리 분류
- **하이브리드 검색**: pgvector 벡터 검색과 Elasticsearch 텍스트 검색의 조합
- **보안**: JWT 기반 사용자 인증 및 권한 관리

## 프로젝트 구조
```
├── front-pjt/          # 프론트엔드 (Vue 3 + Vite)
├── backend-pjt/        # 백엔드 API 서버 (Django + DRF)
└── data-pjt/           # 데이터 파이프라인
    ├── producer/       # RSS → Kafka
    ├── consumer/       # Kafka → Flink → 전처리 → 저장
    └── batch/          # Airflow + Spark 배치 환경
```

## 전체 구동 순서
1. **데이터 파이프라인** ([data-pjt](./data-pjt/README.md)): Kafka 기동 → Consumer(Flink) 실행 → Producer 실행 → 뉴스 수집·전처리·저장
2. **백엔드** ([backend-pjt](./backend-pjt/README.md)): PostgreSQL/Elasticsearch 준비 → 마이그레이션 → `runserver` (기본 8000)
3. **프론트엔드** ([front-pjt](./front-pjt/README.md)): `.env`에 백엔드 주소 설정 → `npm install` → `npm run dev`
