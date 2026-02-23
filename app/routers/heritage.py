import math
import sqlite3
from fastapi import APIRouter, Depends, Request, Query, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.database import get_db

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

PAGE_SIZE = 20


def _get_codes(db):
    """분류코드 전체 목록 (폼 드롭다운용)"""
    return db.execute(
        "SELECT CODE, CODE_NM, TOP_CD, TOP_CD_NM, MID_CD, MID_CD_NM FROM COMMON_CODE ORDER BY CODE"
    ).fetchall()


# ─── HTML pages ───


@router.get("/", response_class=HTMLResponse)
def index(
    request: Request,
    q: str = "",
    ty: str = "",
    page: int = Query(1, ge=1),
    db: sqlite3.Connection = Depends(get_db),
):
    conditions = []
    params = []

    if q:
        conditions.append("(h.GCH_NM LIKE ? OR h.ADDRESS LIKE ?)")
        params.extend([f"%{q}%", f"%{q}%"])
    if ty:
        conditions.append("c1.TOP_CD = ?")
        params.append(ty)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    count_sql = f"""
        SELECT COUNT(*) FROM GEOLOGICAL_CULTURAL_HERITAGE h
        LEFT JOIN COMMON_CODE c1 ON h.TY1_CD = c1.CODE
        {where}
    """
    total = db.execute(count_sql, params).fetchone()[0]
    total_pages = max(1, math.ceil(total / PAGE_SIZE))
    page = min(page, total_pages)

    list_sql = f"""
        SELECT h.SURVEY_NO, h.GCH_NM, h.TY1_DES, h.ADDRESS, h.GEOLGC_AGE,
               c1.TOP_CD_NM AS ty1_top_nm
        FROM GEOLOGICAL_CULTURAL_HERITAGE h
        LEFT JOIN COMMON_CODE c1 ON h.TY1_CD = c1.CODE
        {where}
        ORDER BY h.SURVEY_NO
        LIMIT ? OFFSET ?
    """
    rows = db.execute(list_sql, params + [PAGE_SIZE, (page - 1) * PAGE_SIZE]).fetchall()

    top_codes = db.execute(
        "SELECT DISTINCT TOP_CD, TOP_CD_NM FROM COMMON_CODE ORDER BY TOP_CD"
    ).fetchall()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "rows": rows,
            "q": q,
            "ty": ty,
            "page": page,
            "total_pages": total_pages,
            "total": total,
            "top_codes": top_codes,
        },
    )


@router.get("/map", response_class=HTMLResponse)
def map_view(request: Request, db: sqlite3.Connection = Depends(get_db)):
    sites = db.execute(
        """SELECT h.SURVEY_NO, h.GCH_NM, h.LAT, h.LON, h.ADDRESS,
                  c1.TOP_CD_NM AS ty1_top_nm
           FROM GEOLOGICAL_CULTURAL_HERITAGE h
           LEFT JOIN COMMON_CODE c1 ON h.TY1_CD = c1.CODE
           WHERE h.LAT IS NOT NULL AND h.LON IS NOT NULL"""
    ).fetchall()
    return templates.TemplateResponse(
        "map.html",
        {"request": request, "sites": [dict(s) for s in sites]},
    )


@router.get("/heritage/new", response_class=HTMLResponse)
def new_form(request: Request, db: sqlite3.Connection = Depends(get_db)):
    return templates.TemplateResponse(
        "form.html",
        {
            "request": request,
            "heritage": None,
            "cave": None,
            "references": [],
            "codes": _get_codes(db),
            "is_new": True,
        },
    )


@router.get("/heritage/{survey_no}", response_class=HTMLResponse)
def detail(
    request: Request,
    survey_no: str,
    db: sqlite3.Connection = Depends(get_db),
):
    heritage = db.execute(
        """
        SELECT h.*,
               c1.CODE_NM AS ty1_nm, c1.TOP_CD_NM AS ty1_top,
               c2.CODE_NM AS ty2_nm, c2.TOP_CD_NM AS ty2_top,
               c3.CODE_NM AS ty3_nm, c3.TOP_CD_NM AS ty3_top
        FROM GEOLOGICAL_CULTURAL_HERITAGE h
        LEFT JOIN COMMON_CODE c1 ON h.TY1_CD = c1.CODE
        LEFT JOIN COMMON_CODE c2 ON h.TY2_CD = c2.CODE
        LEFT JOIN COMMON_CODE c3 ON h.TY3_CD = c3.CODE
        WHERE h.SURVEY_NO = ?
        """,
        [survey_no],
    ).fetchone()

    if not heritage:
        return templates.TemplateResponse(
            "detail.html",
            {"request": request, "heritage": None, "cave": None, "references": []},
            status_code=404,
        )

    cave = db.execute(
        "SELECT * FROM GEOLOGICAL_CULTURAL_CAVE WHERE SURVEY_NO = ?",
        [survey_no],
    ).fetchone()

    references = db.execute(
        "SELECT * FROM REFERENCE_MATERIAL WHERE SURVEY_NO = ? ORDER BY GROUP_GBN, ORDR",
        [survey_no],
    ).fetchall()

    return templates.TemplateResponse(
        "detail.html",
        {
            "request": request,
            "heritage": heritage,
            "cave": cave,
            "references": references,
        },
    )


@router.get("/heritage/{survey_no}/edit", response_class=HTMLResponse)
def edit_form(
    request: Request,
    survey_no: str,
    db: sqlite3.Connection = Depends(get_db),
):
    heritage = db.execute(
        "SELECT * FROM GEOLOGICAL_CULTURAL_HERITAGE WHERE SURVEY_NO = ?",
        [survey_no],
    ).fetchone()

    if not heritage:
        return RedirectResponse("/", status_code=302)

    cave = db.execute(
        "SELECT * FROM GEOLOGICAL_CULTURAL_CAVE WHERE SURVEY_NO = ?",
        [survey_no],
    ).fetchone()

    references = db.execute(
        "SELECT * FROM REFERENCE_MATERIAL WHERE SURVEY_NO = ? ORDER BY GROUP_GBN, ORDR",
        [survey_no],
    ).fetchall()

    return templates.TemplateResponse(
        "form.html",
        {
            "request": request,
            "heritage": heritage,
            "cave": cave,
            "references": references,
            "codes": _get_codes(db),
            "is_new": False,
        },
    )


@router.post("/heritage/save")
def save(
    request: Request,
    db: sqlite3.Connection = Depends(get_db),
    is_new: str = Form(""),
    survey_no: str = Form(""),
    gch_nm: str = Form(""),
    survey_nm: str = Form(""),
    psitn: str = Form(""),
    cttpc: str = Form(""),
    area_nm: str = Form(""),
    geolgc_map_nm: str = Form(""),
    strk_sdp: str = Form(""),
    ty1_cd: str = Form(""),
    ty1_des: str = Form(""),
    ty2_cd: str = Form(""),
    ty2_des: str = Form(""),
    ty3_cd: str = Form(""),
    ty3_des: str = Form(""),
    geolgc_age: str = Form(""),
    rrstv_rck: str = Form(""),
    address: str = Form(""),
    lat: str = Form(""),
    lon: str = Form(""),
    cclt_scl: str = Form(""),
    rkfr_des: str = Form(""),
    # 동굴
    has_cave: str = Form(""),
    cave_ent_size: str = Form(""),
    cave_length: str = Form(""),
    cave_type: str = Form(""),
    cave_ent_dir: str = Form(""),
    cave_direction: str = Form(""),
    cave_ungrd_water: str = Form(""),
    cave_ent_water: str = Form(""),
    cave_access: str = Form(""),
    cave_unkn_topo_des: str = Form(""),
    cave_unkn_topo_rank: str = Form(""),
    cave_prodt_des: str = Form(""),
    cave_prodt_rank: str = Form(""),
    cave_bio_des: str = Form(""),
    cave_bio_rank: str = Form(""),
    cave_prs_protect: str = Form(""),
    cave_protect: str = Form(""),
    cave_prsv_rank: str = Form(""),
    cave_eval_des: str = Form(""),
    cave_eval_rank: str = Form(""),
    # 참고문헌 (동적 행)
    ref_group_gbn: list[str] = Form([]),
    ref_ordr: list[str] = Form([]),
    ref_material_nm: list[str] = Form([]),
    ref_pge: list[str] = Form([]),
):
    survey_no = survey_no.strip()
    if not survey_no:
        return RedirectResponse("/", status_code=302)

    lat_val = float(lat) if lat.strip() else None
    lon_val = float(lon) if lon.strip() else None

    def _or_none(v):
        return v.strip() if v.strip() else None

    if is_new == "1":
        db.execute(
            """INSERT INTO GEOLOGICAL_CULTURAL_HERITAGE
               (SURVEY_NO, GCH_NM, SURVEY_NM, PSITN, CTTPC, AREA_NM,
                GEOLGC_MAP_NM, STRK_SDP, TY1_CD, TY1_DES, TY2_CD, TY2_DES,
                TY3_CD, TY3_DES, GEOLGC_AGE, RRSTV_RCK, ADDRESS, LAT, LON,
                CCLT_SCL, RKFR_DES, CREATE_DT)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,datetime('now'))""",
            [
                survey_no, _or_none(gch_nm), _or_none(survey_nm), _or_none(psitn),
                _or_none(cttpc), _or_none(area_nm), _or_none(geolgc_map_nm),
                _or_none(strk_sdp), _or_none(ty1_cd), _or_none(ty1_des),
                _or_none(ty2_cd), _or_none(ty2_des), _or_none(ty3_cd),
                _or_none(ty3_des), _or_none(geolgc_age), _or_none(rrstv_rck),
                _or_none(address), lat_val, lon_val, _or_none(cclt_scl),
                _or_none(rkfr_des),
            ],
        )
    else:
        db.execute(
            """UPDATE GEOLOGICAL_CULTURAL_HERITAGE SET
               GCH_NM=?, SURVEY_NM=?, PSITN=?, CTTPC=?, AREA_NM=?,
               GEOLGC_MAP_NM=?, STRK_SDP=?, TY1_CD=?, TY1_DES=?, TY2_CD=?,
               TY2_DES=?, TY3_CD=?, TY3_DES=?, GEOLGC_AGE=?, RRSTV_RCK=?,
               ADDRESS=?, LAT=?, LON=?, CCLT_SCL=?, RKFR_DES=?
               WHERE SURVEY_NO=?""",
            [
                _or_none(gch_nm), _or_none(survey_nm), _or_none(psitn),
                _or_none(cttpc), _or_none(area_nm), _or_none(geolgc_map_nm),
                _or_none(strk_sdp), _or_none(ty1_cd), _or_none(ty1_des),
                _or_none(ty2_cd), _or_none(ty2_des), _or_none(ty3_cd),
                _or_none(ty3_des), _or_none(geolgc_age), _or_none(rrstv_rck),
                _or_none(address), lat_val, lon_val, _or_none(cclt_scl),
                _or_none(rkfr_des), survey_no,
            ],
        )

    # 동굴 정보
    existing_cave = db.execute(
        "SELECT 1 FROM GEOLOGICAL_CULTURAL_CAVE WHERE SURVEY_NO = ?", [survey_no]
    ).fetchone()

    if has_cave == "1":
        cave_params = [
            _or_none(cave_ent_size), _or_none(cave_length), _or_none(cave_type),
            _or_none(cave_ent_dir), _or_none(cave_direction),
            _or_none(cave_ungrd_water), _or_none(cave_ent_water),
            _or_none(cave_access), _or_none(cave_unkn_topo_des),
            _or_none(cave_unkn_topo_rank), _or_none(cave_prodt_des),
            _or_none(cave_prodt_rank), _or_none(cave_bio_des),
            _or_none(cave_bio_rank), _or_none(cave_prs_protect),
            _or_none(cave_protect), _or_none(cave_prsv_rank),
            _or_none(cave_eval_des), _or_none(cave_eval_rank),
        ]
        if existing_cave:
            db.execute(
                """UPDATE GEOLOGICAL_CULTURAL_CAVE SET
                   ENT_SIZE=?, LENGTH=?, TYPE=?, ENT_DIR=?, DIRECTION=?,
                   UNGRD_WATER=?, ENT_WATER=?, ACCESS=?, UNKN_TOPO_DES=?,
                   UNKN_TOPO_RANK=?, PRODT_DES=?, PRODT_RANK=?, BIO_DES=?,
                   BIO_RANK=?, PRS_PROTECT=?, PROTECT=?, PRSV_RANK=?,
                   EVAL_DES=?, EVAL_RANK=?
                   WHERE SURVEY_NO=?""",
                cave_params + [survey_no],
            )
        else:
            db.execute(
                """INSERT INTO GEOLOGICAL_CULTURAL_CAVE
                   (SURVEY_NO, ENT_SIZE, LENGTH, TYPE, ENT_DIR, DIRECTION,
                    UNGRD_WATER, ENT_WATER, ACCESS, UNKN_TOPO_DES,
                    UNKN_TOPO_RANK, PRODT_DES, PRODT_RANK, BIO_DES,
                    BIO_RANK, PRS_PROTECT, PROTECT, PRSV_RANK,
                    EVAL_DES, EVAL_RANK)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                [survey_no] + cave_params,
            )
    elif existing_cave:
        db.execute("DELETE FROM GEOLOGICAL_CULTURAL_CAVE WHERE SURVEY_NO = ?", [survey_no])

    # 참고문헌: 기존 삭제 후 재입력
    db.execute("DELETE FROM REFERENCE_MATERIAL WHERE SURVEY_NO = ?", [survey_no])
    for i in range(len(ref_material_nm)):
        nm = ref_material_nm[i].strip() if i < len(ref_material_nm) else ""
        if not nm:
            continue
        db.execute(
            """INSERT INTO REFERENCE_MATERIAL
               (SURVEY_NO, GROUP_GBN, ORDR, MATERIAL_NM, PGE, CREATE_DT)
               VALUES (?,?,?,?,?,datetime('now'))""",
            [
                survey_no,
                ref_group_gbn[i].strip() if i < len(ref_group_gbn) else None,
                ref_ordr[i].strip() if i < len(ref_ordr) else None,
                nm,
                ref_pge[i].strip() if i < len(ref_pge) and ref_pge[i].strip() else None,
            ],
        )

    db.commit()
    return RedirectResponse(f"/heritage/{survey_no}", status_code=302)


@router.post("/heritage/{survey_no}/delete")
def delete(survey_no: str, db: sqlite3.Connection = Depends(get_db)):
    db.execute("DELETE FROM GEOLOGICAL_CULTURAL_HERITAGE WHERE SURVEY_NO = ?", [survey_no])
    db.commit()
    return RedirectResponse("/", status_code=302)


# ─── JSON API ───


@router.get("/api/heritage")
def api_list(
    q: str = "",
    ty: str = "",
    page: int = Query(1, ge=1),
    db: sqlite3.Connection = Depends(get_db),
):
    conditions = []
    params = []

    if q:
        conditions.append("(GCH_NM LIKE ? OR ADDRESS LIKE ?)")
        params.extend([f"%{q}%", f"%{q}%"])
    if ty:
        conditions.append("TY1_CD IN (SELECT CODE FROM COMMON_CODE WHERE TOP_CD = ?)")
        params.append(ty)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    total = db.execute(
        f"SELECT COUNT(*) FROM GEOLOGICAL_CULTURAL_HERITAGE {where}", params
    ).fetchone()[0]

    rows = db.execute(
        f"""SELECT SURVEY_NO, GCH_NM, TY1_DES, ADDRESS, GEOLGC_AGE, LAT, LON
            FROM GEOLOGICAL_CULTURAL_HERITAGE {where}
            ORDER BY SURVEY_NO LIMIT ? OFFSET ?""",
        params + [PAGE_SIZE, (page - 1) * PAGE_SIZE],
    ).fetchall()

    return {
        "total": total,
        "page": page,
        "page_size": PAGE_SIZE,
        "items": [dict(r) for r in rows],
    }


@router.get("/api/heritage/{survey_no}")
def api_detail(survey_no: str, db: sqlite3.Connection = Depends(get_db)):
    heritage = db.execute(
        "SELECT * FROM GEOLOGICAL_CULTURAL_HERITAGE WHERE SURVEY_NO = ?",
        [survey_no],
    ).fetchone()

    if not heritage:
        return {"error": "not found"}

    cave = db.execute(
        "SELECT * FROM GEOLOGICAL_CULTURAL_CAVE WHERE SURVEY_NO = ?",
        [survey_no],
    ).fetchone()

    references = db.execute(
        "SELECT * FROM REFERENCE_MATERIAL WHERE SURVEY_NO = ? ORDER BY GROUP_GBN, ORDR",
        [survey_no],
    ).fetchall()

    return {
        "heritage": dict(heritage),
        "cave": dict(cave) if cave else None,
        "references": [dict(r) for r in references],
    }
