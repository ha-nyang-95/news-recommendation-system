# SSAFYNEWS

> Vue 3 기반 개인 맞춤형 뉴스 큐레이팅 서비스

SSAFY 개인 맞춤형 뉴스 서비스는 사용자의 취향에 맞춘 다양한 뉴스를 제공하며, 이후에는 뉴스 기반 AI 챗봇 기능까지 추가하여 제공하는걸 목표로 합니다.

---

## 주요 기능

- **회원가입 및 로그인**  
  개인 맞춤형 뉴스 큐레이팅 기능

<table>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/aa2e92c8-d4ac-46e6-aa09-36e73c9bd352" width="500"/></td>
    <td><img src="https://github.com/user-attachments/assets/dd88eafa-13e4-4a77-b9b7-479ccbbcefa8" width="500"/></td>
  </tr>
</table>

- **AI 맞춤 뉴스 추천**  
  카테고리별, 최신순/추천순 필터 제공  
  <img width="1512" src="https://github.com/user-attachments/assets/b16c92cb-1bad-45db-9fd9-92ae706aa571">

- **뉴스 상세 페이지**  
  기사 '좋아요' 저장, 관련 뉴스 사이드바 제공  
  <img width="1512" src="https://github.com/user-attachments/assets/ab9a2093-bf6f-448f-bec7-d6348053fd15">

- **대시보드**  
  사용자 활동 시각화: 관심 카테고리, 주요 키워드, 주간 기사 수, 좋아요한 뉴스 등  
  <img width="1206" src="https://github.com/user-attachments/assets/12b5a052-9245-4a51-a094-c709846fecc2">

---

## 실행 가이드

### 1. 필수 프로그램 설치

- [Node.js](https://nodejs.org/) 설치
- 개발 IDE로는 [VSCode](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) 추천

---

### 2. npm 설치

```bash
npm install
```

---

### 3. 환경 변수 파일 설정

`.env` 파일을 루트 디렉토리에 생성 후 다음 내용 입력

```env
VITE_BASE_URL='http://localhost:8000'
```

> 실제 API 서버 주소에 맞춰 변경 가능(백엔드 서버 주소와 포트 맞춰야 함)

---

### 4. 개발 서버 실행

```bash
npm run dev
```

- 기본 실행 주소: [http://localhost:3000](http://localhost:3000)
- WSL2 환경에서는 `0.0.0.0` 바인딩을 통해 외부 접속 허용됨

---

### 5. 프로덕션 빌드

```bash
npm run build
```

- `dist/` 폴더에 정적 파일 생성됨

---

## 프로젝트 구조 예시

```
ssafy-custom-news-frontend/
├── public/
├── src/
│   ├── assets/
│   ├── components/
│   ├── views/
│   ├── router/
│   └── store/
├── .env
├── package.json
└── vite.config.js
```

---