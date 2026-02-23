# Plan: PDF → JSON → SQLite 데이터 입력 파이프라인

## Context
heritage_list 폴더의 PDF 현장조사표 데이터를 DB에 넣기 위한 2단계 파이프라인을 구축한다.
- 1단계: PDF 데이터를 수동으로 JSON 파일로 작성
- 2단계: Python 스크립트가 JSON을 읽어 SQLite DB에 INSERT

## 파일 구조

```
heritage_list/
  data/
    GN007.json          # 2022 일반 지질유산 샘플
    CB007.json          # 2024 동굴 샘플
import_heritage.py      # JSON → SQLite 입력 스크립트
```

## 1. JSON 스키마 설계

### 일반 지질유산 (GN007.json)
```json
{
  "survey_no": "GN007",
  "gch_nm": "거제 갈곶리 중생대 새, 익룡발자국 화석산지",
  "survey_nm": "권창우, 김현철, 이태호",
  "psitn": "한국지질자원연구원",
  "cttpc": null,
  "area_nm": "경남권",
  "geolgc_map_nm": "율포",
  "strk_sdp": "N30E/10SE",
  "types": [
    {"code": "Fd001", "des": "화석(생흔화석_생흔작용)"},
    {"code": "Gc001", "des": "지질(구조_퇴적작용)"}
  ],
  "geolgc_age": "중생대 백악기",
  "rrstv_rck": "사암, 이암, 응회질퇴적암(경상누층군 성포리층)",
  "address": "경상남도 거제시 남부면 갈곶리 산14-47",
  "lat_dms": "34°44′19.18″N",
  "lon_dms": "128°39′30.18″E",
  "cclt_scl": "정밀발굴조사지역: 10,971㎡, 표본조사지역: 13,070㎡, 참관조사지역: 8,155㎡ (총면적: 32,196㎡)",
  "rkfr_des": "이 화석산지는 거제시 해금강 신선대 서편에 위치하고 있음...",
  "cave": null,
  "references": [
    {"group_gbn": "3", "ordr": "1", "material_nm": "원종관 외, 1980, 한국지질도...", "pge": null},
    {"group_gbn": "4", "ordr": "1", "material_nm": "거제관광문화(http://tour.geoje.go.kr)", "pge": null},
    {"group_gbn": "기존자료", "ordr": "1", "material_nm": "한국의 지질다양성(문화재청, 2011, 2012, 2013)", "pge": "36-47"}
  ]
}
```

### 동굴 지질유산 (CB007.json) — cave 필드 추가
```json
{
  "survey_no": "CB007",
  "...(공통 필드 동일)...": "",
  "cave": {
    "ent_size": "3.0m × 2.5m(타원형)",
    "length": "약 20m",
    "type": "경사",
    "ent_dir": "북동(NE)",
    "direction": "북동(NE)",
    "ungrd_water": "유",
    "ent_water": "무",
    "access": "금성면 성내리 111-12의 절개지 하부에 위치",
    "unkn_topo_des": null,
    "unkn_topo_rank": null,
    "prodt_des": "종유관, 종유석, 석순, 석주, 베이컨시트, 유석, 휴석(소), 동굴산호",
    "prodt_rank": "라",
    "bio_des": null,
    "bio_rank": null,
    "prs_protect": "무",
    "protect": "설치(공사기간 중 설치 예정)",
    "prsv_rank": "매우 양호",
    "eval_des": "층리방향의 수직적으로 발달한 절리...",
    "eval_rank": "라"
  },
  "references": [...]
}
```

## 2. Python 스크립트 (`import_heritage.py`)

### 주요 기능:
1. **DMS→DD 변환**: `34°44′19.18″N` → `34.738661`
2. **유형코드 검증**: `types[].code`가 COMMON_CODE에 존재하는지 확인
3. **INSERT 순서**: GEOLOGICAL_CULTURAL_HERITAGE → GEOLOGICAL_CULTURAL_CAVE → REFERENCE_MATERIAL
4. **중복 방지**: SURVEY_NO 기준 이미 존재하면 스킵 또는 업데이트 옵션

### CLI 사용법:
```bash
# 단일 JSON 파일 입력
python import_heritage.py ghc2026.db heritage_list/data/GN007.json

# 폴더 내 모든 JSON 파일 입력
python import_heritage.py ghc2026.db heritage_list/data/
```

### 스크립트 구조:
- `parse_dms(dms_str) -> float`: DMS 문자열을 십진수로 변환
- `validate_type_code(cursor, code) -> bool`: COMMON_CODE 존재 여부 확인
- `insert_heritage(cursor, data)`: GEOLOGICAL_CULTURAL_HERITAGE INSERT
- `insert_cave(cursor, data)`: GEOLOGICAL_CULTURAL_CAVE INSERT (cave가 있을 때만)
- `insert_references(cursor, survey_no, refs)`: REFERENCE_MATERIAL INSERT
- `main()`: 인자 파싱, JSON 로드, DB 연결, 트랜잭션 처리

## 3. 수정/생성 파일 목록

| 파일 | 작업 |
|---|---|
| `heritage_list/data/GN007.json` | 새로 생성 — 2022 일반 지질유산 샘플 |
| `heritage_list/data/CB007.json` | 새로 생성 — 2024 동굴 샘플 |
| `import_heritage.py` | 새로 생성 — JSON → SQLite 입력 스크립트 |

## 4. 검증 방법

```bash
# 스크립트 실행
python import_heritage.py ghc2026.db heritage_list/data/

# 데이터 확인
sqlite3 ghc2026.db "SELECT SURVEY_NO, GCH_NM, LAT, LON FROM GEOLOGICAL_CULTURAL_HERITAGE;"
sqlite3 ghc2026.db "SELECT * FROM GEOLOGICAL_CULTURAL_CAVE;"
sqlite3 ghc2026.db "SELECT SURVEY_NO, GROUP_GBN, MATERIAL_NM FROM REFERENCE_MATERIAL;"
```
