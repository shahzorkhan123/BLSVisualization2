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






# Phase 5b: Split Data for Lazy Loading

## Context

`data/job_data.js` is 360KB with 720 records. Only 10 unique occupations are repeated across 72 regions — massive duplication. Every page load downloads all 720 records even though the user only views one region at a time. This is wasteful for mobile users.

**Goal**: Split into per-region files loaded on demand. Metadata (occupation names, region display names) lives in a small always-loaded file. Region data files contain only compact value arrays — no repeated keys, no metadata. The filename itself encodes year, region type, region slug, and country code.

**Payload comparison**:
- Before: 360KB on every page load
- After: ~5KB initial (metadata) + ~400 bytes per region on demand
- Typical mobile session: **~5.4KB** (98% reduction)

---

## Generated File Architecture

### 1. `data/meta.js` (~5KB, always loaded)

Single metadata file with occupation lookup AND region manifest. No data file needs to repeat any of this.

```javascript
window.BLS_META = {
  years: [2024],
  // Occupation lookup: [soc_code, title, major_group_prefix, major_group_name]
  occ: [
    ["11-0000", "Management Occupations", "11", "Management"],
    ["13-0000", "Business and Financial Operations", "13", "Business and Financial Operations"],
    // ... 8 more
  ],
  // Regions grouped by type: [slug, display_name, country_code]
  regions: {
    "National": [
      ["national-united_states", "United States", "us"]
    ],
    "State": [
      ["state-alabama", "Alabama", "us"],
      ["state-california", "California", "us"],
      // ... 48 more
    ],
    "Metro": [
      ["metro-atlanta", "Atlanta-Sandy Springs-Alpharetta, GA", "us"],
      // ... 20 more
    ]
  }
};
```

### 2. `data/regions/{year}.{slug}.{country}.data.js` (~300-400 bytes each)

**Pure value arrays only.** The filename encodes all context (year, region type, region, country). No metadata repeated inside.

```javascript
// File: data/regions/2024.state-california.us.data.js
// Rows: [occ_index, employment, wage, gdp, complexity_score]
window.BLS_LOAD([
[0,10990,118597,1303317030,1.0],
[1,10231,89827,919101337,0.5632],
[2,5221,107475,561127475,0.2879],
[3,2870,89188,255929560,0.0531],
[4,1145,86791,99375595,0.0],
[5,2511,56131,140936841,0.0319],
[6,1389,115972,161085108,0.0475],
[7,5001,70112,350630112,0.1932],
[8,4980,113862,566832360,0.3594],
[9,2314,54271,125590994,0.0201]
]);
```

- `occ_index` maps to `window.BLS_META.occ[index]`
- `slug` in filename maps to `window.BLS_META.regions[type]` entries
- No region name, year, or occupation title stored inside — all derivable from filename + meta.js

### 3. `data/job_data.js` (kept as-is for backward compat)

Still generated by existing `export_jsonp.py`. Used by:
- `tests/conftest.py` (regex parsing)
- `tests/test_data_validation.py`
- Could be removed in future once split approach is fully validated

### Filename Convention

| Region | Filename |
|--------|----------|
| US National | `2024.national-united_states.us.data.js` |
| California | `2024.state-california.us.data.js` |
| New York (state) | `2024.state-new_york.us.data.js` |
| Atlanta metro | `2024.metro-atlanta.us.data.js` |
| NYC metro | `2024.metro-new_york.us.data.js` |
| St. Louis metro | `2024.metro-st_louis.us.data.js` |

**Slug algorithm**:
- Prefix = region_type lowercased
- National/State: lowercase display name, spaces → underscores, strip punctuation
- Metro: first city only (before first `-` or `,`), same cleanup

---

## Files to Create

| File | Purpose |
|------|---------|
| `scripts/pipeline/export_split.py` | Generate meta.js + region files from SQLite |
| `data/meta.js` | Occupation lookup + region manifest (generated) |
| `data/regions/*.data.js` | 72 per-region data files (generated) |

## Files to Modify

| File | Change |
|------|--------|
| `scripts/pipeline/run_pipeline.py` | Add `export_split` call after existing exports |
| `shared/utils.js` | Add `loadRegionData()`, `expandCompactRows()`, `findManifestEntry()` |
| `visualizations/direct_html_job_treemap.html` | Replace job_data.js with meta.js, add Load Data button, lazy loading |
| `visualizations/direct_html_compensation_treemap.html` | Same changes |
| `tests/test_pipeline.py` | Add `TestExportSplit` class |
| `tests/test_link_checker.py` | Add meta.js and regions/ existence checks |

---

## Pipeline: `scripts/pipeline/export_split.py`

Key function: `export_split(conn, country_codes, output_dir)`

1. Query all records with country code
2. Build occupation lookup (deduplicate SOC codes → indexed array)
3. Group records by (year, region_type, region, country)
4. For each group:
   - Generate slug from region type + name
   - Write `data/regions/{year}.{slug}.{country}.data.js` with compact rows
5. Write `data/meta.js` with occ lookup + region manifest (years, regions by type)
6. Return stats dict

`_make_slug()` helper:
- Metro: `re.split(r"[-,]", name)[0]` → first city, lowercased, spaces to underscores
- State/National: lowercase, spaces to underscores, strip non-alphanumeric

---

## Frontend Loading Flow

### HTML Changes (both treemap files)

**Script tags** — replace `<script src="../data/job_data.js">` with:
```html
<script src="../data/meta.js"></script>
```

**Add Load Data button** after the vocation-limit control group:
```html
<div class="control-group">
    <label>&nbsp;</label>
    <button id="load-data-btn">Load Data</button>
</div>
```

**Year dropdown** — populated dynamically from `BLS_META.years` (remove hardcoded 2020-2024 options)

**Region dropdown** — populated from `BLS_META.regions[selectedType]` (remove hardcoded state/metro arrays)

### `shared/utils.js` — New Functions

```javascript
var BLS_REGION_CACHE = {};

function loadRegionData(slug, year, country, callback) {
    var key = year + '.' + slug + '.' + country;
    if (BLS_REGION_CACHE[key]) { callback(BLS_REGION_CACHE[key]); return; }

    window.BLS_LOAD = function(rows) {
        var expanded = expandCompactRows(rows, slug, year);
        BLS_REGION_CACHE[key] = expanded;
        callback(expanded);
    };

    var script = document.createElement('script');
    script.src = '../data/regions/' + key + '.data.js';
    script.onerror = function() { callback([]); };
    document.head.appendChild(script);
}

function expandCompactRows(rows, slug, year) {
    // Look up region type + display name from BLS_META.regions using slug
    // Map each row: occ_index → BLS_META.occ[index] for SOC_Code, title, group
    // Return array of full record objects matching existing schema
}

function findManifestEntry(regionType, regionName) {
    // Find [slug, name, country] in BLS_META.regions[regionType] by name
}
```

**Key design**: `expandCompactRows` reconstructs the full record objects (same schema as `job_data.js` records) so `updateTreemap()` works without any changes.

### Init Flow

1. Page loads → `meta.js` loaded (tiny, synchronous)
2. `$(document).ready`: populate year dropdown from `BLS_META.years`, call `updateRegionDropdown()`
3. Show placeholder: "Select a region and click Load Data"
4. User selects dropdowns → clicks **Load Data**
5. `loadRegionData()` injects `<script>` for the one region file (~400 bytes)
6. Callback expands compact rows → full records → `updateTreemap()` renders
7. Changing parameter/color/limit re-renders from cached data (no re-load)
8. Changing year/region type/region shows placeholder again (need new Load Data click)

### jQueryLite Compatibility

All new code uses:
- `.append('<option value="x">text</option>')` — strings only (no `$('<option>', {})`)
- `.empty()`, `.val()`, `.click()`, `.change()` — all supported
- `document.createElement('script')` — vanilla JS for dynamic loading

---

## Test Changes

### `tests/test_pipeline.py` — New `TestExportSplit` class

- `test_export_split_creates_files` — 72 region files + meta.js
- `test_meta_structure` — parse meta.js, verify years/occ/regions
- `test_region_file_compact_format` — verify `window.BLS_LOAD([...])` format, 10 rows, 5 values each
- `test_all_manifest_files_exist` — every region in meta.js has a corresponding file
- `test_slug_generation` — unit test `_make_slug()` for edge cases (St. Louis, New York, etc.)

### `tests/test_link_checker.py` — New checks

- `test_meta_js_exists`
- `test_regions_directory_not_empty`

---

## Implementation Order

1. Create `scripts/pipeline/export_split.py`
2. Wire into `scripts/pipeline/run_pipeline.py` (add import + call)
3. Run pipeline → generates `data/meta.js` + `data/regions/*.data.js`
4. Add lazy-loading functions to `shared/utils.js`
5. Update `visualizations/direct_html_job_treemap.html` (meta.js, Load Data button, init flow)
6. Update `visualizations/direct_html_compensation_treemap.html` (same)
7. Add tests to `tests/test_pipeline.py` and `tests/test_link_checker.py`
8. Run full test suite: `pytest tests/ -v -k "not screenshot"`
9. Manual browser test: open treemaps via file://, verify Load Data works

---

## Verification

1. `python scripts/pipeline/run_pipeline.py --year 2024 --fresh` — generates meta.js + 72 region files
2. `ls data/regions/ | wc -l` → 72 files
3. Check `data/meta.js` has 10 occupations, 72 regions across 3 types
4. Open `visualizations/direct_html_job_treemap.html` in browser:
   - Dropdowns populated from meta.js (50 states, 21 metros)
   - Click Load Data → treemap renders
   - Change state → click Load Data → different data renders
   - Network tab shows only ~400 byte request per region
5. `pytest tests/ -v -k "not screenshot"` — all tests pass
