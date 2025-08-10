# Repository Exploration Notes

## Project Structure
- **data/**: Contains sample CSV files for occupational data (country, state, metro) and processed outputs like `yearly_job_data.csv`.
- **scripts/**: Python scripts for data processing and visualization generation.
  - `data_processing/parse_bls_data_improved.py` parses raw BLS text data and extracts SOC codes, data types, and area codes.
  - `data_processing/process_bls_excel_data.py` processes national and state Excel files and groups occupations into major and "uber" categories.
  - `data_processing/process_bls_onet_data_final.py` integrates ONET task information.
  - `complexity/` scripts compute job and task complexity scores.
  - `visualization/` scripts create treemaps and job-space visualizations.
- **visualizations/** and **interactive_visualizations/**: HTML files for treemaps, maps, scatter plots, and network visualizations.
- **treemaps/**: Additional treemap HTML files and data like `combined_job_data.json`.
- **documentation/**: Reproducibility instructions and contribution guidelines.
- **index.html**: Landing page linking to treemap, job space network, and documentation pages.

## Data Usage
- Current visualizations rely on sample CSV data in the `data/` directory.
- Scripts expect raw BLS files at `/home/ubuntu/...` paths; these need adjustment for real data integration.
- Processed data is stored under `data/processed/` with subfolders for complexity metrics and yearly job data.

## Notable Observations
- Many standalone visualization HTML files appear to be experiments or duplicates.
- Harvard Atlas analysis (`harvard_atlas_visualization_analysis.md`) outlines desired features such as interactive filtering, cross-linking between views, and comprehensive tooltips.
- Moving to production data will require cleaning unused files and standardizing data pipelines.
