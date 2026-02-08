# Architecture

## Directory Structure
```
/
├── lib/                    # Local libraries (Plotly, jQuery, D3, Bootstrap)
├── shared/                 # Reusable JS/CSS (treemap.js, utils.js, common.css)
├── data/                   # Data files
│   ├── job_data.js         # JSONP data (window.BLS_DATA)
│   ├── states/             # 50 state CSVs
│   ├── metros/             # 37 metro CSVs (US + international)
│   ├── export/             # Intermediate CSVs for Excel (gitignored)
│   ├── *.csv               # Country-level CSVs (us_, gbr_, ind_, etc.)
│   └── bls.db              # SQLite database (gitignored)
├── visualizations/         # 3 HTML visualization pages
├── scripts/                # Python scripts
│   ├── pipeline/           # Data pipeline package
│   └── *.py                # Legacy scripts
├── tests/                  # pytest + Playwright tests
├── research/               # Research docs (not published)
├── memory-bank/            # AI context files
└── index.html              # Landing page
```

## Data Flow
```
CSV Sources (data/states/*.csv, data/metros/*.csv, data/*_occupational_data.csv)
    ↓
[scripts/pipeline/import_csv.py]  — Parse & detect SOC vs ISCO
    ↓
SQLite DB (data/bls.db)           — Source of truth
    ↓
[scripts/pipeline/export_csv.py]  — Intermediate CSVs for Excel
    ↓
data/export/*.csv                 — Flat CSVs
    ↓
[scripts/pipeline/export_jsonp.py] — Generate website data
    ↓
data/job_data.js                  — window.BLS_DATA (JSONP)
```

## Frontend Contract (window.BLS_DATA.jobData schema)
```json
{
    "year": 2024,
    "Region_Type": "National|State|Metro",
    "Region": "United States",
    "SOC_Code": "11-0000",
    "OCC_TITLE": "Management Occupations",
    "SOC_Major_Group": "11",
    "SOC_Major_Group_Name": "Management",
    "TOT_EMP": 9270000,
    "A_MEAN": 126480,
    "GDP": 1173091200000,
    "complexity_score": 0.85
}
```

## CSV Source Schema
```
occupation_code,occupation_title,employment,mean_annual_wage,complexity_score
11-0000,Management Occupations,9270,126480,0.85
```
Note: employment values in CSVs may be in thousands or raw counts (varies by source).
