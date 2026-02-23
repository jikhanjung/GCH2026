# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GHC2026 is a Korean geological cultural heritage (지질유산) database project. It defines a SQLite schema and reference data for cataloging geological heritage sites, including survey records, classification codes, cave data, images, and reference materials.

## Database Architecture

The database uses SQLite with foreign keys enabled (`PRAGMA foreign_keys = ON`).

### Tables and Relationships

- **COMMON_CODE** — 3-level hierarchical classification codes (TOP_CD → MID_CD → BOT_CD). Unique index on `CODE`.
- **GEOLOGICAL_CULTURAL_HERITAGE** — Main table for heritage survey records, keyed by `SURVEY_NO`. Links to COMMON_CODE via `TY1_CD`, `TY2_CD`, `TY3_CD` (type classifications). Contains location (LAT/LON), geological age, address, and descriptive fields.
- **CHT_IMAG_DM** — Image/file attachments linked to heritage records via `REF_SEID` → `SURVEY_NO`. Cascades on delete.
- **GEOLOGICAL_CULTURAL_CAVE** — Cave-specific extended data, 1:1 with heritage records via shared `SURVEY_NO` primary key. Cascades on delete.
- **REFERENCE_MATERIAL** — Bibliography/references linked to surveys via `SURVEY_NO`. Cascades on delete.

### Classification Code System (COMMON_CODE)

Codes follow the pattern `{TOP}{MID}{sequence}`:
- **G** (지질/Geology): Ga=암석(rocks), Gb=층서(stratigraphy), Gc=구조(structure)
- **L** (지형/Landform): La=동굴(caves), Lb=자연지형(natural landforms)
- **F** (화석/Fossil): Fa=척추동물(vertebrate), Fb=무척추동물(invertebrate), Fc=식물(plant), Fd=생흔(trace), Fe=미화석(micro)
- **N** (자연현상/Natural phenomena): Na=바람(wind), Nb=물/지하수(water), Nc=해양(ocean)

## Development Log (`devlog/`)

Files in `devlog/` follow two naming conventions:

- **`YYYYMMDD_P99_title.md`** — Plan. Written *before* starting work. Contains goals, design decisions, file structure, etc.
- **`YYYYMMDD_999_title.md`** — Work log. Written *after* work is done. Records what was actually implemented, files created/modified, and verification results.

The numeric part (`P99` / `999`) is a sequence number within the same date. Plans and work logs are numbered independently (e.g. `P01`, `P02` for plans; `001`, `002` for logs). A work log should reference the plan it is based on when applicable.

## Session Handoff

Read `docs/HANDOFF.md` at the start of every new session. It contains the current project state, what has been built, route map, project structure, and remaining work.

## Key Files

- `sql/geological_heritage_sqlite_schema.sql` — Full database schema (all tables, indexes, foreign keys)
- `sql/common_code.sql` — INSERT statements for classification reference data
- `heritage_list/` — Field survey list PDFs (현장조사목록) from 2022-2024

## Commands

```bash
# Initialize the database
sqlite3 ghc2026.db < sql/geological_heritage_sqlite_schema.sql

# Load classification codes
sqlite3 ghc2026.db < sql/common_code.sql
```
