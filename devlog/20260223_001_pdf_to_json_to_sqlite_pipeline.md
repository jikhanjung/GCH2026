# Work Log: PDF → JSON → SQLite 데이터 입력 파이프라인

> 기반 계획: `20260223_P01_pdf_to_json_to_sqlite_pipeline.md`

## 구현 결과

계획대로 2단계 파이프라인을 구축하고, 168건의 현장조사 데이터를 DB에 적재 완료.

### 1단계 — PDF → JSON 수동 변환

`heritage_list/data/` 디렉토리에 JSON 파일 168개 작성.

| 지역코드 | 지역명 | 파일 수 |
|----------|--------|---------|
| BS | 부산 | 1 |
| CB | 충북 | 7 |
| CN | 충남 | 7 |
| GB | 경북 | 33 |
| GG | 경기 | 1 |
| GN | 경남 | 32 |
| GW | 강원 | 12 |
| JB | 전북 | 13 |
| JJ | 제주 | 25 |
| JN | 전남 | 29 |
| US | 울산 | 8 |

### 2단계 — JSON → SQLite 입력 스크립트 (`import_heritage.py`)

계획서의 스크립트 구조를 그대로 구현:

- `parse_dms(dms_str) -> float` — DMS 문자열(`34°44′19.18″N`)을 십진수 좌표로 변환
- `validate_type_codes(cursor, types) -> list` — COMMON_CODE 테이블 존재 여부 검증, 미존재 코드 목록 반환
- `insert_heritage(cursor, data)` — GEOLOGICAL_CULTURAL_HERITAGE INSERT (types 배열에서 TY1~TY3 자동 매핑)
- `insert_cave(cursor, survey_no, cave)` — GEOLOGICAL_CULTURAL_CAVE INSERT (cave 필드가 있을 때만)
- `insert_references(cursor, survey_no, refs)` — REFERENCE_MATERIAL INSERT
- `import_json(db_path, json_path, update)` — 단일 JSON 파일 처리 (중복 체크, `--update` 옵션 시 DELETE 후 재삽입)
- `main()` — CLI 인자 파싱, 파일/디렉토리 대응, 결과 집계 출력

#### CLI 사용법
```bash
# 단일 파일
python import_heritage.py ghc2026.db heritage_list/data/GN007.json

# 디렉토리 전체
python import_heritage.py ghc2026.db heritage_list/data/

# 기존 레코드 덮어쓰기
python import_heritage.py ghc2026.db heritage_list/data/ --update
```

## 적재 결과

| 테이블 | 건수 |
|--------|------|
| GEOLOGICAL_CULTURAL_HERITAGE | 168 |
| GEOLOGICAL_CULTURAL_CAVE | 29 |
| REFERENCE_MATERIAL | 1,187 |
| COMMON_CODE (기존) | 42 |

### 유형별 분포

| 대분류 | 중분류 | 코드 | 건수 |
|--------|--------|------|------|
| 지질(G) | 구조 | Gc001~Gc005 | 68 |
| | 층서 | Gb001 | 6 |
| | 암석 | Ga001~Ga003 | 6 |
| 화석(F) | 생흔 | Fd001 | 25 |
| | 무척추동물 | Fb001~Fb002 | 6 |
| | 식물 | Fc001~Fc002 | 5 |
| | 미화석 | Fe001 | 1 |
| 지형(L) | 동굴 | La001~La003 | 29 |
| | 자연지형 | Lb001~Lb004 | 21 |
| 자연현상(N) | 물/지하수 | Nb001 | 1 |

## 생성/수정 파일

| 파일 | 작업 |
|------|------|
| `heritage_list/data/*.json` (168개) | 새로 생성 — 현장조사표 JSON 변환 |
| `import_heritage.py` | 새로 생성 — JSON → SQLite 입력 스크립트 |
| `ghc2026.db` | 갱신 — 168건 + 동굴 29건 + 참고문헌 1,187건 적재 |

## 검증

```bash
sqlite3 ghc2026.db "SELECT COUNT(*) FROM GEOLOGICAL_CULTURAL_HERITAGE;"
# → 168

sqlite3 ghc2026.db "SELECT COUNT(*) FROM GEOLOGICAL_CULTURAL_CAVE;"
# → 29

sqlite3 ghc2026.db "SELECT COUNT(*) FROM REFERENCE_MATERIAL;"
# → 1187
```

## 비고

- 계획서 대비 변경 사항 없음. JSON 스키마, 스크립트 구조, CLI 인터페이스 모두 계획대로 구현.
- 초기 샘플 2건(GN007, CB007)으로 검증 후, 나머지 166건을 추가 작성하여 전체 168건 적재 완료.
- `--update` 옵션은 기존 레코드를 CASCADE DELETE 후 재삽입하는 방식으로 동작.
