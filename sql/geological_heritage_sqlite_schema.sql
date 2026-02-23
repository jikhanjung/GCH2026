
PRAGMA foreign_keys = ON;

-- ============================================
-- COMMON_CODE
-- ============================================
CREATE TABLE COMMON_CODE (
    CODE_SN     INTEGER PRIMARY KEY AUTOINCREMENT,
    CODE        TEXT,
    CODE_NM     TEXT,
    TOP_CD      TEXT,
    TOP_CD_NM   TEXT,
    MID_CD      TEXT,
    MID_CD_NM   TEXT,
    BOT_CD      TEXT,
    BOT_CD_NM   TEXT,
    UPPER_CD    TEXT,
    RGSDE       TEXT
);

CREATE UNIQUE INDEX UX_COMMON_CODE_CODE ON COMMON_CODE(CODE);


-- ============================================
-- GEOLOGICAL_CULTURAL_HERITAGE
-- ============================================
CREATE TABLE GEOLOGICAL_CULTURAL_HERITAGE (
    SURVEY_NO       TEXT PRIMARY KEY,
    SURVEY_YEAR     INTEGER,

    GCH_NM          TEXT,
    SURVEY_NM       TEXT,
    PSITN           TEXT,
    CTTPC           TEXT,
    AREA_NM         TEXT,
    GEOLGC_MAP_NM   TEXT,
    STRK_SDP        TEXT,

    TY1_CD          TEXT,
    TY1_DES         TEXT,
    TY2_CD          TEXT,
    TY2_DES         TEXT,
    TY3_CD          TEXT,
    TY3_DES         TEXT,

    GEOLGC_AGE      TEXT,
    RRSTV_RCK       TEXT,
    ADDRESS         TEXT,

    LAT             REAL,
    LON             REAL,

    CCLT_SCL        TEXT,
    RKFR_DES        TEXT,

    CREATE_DT       TEXT,
    CREATOR_ID      TEXT,

    FOREIGN KEY (TY1_CD) REFERENCES COMMON_CODE(CODE),
    FOREIGN KEY (TY2_CD) REFERENCES COMMON_CODE(CODE),
    FOREIGN KEY (TY3_CD) REFERENCES COMMON_CODE(CODE)
);

CREATE INDEX IDX_GEO_TY1 ON GEOLOGICAL_CULTURAL_HERITAGE(TY1_CD);
CREATE INDEX IDX_GEO_TY2 ON GEOLOGICAL_CULTURAL_HERITAGE(TY2_CD);
CREATE INDEX IDX_GEO_TY3 ON GEOLOGICAL_CULTURAL_HERITAGE(TY3_CD);


-- ============================================
-- CHT_IMAG_DM
-- ============================================
CREATE TABLE CHT_IMAG_DM (
    FILE_SN     INTEGER PRIMARY KEY AUTOINCREMENT,

    REF_SEID    TEXT NOT NULL,
    SUB_NO      TEXT,
    SAVE_PT     TEXT,
    SFILE_NM    TEXT,
    OFILE_NM    TEXT,
    FILE_SZ     TEXT,

    CREATE_DT   TEXT,
    CREATOR_ID  TEXT,
    REMARK      TEXT,

    FOREIGN KEY (REF_SEID)
        REFERENCES GEOLOGICAL_CULTURAL_HERITAGE(SURVEY_NO)
        ON DELETE CASCADE
);

CREATE INDEX IDX_IMAG_SURVEY ON CHT_IMAG_DM(REF_SEID);


-- ============================================
-- GEOLOGICAL_CULTURAL_CAVE
-- ============================================
CREATE TABLE GEOLOGICAL_CULTURAL_CAVE (
    SURVEY_NO        TEXT PRIMARY KEY,

    ENT_SIZE         TEXT,
    LENGTH           TEXT,
    TYPE             TEXT,
    ENT_DIR          TEXT,
    DIRECTION        TEXT,
    UNGRD_WATER      TEXT,
    ENT_WATER        TEXT,
    ACCESS           TEXT,

    UNKN_TOPO_DES    TEXT,
    UNKN_TOPO_RANK   TEXT,

    PRODT_DES        TEXT,
    PRODT_RANK       TEXT,

    BIO_DES          TEXT,
    BIO_RANK         TEXT,

    PRS_PROTECT      TEXT,
    PROTECT          TEXT,
    PRSV_RANK        TEXT,

    EVAL_DES         TEXT,
    EVAL_RANK        TEXT,

    FOREIGN KEY (SURVEY_NO)
        REFERENCES GEOLOGICAL_CULTURAL_HERITAGE(SURVEY_NO)
        ON DELETE CASCADE
);


-- ============================================
-- REFERENCE_MATERIAL
-- ============================================
CREATE TABLE REFERENCE_MATERIAL (
    MATERIAL_SN  INTEGER PRIMARY KEY AUTOINCREMENT,

    SURVEY_NO    TEXT NOT NULL,
    GROUP_GBN    TEXT,
    ORDR         TEXT,
    MATERIAL_NM  TEXT,
    PGE          TEXT,

    CREATE_DT    TEXT,
    CREATOR_ID   TEXT,

    FOREIGN KEY (SURVEY_NO)
        REFERENCES GEOLOGICAL_CULTURAL_HERITAGE(SURVEY_NO)
        ON DELETE CASCADE
);

CREATE INDEX IDX_REF_SURVEY ON REFERENCE_MATERIAL(SURVEY_NO);
