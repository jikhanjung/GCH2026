# Handoff — Current Project State

> Last updated: 2026-02-23

## What Has Been Built

### 1. SQLite Database (`ghc2026.db`)
- Schema defined in `sql/geological_heritage_sqlite_schema.sql` (5 tables)
- Classification codes loaded from `sql/common_code.sql` (37 codes across 4 top categories)
- 2 sample records imported: GN007 (fossil site), CB007 (cave)

### 2. JSON Import Pipeline (`import_heritage.py`)
- Converts hand-written JSON files in `heritage_list/data/` into DB records
- Handles DMS→DD coordinate conversion, type code validation, cave data, references
- Plan documented in `devlog/20260223_P01_pdf_to_json_to_sqlite_pipeline.md`

### 3. FastAPI Web Application (`app/`)
- **Stack**: FastAPI + Jinja2 (server-side rendering) + Bootstrap 5.3 CDN + Leaflet 1.9.4
- **CRUD complete**: list, detail, create, edit, delete for heritage records
- Includes cave data toggle and dynamic reference rows on the form
- **Map views**: detail page shows individual site on OSM map; dedicated map page shows all sites
- JSON API endpoints at `/api/heritage` and `/api/heritage/{survey_no}`
- Plans & logs in `devlog/20260223_P02_fastapi_bootstrap_webapp.md`, `devlog/20260223_002_webapp_crud_implementation.md`

#### Routes
| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Heritage list (search, filter by type, pagination) |
| GET | `/map` | Full map with all sites (Leaflet + OSM) |
| GET | `/heritage/new` | New record form |
| GET | `/heritage/{survey_no}` | Record detail view (includes individual map) |
| GET | `/heritage/{survey_no}/edit` | Edit form |
| POST | `/heritage/save` | Create or update record |
| POST | `/heritage/{survey_no}/delete` | Delete record (cascades) |
| GET | `/api/heritage` | List JSON API |
| GET | `/api/heritage/{survey_no}` | Detail JSON API |

#### How to Run
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
# http://127.0.0.1:8000
```

## Project Structure
```
GHC2026/
├── app/
│   ├── main.py                 # FastAPI entry point
│   ├── database.py             # SQLite connection (get_db dependency)
│   ├── routers/
│   │   └── heritage.py         # All routes (HTML + JSON API)
│   ├── templates/
│   │   ├── base.html           # Bootstrap layout (navbar, footer)
│   │   ├── index.html          # List page
│   │   ├── detail.html         # Detail page (with individual Leaflet map)
│   │   ├── form.html           # Create/edit form
│   │   └── map.html            # Full map page (all sites)
│   └── static/
│       └── style.css
├── sql/
│   ├── geological_heritage_sqlite_schema.sql
│   └── common_code.sql
├── heritage_list/              # Source PDFs + JSON data files
├── devlog/                     # Development plans & logs
├── docs/
│   └── HANDOFF.md              # ← This file
├── import_heritage.py          # JSON → SQLite import script
├── ghc2026.db                  # SQLite database
├── requirements.txt            # Python dependencies (fastapi, uvicorn, jinja2, python-multipart)
└── CLAUDE.md                   # AI assistant instructions
```

## What Is NOT Done Yet
- Image upload/display (CHT_IMAG_DM table exists but no UI)
- Bulk data entry from remaining PDF survey lists (2022-2024)
- User authentication / access control
- Deployment configuration (Docker, etc.)
