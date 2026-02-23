#!/usr/bin/env python3
"""JSON → SQLite import script for geological cultural heritage data."""

import json
import re
import sqlite3
import sys
from pathlib import Path


def parse_dms(dms_str):
    """Convert DMS string like '34°44′19.18″N' to decimal degrees."""
    if not dms_str:
        return None
    m = re.match(
        r"(\d+)[°]\s*(\d+)[′']\s*([\d.]+)[″\"]\s*([NSEWnsew])", dms_str
    )
    if not m:
        raise ValueError(f"Cannot parse DMS: {dms_str}")
    deg, minutes, sec, direction = (
        int(m.group(1)),
        int(m.group(2)),
        float(m.group(3)),
        m.group(4).upper(),
    )
    dd = deg + minutes / 60 + sec / 3600
    if direction in ("S", "W"):
        dd = -dd
    return round(dd, 6)


def validate_type_codes(cursor, types):
    """Validate that all type codes exist in COMMON_CODE. Returns list of missing codes."""
    missing = []
    for t in types:
        cursor.execute("SELECT 1 FROM COMMON_CODE WHERE CODE = ?", (t["code"],))
        if not cursor.fetchone():
            missing.append(t["code"])
    return missing


def insert_heritage(cursor, data):
    """Insert a record into GEOLOGICAL_CULTURAL_HERITAGE."""
    types = data.get("types", [])
    ty1_cd = types[0]["code"] if len(types) > 0 else None
    ty1_des = types[0]["des"] if len(types) > 0 else None
    ty2_cd = types[1]["code"] if len(types) > 1 else None
    ty2_des = types[1]["des"] if len(types) > 1 else None
    ty3_cd = types[2]["code"] if len(types) > 2 else None
    ty3_des = types[2]["des"] if len(types) > 2 else None

    lat = parse_dms(data.get("lat_dms"))
    lon = parse_dms(data.get("lon_dms"))

    cursor.execute(
        """INSERT INTO GEOLOGICAL_CULTURAL_HERITAGE
           (SURVEY_NO, SURVEY_YEAR, GCH_NM, SURVEY_NM, PSITN, CTTPC, AREA_NM,
            GEOLGC_MAP_NM, STRK_SDP,
            TY1_CD, TY1_DES, TY2_CD, TY2_DES, TY3_CD, TY3_DES,
            GEOLGC_AGE, RRSTV_RCK, ADDRESS, LAT, LON,
            CCLT_SCL, RKFR_DES, CREATE_DT)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,datetime('now'))""",
        (
            data["survey_no"],
            data.get("survey_year"),
            data.get("gch_nm"),
            data.get("survey_nm"),
            data.get("psitn"),
            data.get("cttpc"),
            data.get("area_nm"),
            data.get("geolgc_map_nm"),
            data.get("strk_sdp"),
            ty1_cd,
            ty1_des,
            ty2_cd,
            ty2_des,
            ty3_cd,
            ty3_des,
            data.get("geolgc_age"),
            data.get("rrstv_rck"),
            data.get("address"),
            lat,
            lon,
            data.get("cclt_scl"),
            data.get("rkfr_des"),
        ),
    )


def insert_cave(cursor, survey_no, cave):
    """Insert a record into GEOLOGICAL_CULTURAL_CAVE."""
    cursor.execute(
        """INSERT INTO GEOLOGICAL_CULTURAL_CAVE
           (SURVEY_NO, ENT_SIZE, LENGTH, TYPE, ENT_DIR, DIRECTION,
            UNGRD_WATER, ENT_WATER, ACCESS,
            UNKN_TOPO_DES, UNKN_TOPO_RANK,
            PRODT_DES, PRODT_RANK,
            BIO_DES, BIO_RANK,
            PRS_PROTECT, PROTECT, PRSV_RANK,
            EVAL_DES, EVAL_RANK)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            survey_no,
            cave.get("ent_size"),
            cave.get("length"),
            cave.get("type"),
            cave.get("ent_dir"),
            cave.get("direction"),
            cave.get("ungrd_water"),
            cave.get("ent_water"),
            cave.get("access"),
            cave.get("unkn_topo_des"),
            cave.get("unkn_topo_rank"),
            cave.get("prodt_des"),
            cave.get("prodt_rank"),
            cave.get("bio_des"),
            cave.get("bio_rank"),
            cave.get("prs_protect"),
            cave.get("protect"),
            cave.get("prsv_rank"),
            cave.get("eval_des"),
            cave.get("eval_rank"),
        ),
    )


def insert_references(cursor, survey_no, refs):
    """Insert records into REFERENCE_MATERIAL."""
    for ref in refs:
        cursor.execute(
            """INSERT INTO REFERENCE_MATERIAL
               (SURVEY_NO, GROUP_GBN, ORDR, MATERIAL_NM, PGE, CREATE_DT)
               VALUES (?,?,?,?,?,datetime('now'))""",
            (
                survey_no,
                ref.get("group_gbn"),
                ref.get("ordr"),
                ref.get("material_nm"),
                ref.get("pge"),
            ),
        )


def import_json(db_path, json_path, update=False):
    """Import a single JSON file into the database."""
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    survey_no = data["survey_no"]
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    try:
        # Check for duplicate
        cursor.execute(
            "SELECT 1 FROM GEOLOGICAL_CULTURAL_HERITAGE WHERE SURVEY_NO = ?",
            (survey_no,),
        )
        exists = cursor.fetchone()

        if exists and not update:
            print(f"  SKIP {survey_no}: already exists (use --update to overwrite)")
            conn.close()
            return False

        if exists and update:
            # Delete existing record (cascades to cave and references)
            cursor.execute(
                "DELETE FROM GEOLOGICAL_CULTURAL_HERITAGE WHERE SURVEY_NO = ?",
                (survey_no,),
            )
            print(f"  UPDATE {survey_no}: deleting existing record for re-insert")

        # Validate type codes
        types = data.get("types", [])
        missing = validate_type_codes(cursor, types)
        if missing:
            print(f"  ERROR {survey_no}: unknown type codes: {missing}")
            conn.close()
            return False

        # Insert heritage record
        insert_heritage(cursor, data)

        # Insert cave data if present
        cave = data.get("cave")
        if cave:
            insert_cave(cursor, survey_no, cave)

        # Insert references
        refs = data.get("references", [])
        if refs:
            insert_references(cursor, survey_no, refs)

        conn.commit()
        cave_mark = " +cave" if cave else ""
        print(f"  OK {survey_no}: {data.get('gch_nm')}{cave_mark}, {len(refs)} refs")
        return True

    except Exception as e:
        conn.rollback()
        print(f"  ERROR {survey_no}: {e}")
        return False
    finally:
        conn.close()


def main():
    if len(sys.argv) < 3:
        print("Usage: python import_heritage.py <db_path> <json_path_or_dir> [--update]")
        print()
        print("  db_path          Path to SQLite database")
        print("  json_path_or_dir Single JSON file or directory of JSON files")
        print("  --update         Overwrite existing records (default: skip)")
        sys.exit(1)

    db_path = sys.argv[1]
    target = sys.argv[2]
    update = "--update" in sys.argv

    if not Path(db_path).exists():
        print(f"Error: database not found: {db_path}")
        sys.exit(1)

    target_path = Path(target)
    if target_path.is_file():
        json_files = [target_path]
    elif target_path.is_dir():
        json_files = sorted(target_path.glob("*.json"))
        if not json_files:
            print(f"No JSON files found in {target}")
            sys.exit(1)
    else:
        print(f"Error: not found: {target}")
        sys.exit(1)

    print(f"Importing {len(json_files)} file(s) into {db_path}")
    ok, skip_err = 0, 0
    for jf in json_files:
        print(f"  Processing {jf.name}...")
        if import_json(db_path, str(jf), update):
            ok += 1
        else:
            skip_err += 1

    print(f"Done: {ok} imported, {skip_err} skipped/errors")


if __name__ == "__main__":
    main()
