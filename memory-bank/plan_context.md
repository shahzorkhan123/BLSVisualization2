# Plan Context

## Phase Status
- Phase 0: Research reorganized ✅
- Phase 1: d3.min.js fixed ✅
- Phase 2: Testing (43 tests, 41 pass, 2 xfail) ✅
- Phase 4: Cleanup (195→5 HTML files) ✅
- Phase 5: Data Pipeline ✅
- Phase 6: CI/CD (optional, future)

## Phase 5 Details
- Pipeline: CSV → SQLite → intermediate CSV → JSONP
- Multi-country extensible (US first)
- Complexity placeholder (normalized GDP)
- Expected output: ~720 US records in job_data.js

## Key Decisions Affecting Implementation
- Region_Type uses "Metro" (matches HTML dropdowns)
- SQLite is gitignored (intermediate artifact)
- Export CSVs are gitignored (for local Excel analysis)
- Python package under scripts/pipeline/




# PLAN

# Implementation Plan: Memory Bank + Data Pipeline

## Completed Phases

- Phase 0: Research reorganized ✅
- Phase 1: d3.min.js fixed ✅
- Phase 2: Testing (43 tests, 41 pass, 2 xfail) ✅
- Phase 4: Cleanup (195→5 HTML files) ✅

---

## Pre-Step: Create Memory Bank for AI Context Management

### Context

To optimize token usage across conversations, create a `memory-bank/` directory with structured context files. AI tools should read only relevant files per task instead of loading entire chat history.

### Files to Create

```
memory-bank/
├── active_context.md        # Current work focus, recent changes, next steps
├── plan_context.md          # Current plan status, phase tracking
├── tasks_context.md         # Active tasks, blockers, priorities
├── project_overview.md      # What this project is, tech stack, key URLs
├── requirements.md          # User requirements, constraints, non-negotiables
├── architecture.md          # Directory structure, data flow, frontend contract
├── design_decisions.md      # Key decisions made and why (e.g., JSONP over fetch, Metro vs Metropolitan)
└── tasks_todo.md            # Remaining work items with status
```

### File Contents

**`active_context.md`** — What's happening right now:
- Current phase being worked on
- Last completed step
- Next immediate action
- Any blockers or open questions

**`plan_context.md`** — Phase tracking:
- All phases with status (✅/⏳/❌)
- Current phase details
- Key decisions that affect implementation

**`tasks_context.md`** — Granular task tracking:
- In-progress tasks
- Blocked tasks with reasons
- Recently completed tasks

**`project_overview.md`** — Static project info:
- BLS data visualization static website
- Tech stack: HTML/JS/CSS, Plotly.js, D3.js, Python pipeline
- Deployment: GitHub Pages (no backend)
- Data: BLS/O*NET occupational data, JSONP format

**`requirements.md`** — User requirements:
- CORS-free architecture (JSONP, no fetch for data)
- No synthetic data
- Mobile-friendly
- Extensible to multiple countries
- Complexity = GDP placeholder for now
- User manages git commits manually

**`architecture.md`** — Technical architecture:
- Directory structure
- Data flow: CSV → SQLite → intermediate CSV → JSONP → browser
- Frontend contract (window.BLS_DATA schema)
- Shared components (treemap.js, utils.js)

**`design_decisions.md`** — Decisions log:
- Region_Type uses "Metro" (matches HTML dropdowns)
- SQLite as source of truth (not DuckDB-WASM)
- Per-region GDP normalization for complexity placeholder
- SOC codes for US, ISCO (OC1-OC9) for international
- String pooling deferred until data volume warrants it

**`tasks_todo.md`** — Remaining work:
- Phase 5: Data pipeline (current)
- Phase 6: CI/CD (optional)
- Future: Real complexity framework
- Future: Multi-country frontend support

### CLAUDE.md Update

Add to CLAUDE.md:

```markdown
## Token Optimization & Memory Bank

**Important**: To optimize token usage across conversations:

1. **Read `memory-bank/` files** at the start of each task — only load files relevant to the current work
2. **Never rely on chat history** for project context — always load from memory-bank
3. **Keep memory-bank files updated** after completing work — update active_context.md, tasks_context.md, etc.
4. **Keep responses short** unless detail is requested
5. **If information is missing**, ask which memory-bank file to update rather than storing in chat

### Memory Bank Files
- `active_context.md` — Current work focus and next steps
- `plan_context.md` — Phase tracking and plan status
- `tasks_context.md` — Active/blocked/completed tasks
- `project_overview.md` — Project description and tech stack
- `requirements.md` — User requirements and constraints
- `architecture.md` — Technical architecture and data flow
- `design_decisions.md` — Key decisions and rationale
- `tasks_todo.md` — Remaining work items
```

### Implementation Order (Pre-Step)

1. Create `memory-bank/` directory
2. Create all 8 files with current project state
3. Update `CLAUDE.md` with memory-bank instructions
4. Add `memory-bank/` to version control (not .gitignore — these are project docs)

---

## Phase 5: Extensible Data Pipeline

### Context

The website currently has only 10 sample records in `data/job_data.js`, which breaks treemap rendering. We need to rebuild the data pipeline to import real CSV data into SQLite, generate intermediate CSVs for Excel analysis, and export JSONP for the static website. The pipeline must be extensible to multiple countries (US first, then India, Egypt, etc.).

**Key decisions:**
- Complexity calculation disabled for now — use `complexity_score = normalized GDP (0-1)` as placeholder
- Use `"Metro"` (not `"Metropolitan"`) for Region_Type to match existing HTML dropdowns
- Generate intermediate CSV files before JSONP so data can be analyzed in Excel
- Pipeline is a Python package under `scripts/pipeline/`

## Architecture

```
CSV Sources (data/states/*.csv, data/metros/*.csv, etc.)
    ↓
[scripts/pipeline/import_csv.py]  — Parse & detect code system (SOC vs ISCO)
    ↓
SQLite DB (data/bls.db)           — Source of truth
    ↓
[scripts/pipeline/export_csv.py]  — Intermediate CSVs for Excel analysis
    ↓
data/export/combined_data.csv     — All records, flat CSV
data/export/national_summary.csv  — National-level summary
data/export/by_state.csv          — State-level data
    ↓
[scripts/pipeline/export_jsonp.py] — Generate website data
    ↓
data/job_data.js                  — window.BLS_DATA (JSONP)
```

## SQLite Schema (`scripts/pipeline/db.py`)

```sql
CREATE TABLE countries (
    id INTEGER PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,        -- 'USA', 'IND', 'EGY'
    name TEXT NOT NULL,               -- 'United States', 'India'
    code_system TEXT NOT NULL,        -- 'SOC' or 'ISCO'
    currency TEXT DEFAULT 'USD'
);

CREATE TABLE regions (
    id INTEGER PRIMARY KEY,
    country_id INTEGER NOT NULL REFERENCES countries(id),
    name TEXT NOT NULL,               -- 'United States', 'California', 'New York-Newark'
    region_type TEXT NOT NULL,        -- 'National', 'State', 'Metro'
    UNIQUE(country_id, name, region_type)
);

CREATE TABLE occupations (
    id INTEGER PRIMARY KEY,
    year INTEGER NOT NULL,
    region_id INTEGER NOT NULL REFERENCES regions(id),
    occupation_code TEXT NOT NULL,    -- 'XX-XXXX' (SOC) or 'OC1' (ISCO)
    occupation_title TEXT NOT NULL,
    major_group_name TEXT NOT NULL,
    employment INTEGER NOT NULL,
    mean_annual_wage INTEGER NOT NULL,
    gdp BIGINT NOT NULL,             -- employment × mean_annual_wage
    complexity_score REAL NOT NULL DEFAULT 0.5,
    UNIQUE(year, region_id, occupation_code)
);

CREATE INDEX idx_occ_year ON occupations(year);
CREATE INDEX idx_occ_region ON occupations(region_id);
```

## Files to Create

| File | Purpose |
|------|---------|
| `scripts/pipeline/__init__.py` | Package init |
| `scripts/pipeline/config.py` | Country registry, metro→country mapping, SOC group names |
| `scripts/pipeline/db.py` | Schema creation, CRUD, complexity computation |
| `scripts/pipeline/import_csv.py` | CSV parsing, code system detection, import logic |
| `scripts/pipeline/export_csv.py` | **NEW**: Generate intermediate CSVs for Excel analysis |
| `scripts/pipeline/export_jsonp.py` | Generate `data/job_data.js` from SQLite |
| `scripts/pipeline/validate.py` | Validation checks on DB and output |
| `scripts/pipeline/run_pipeline.py` | CLI orchestrator |
| `tests/test_pipeline.py` | Pipeline tests |
| `docs/adding_country.md` | Guide for adding new countries |
| `data/export/` | Directory for intermediate CSVs |

## Files to Modify

| File | Change |
|------|--------|
| `data/job_data.js` | Regenerated (10 → ~720 records) |
| `tests/test_visual_regression.py` | Remove `xfail` from treemap tests (data now sufficient) |
| `tests/test_data_validation.py` | Update `VALID_REGION_TYPES` to use `"Metro"` instead of `"Metropolitan"` |
| `CLAUDE.md` | Add pipeline usage section |
| `.gitignore` | Add `data/*.db`, `data/export/` |

## Module Details

### 1. `config.py` — Country & Metro Registry

```python
COUNTRIES = {
    'USA': {'name': 'United States', 'code_system': 'SOC', 'currency': 'USD',
            'national_csv': 'data/us_occupational_data.csv',
            'states_dir': 'data/states',
            'metros_pattern': ['new_york_*', 'los_angeles_*', ...]},  # 21 US metros
    'GBR': {'name': 'United Kingdom', 'code_system': 'ISCO', ...},
    'IND': {'name': 'India', 'code_system': 'ISCO', ...},
    'EGY': {'name': 'Egypt', 'code_system': 'ISCO', ...},
    'CAN': {'name': 'Canada', 'code_system': 'ISCO', ...},
    'MEX': {'name': 'Mexico', 'code_system': 'ISCO', ...},
    'EUU': {'name': 'European Union', 'code_system': 'ISCO', ...},
}

METRO_COUNTRY_MAP = {
    'london': 'GBR', 'paris': 'EUU', 'berlin': 'EUU', ...
    'mumbai': 'IND', 'delhi': 'IND', 'bangalore': 'IND',
    'cairo': 'EGY', 'alexandria': 'EGY',
    # US metros default to 'USA'
}

SOC_MAJOR_GROUPS = {
    '11': 'Management', '13': 'Business and Financial Operations', ...
}
```

### 2. `import_csv.py` — CSV Import

Key functions:
- `detect_code_system(code) → 'SOC'|'ISCO'` — regex on first occupation code
- `derive_major_group(code, title, system)` — SOC: lookup by prefix; ISCO: title is the group
- `import_national(conn, country_code, csv_path, year)` — Import one country's national data
- `import_states(conn, country_code, states_dir, year)` — Import all state CSVs from directory
- `import_metros(conn, metro_csv_path, country_code, year)` — Import one metro CSV
- `import_all(conn, year)` — Walk config, import everything found

CSV expected schema: `occupation_code, occupation_title, employment, mean_annual_wage, complexity_score`
GDP auto-calculated as `employment × mean_annual_wage`. Original `complexity_score` from CSV is **ignored** — will be recomputed.

### 3. `db.py` — Complexity Placeholder

```python
def compute_complexity_scores(conn):
    """Set complexity_score = min-max normalized GDP per (year, region).

    Per-region normalization ensures each treemap view gets full 0-1 color range.
    If all GDPs equal in a region, set 0.5.
    """
```

### 4. `export_csv.py` — Intermediate CSVs for Excel

Generates to `data/export/`:
- **`combined_data.csv`** — All records with columns: country, year, region_type, region, occupation_code, occupation_title, major_group_name, employment, mean_annual_wage, gdp, complexity_score
- **`us_national.csv`** — US National only (easy Excel pivot)
- **`us_by_state.csv`** — All US states
- **`us_by_metro.csv`** — All US metros
- **`country_summary.csv`** — One row per country with totals

### 5. `export_jsonp.py` — Website Data

Maps SQLite records to frontend contract:
```
DB column              → JS field
occupation_code        → SOC_Code
occupation_title       → OCC_TITLE
major_group_name       → SOC_Major_Group_Name
employment             → TOT_EMP
mean_annual_wage       → A_MEAN
gdp                    → GDP
region.region_type     → Region_Type  (uses "Metro" to match HTML)
region.name            → Region
```

### 6. `run_pipeline.py` — CLI

```bash
# Full pipeline (import + export)
python scripts/pipeline/run_pipeline.py --year 2024 --fresh

# Import only (rebuild DB)
python scripts/pipeline/run_pipeline.py --import-only --fresh

# Export only (from existing DB)
python scripts/pipeline/run_pipeline.py --export-only

# Specific countries for JSONP export
python scripts/pipeline/run_pipeline.py --export-country USA IND EGY
```

Default: imports all countries found in config, exports US-only JSONP.

## Expected Record Counts

| Region Type | Source | Records |
|-------------|--------|---------|
| National | `us_occupational_data.csv` | 10 |
| State | 50 state CSVs × 10 each | 500 |
| Metro | 21 US metro CSVs × ~10 each | ~210 |
| **US Total** | | **~720** |

International (available for future export):
- 6 countries × ~9 occupations = ~54 national
- 16 international metros × ~9 = ~144

## Implementation Order

1. Create `scripts/pipeline/__init__.py` and `config.py`
2. Create `db.py` (schema + CRUD + complexity computation)
3. Create `import_csv.py` (CSV parsing + import)
4. Create `export_csv.py` (intermediate CSVs)
5. Create `export_jsonp.py` (JSONP generation)
6. Create `validate.py`
7. Create `run_pipeline.py` (CLI orchestrator)
8. Run pipeline: `python scripts/pipeline/run_pipeline.py --year 2024 --fresh`
9. Verify: open treemap in browser, check dropdowns populate
10. Fix tests: update Region_Type validation, remove xfail markers
11. Create `tests/test_pipeline.py`
12. Run full test suite: `pytest tests/ -v`
13. Create `docs/adding_country.md`
14. Update `CLAUDE.md` and `.gitignore`

## Known Issues to Fix During Implementation

1. **Region_Type mismatch**: HTML uses `"Metro"`, tests validate `"Metropolitan"` → update tests to `"Metro"`
2. **Employment units**: Source CSVs have values like 9270 (may be in thousands). Import as-is from CSV; if user needs to multiply, add `employment_multiplier` to country config later.

## Verification

1. `python scripts/pipeline/run_pipeline.py --year 2024 --fresh` — should print summary with ~720 US records
2. Check `data/export/combined_data.csv` opens in Excel with all columns
3. `python -m http.server 8000` → open treemaps, verify dropdowns and rendering
4. `pytest tests/ -v` — all tests should pass (no more xfail)

## Adding a New Country (Extensibility)

1. Add entry to `COUNTRIES` dict in `config.py`
2. Place CSV file at configured path (schema: occupation_code, occupation_title, employment, mean_annual_wage, complexity_score)
3. If the country has state/metro data, add CSV files and configure paths
4. Run `python scripts/pipeline/run_pipeline.py --fresh`
5. To include in website: `--export-country USA NEW_COUNTRY`
