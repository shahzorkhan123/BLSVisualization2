# Implementation Plan

## 1. Replace Sample Data with Real Datasets
1. Acquire latest BLS Occupational Employment and Wage Statistics (OEWS) files and ONET task data.
2. Update file paths in `scripts/data_processing/parse_bls_data_improved.py` and `process_bls_excel_data.py` to point to the new raw data locations.
3. Run `parse_bls_data_improved.py` to extract national, state, and metro statistics into `data/bls/`.
4. Execute `process_bls_excel_data.py` to create structured CSVs for national and state datasets, including major and uber categories.
5. Run `process_bls_onet_data_final.py` to merge ONET tasks with BLS occupation codes.
6. Commit generated CSVs to `data/` and `data/processed/` so that visualizations load real data.

## 2. Generate Category-Specific CSV Files
1. For each category (national, states, metros, tasks), produce dedicated CSV files using the processing scripts.
2. Store outputs under `data/processed/<category>/` to maintain organization.
3. Create a validation script that checks file presence and basic schema (columns, row counts) before committing.
4. Document the generation steps in `documentation/reproducibility.md` and ensure reproducibility instructions reference the new scripts.

## 3. Introduce Interactive Filters
1. Review Harvard Atlas features for reference (search, dropdowns, cross-filtering).
2. In `index.html` and visualization templates, add filter controls for:
   - Geography (country, state, metro)
   - Occupation categories (major and uber groups)
   - Metrics (complexity, wage, employment)
   - Time period (where applicable)
3. Implement filter logic in JavaScript to hide/show or recolor elements based on selections.
4. Ensure filters maintain state across visualizations where relevant (e.g., selected occupation highlighted in treemap and job space).
5. Test filters with real data to confirm performance and usability.

## 4. Implement Automated Year/Country Data Pipelines
1. Create a parameterized ingestion script (e.g., `scripts/data_processing/update_data.py`) that accepts `year` and `country` inputs.
2. For `US`, fetch BLS OEWS and ONET files for the specified year; for other countries, integrate their respective labor databases (e.g., Eurostat, ILO).
3. Normalize all sources to a shared schema and store raw files in `data/raw/<country>/<year>/`.
4. Execute existing processing scripts to generate category CSVs under `data/processed/<country>/<year>/`.
5. Provide a Makefile or CLI entry that runs the full pipeline and updates data in place.
6. Schedule the pipeline via GitHub Actions or cron to refresh datasets annually.
7. Document pipeline usage and country data source mappings in `documentation/reproducibility.md`.

## 5. Clean Up and Streamline
1. Identify unused or experimental HTML files and remove or archive them.
2. Consolidate visualization scripts to reduce duplication.
3. Standardize data file naming conventions and directory structure.
4. Update README and documentation to reflect the finalized workflow.

## 6. Future Enhancements
- Integrate time-series analysis once multiple years of data are available.
- Expand data pipelines to additional country sources and historical backfilling.
- Explore deploying the site with a lightweight backend for dynamic data queries.
