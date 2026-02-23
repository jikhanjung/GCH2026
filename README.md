# GCH2026 — 지질문화유산 분포지도

한국의 지질문화유산(Geological Cultural Heritage) 현장조사 데이터를 관리하는 웹 애플리케이션.

## 주요 기능

- 지질유산 목록 조회 (키워드 검색, 분류 필터, 페이징)
- 상세 보기 (기본정보, 분류코드, 동굴정보, 참고문헌)
- 등록 / 수정 / 삭제
- JSON API (`/api/heritage`, `/api/heritage/{survey_no}`)
- JSON 파일 → SQLite 일괄 입력 (`import_heritage.py`)

## 기술 스택

- **Backend**: Python, FastAPI, Jinja2
- **Frontend**: Bootstrap 5.3 (CDN)
- **Database**: SQLite

## 시작하기

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. DB 초기화 (최초 1회)

```bash
sqlite3 ghc2026.db < sql/geological_heritage_sqlite_schema.sql
sqlite3 ghc2026.db < sql/common_code.sql
```

### 3. 데이터 입력 (선택)

```bash
# 단일 JSON 파일
python import_heritage.py ghc2026.db heritage_list/data/GN007.json

# 폴더 내 전체
python import_heritage.py ghc2026.db heritage_list/data/
```

### 4. 웹 서버 실행

```bash
uvicorn app.main:app --reload
```

http://127.0.0.1:8000 에서 확인.

## DB 구조

| 테이블 | 설명 |
|--------|------|
| `COMMON_CODE` | 3단계 분류코드 (지질/지형/화석/자연현상) |
| `GEOLOGICAL_CULTURAL_HERITAGE` | 유산 조사 기록 (메인 테이블) |
| `GEOLOGICAL_CULTURAL_CAVE` | 동굴 확장 데이터 (1:1) |
| `CHT_IMAG_DM` | 이미지/첨부파일 |
| `REFERENCE_MATERIAL` | 참고문헌 |

스키마 상세: `sql/geological_heritage_sqlite_schema.sql`

## 프로젝트 구조

```
GHC2026/
├── app/
│   ├── main.py                 # FastAPI 엔트리포인트
│   ├── database.py             # SQLite 연결 관리
│   ├── routers/
│   │   └── heritage.py         # HTML + JSON API 라우터
│   ├── templates/              # Jinja2 템플릿
│   └── static/                 # CSS
├── sql/                        # DB 스키마 및 초기 데이터
├── heritage_list/              # 현장조사 PDF 및 JSON 데이터
├── devlog/                     # 개발 계획 및 작업 기록
├── docs/                       # 프로젝트 문서
├── import_heritage.py          # JSON → SQLite 입력 스크립트
├── requirements.txt
└── ghc2026.db                  # SQLite 데이터베이스
```
