# Project Overview

## What This Is
Static website visualizing job and task complexity metrics across occupations and geographic regions using BLS (Bureau of Labor Statistics) and O*NET data.

## Tech Stack
- **Frontend**: HTML/JS/CSS, Plotly.js (treemaps), D3.js (network viz), jQuery, Bootstrap
- **Data Pipeline**: Python (SQLite, CSV processing)
- **Deployment**: GitHub Pages (pure static, no backend)
- **Testing**: pytest + Playwright (visual regression)

## Key URLs
- Repo: GitHub Pages static hosting
- Data sources: BLS OES, O*NET

## Data Format
- JSONP pattern: `window.BLS_DATA = { jobData: [...] }` in `data/job_data.js`
- Avoids CORS issues with static file hosting
- Libraries hosted locally in `lib/` for offline/caching

## Current State (as of Phase 5)
- 3 active HTML visualizations in `visualizations/`
- 50 state CSVs, 37 metro CSVs, 7 country CSVs
- 10 sample records in job_data.js (needs full pipeline to populate ~720+)
- Test suite: 43 tests (41 pass, 2 xfail due to insufficient data)
