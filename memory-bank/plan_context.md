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
