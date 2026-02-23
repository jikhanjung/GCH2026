# Work Log: FastAPI + Bootstrap 웹앱 구현

> 기반 계획: `devlog/20260223_P02_fastapi_bootstrap_webapp.md`

## 1차 — 조회 기능 구현

P02 계획대로 목록/상세/JSON API를 구현했다.

### 생성한 파일
| 파일 | 설명 |
|---|---|
| `requirements.txt` | fastapi, uvicorn[standard], jinja2 |
| `app/__init__.py` | 패키지 init |
| `app/main.py` | FastAPI 앱, static mount, router 등록 |
| `app/database.py` | sqlite3 연결, Row factory, FK 활성화 |
| `app/routers/__init__.py` | 패키지 init |
| `app/routers/heritage.py` | 목록/상세 HTML + JSON API 라우터 |
| `app/templates/base.html` | Bootstrap 5.3 CDN 레이아웃 |
| `app/templates/index.html` | 목록 (검색, 분류필터, 페이징) |
| `app/templates/detail.html` | 상세 (기본정보, 분류, 동굴, 참고문헌) |
| `app/static/style.css` | 최소 커스텀 스타일 |

### 검증
- uvicorn 정상 기동 확인
- `/api/heritage` — GN007, CB007 두 건 JSON 응답 확인
- `/` — HTML 테이블 렌더링 확인
- `/heritage/GN007` — 상세 페이지 제목 렌더링 확인

---

## 2차 — CRUD (등록/수정/삭제) 추가

### 추가한 엔드포인트
| Method | Path | 설명 |
|--------|------|------|
| GET | `/heritage/new` | 새 유산 등록 폼 |
| GET | `/heritage/{survey_no}/edit` | 기존 유산 수정 폼 |
| POST | `/heritage/save` | 생성/수정 처리 (is_new 플래그로 분기) |
| POST | `/heritage/{survey_no}/delete` | 삭제 (confirm 다이얼로그) |

### 새로 생성한 파일
| 파일 | 설명 |
|---|---|
| `app/templates/form.html` | 등록/수정 공용 폼 |

### 수정한 파일
| 파일 | 변경 내용 |
|---|---|
| `app/routers/heritage.py` | save/delete 엔드포인트, `_get_codes()` 헬퍼 추가 |
| `app/templates/index.html` | "새로 등록" 버튼 추가 |
| `app/templates/detail.html` | "수정" / "삭제" 버튼 추가 |
| `requirements.txt` | `python-multipart` 의존성 추가 |

### 폼 상세
- 기본정보 전 필드 편집
- 분류코드: COMMON_CODE 전체를 `<select>` 드롭다운으로 제공
- 동굴정보: 토글 스위치로 on/off — 해제 시 기존 동굴 레코드 DELETE
- 참고문헌: JavaScript로 행 동적 추가/삭제, 저장 시 전체 삭제 후 재입력
- 삭제: `confirm()` 다이얼로그 후 POST

### 검증
- `GET /heritage/new` — 폼 정상 렌더링
- `POST /heritage/save` (is_new=1) — 302 redirect, 레코드 생성 확인
- `GET /heritage/GN007/edit` — 기존 데이터 폼에 로드 확인
- `GET /heritage/CB007/edit` — 동굴 체크박스 checked, 동굴 데이터 로드 확인
- `POST /heritage/TEST01/delete` — 302 redirect, API에서 not found 확인
