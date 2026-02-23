# Plan: FastAPI + Bootstrap 지질유산 웹 애플리케이션

## Context
SQLite DB(ghc2026.db)에 저장된 지질문화유산 데이터를 조회·관리할 수 있는 웹 애플리케이션을 구축한다.
- Backend: FastAPI + Jinja2 (서버사이드 렌더링)
- Frontend: Bootstrap 5 (CDN)
- DB: 기존 SQLite (aiosqlite 사용하지 않고, 동기 sqlite3 사용)

## 파일 구조

```
app/
  main.py              # FastAPI 앱 엔트리포인트
  database.py          # SQLite 연결 관리
  routers/
    heritage.py        # 지질유산 CRUD 라우터
  templates/
    base.html          # Bootstrap 레이아웃 (navbar, footer)
    index.html         # 메인 페이지 — 유산 목록 (검색/필터/페이징)
    detail.html        # 유산 상세 보기 (동굴정보, 참고문헌 포함)
  static/
    style.css          # 커스텀 스타일 (최소한)
requirements.txt       # fastapi, uvicorn, jinja2
```

## 1. 핵심 기능

### 1-1. 유산 목록 (GET /)
- GEOLOGICAL_CULTURAL_HERITAGE 테이블의 전체 목록을 Bootstrap 테이블로 표시
- 표시 컬럼: SURVEY_NO, GCH_NM, TY1_DES, ADDRESS, GEOLGC_AGE
- 검색: GCH_NM 또는 ADDRESS 키워드 검색 (LIKE)
- 분류 필터: TOP_CD (지질/지형/화석/자연현상) 드롭다운
- 페이징: 한 페이지 20건

### 1-2. 유산 상세 (GET /heritage/{survey_no})
- 기본정보: 모든 필드 표시
- 분류코드: TY1~TY3 코드명 JOIN 표시
- 동굴정보: GEOLOGICAL_CULTURAL_CAVE 데이터 (있는 경우만)
- 참고문헌: REFERENCE_MATERIAL 목록
- 위치: LAT/LON 표시

### 1-3. API 엔드포인트 (JSON)
- GET /api/heritage — 목록 JSON (향후 확장용)
- GET /api/heritage/{survey_no} — 상세 JSON

## 2. 기술 상세

### database.py
- `get_db()` 함수: sqlite3.connect로 ghc2026.db 연결, Row factory 설정
- `PRAGMA foreign_keys = ON` 설정
- FastAPI dependency로 사용

### routers/heritage.py
- 목록 쿼리: LEFT JOIN COMMON_CODE로 분류명 가져오기
- 상세 쿼리: heritage + cave(LEFT JOIN) + references(별도 쿼리)
- 검색/필터 파라미터: `q` (키워드), `ty` (분류 TOP_CD), `page` (페이지)

### templates/base.html
- Bootstrap 5.3 CDN
- 한글 폰트 (Pretendard 또는 시스템 폰트)
- Navbar: 사이트명 "지질유산 DB", 메뉴 링크
- Footer: 간단한 저작권 표시

## 3. 수정/생성 파일 목록

| 파일 | 작업 |
|---|---|
| `requirements.txt` | 새로 생성 — 의존성 |
| `app/main.py` | 새로 생성 — FastAPI 앱 |
| `app/database.py` | 새로 생성 — DB 연결 |
| `app/routers/heritage.py` | 새로 생성 — 라우터 |
| `app/templates/base.html` | 새로 생성 — 기본 레이아웃 |
| `app/templates/index.html` | 새로 생성 — 목록 페이지 |
| `app/templates/detail.html` | 새로 생성 — 상세 페이지 |
| `app/static/style.css` | 새로 생성 — 커스텀 스타일 |

## 4. 실행 방법

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
# http://127.0.0.1:8000 에서 확인
```
