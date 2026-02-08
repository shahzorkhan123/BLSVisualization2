# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a static website project that visualizes job and task complexity metrics across occupations and geographic regions using BLS (Bureau of Labor Statistics) and O*NET data. The visualizations are built using Plotly.js treemaps and are designed to work both locally and when deployed to static hosting platforms like GitHub Pages.

## Architecture

### CORS-Free Static Architecture

The project uses a **lightweight, cacheable architecture** that solves CORS issues inherent in static file hosting:

- **Embedded Data Approach**: Data is embedded directly in JavaScript files (`window.BLS_DATA`) instead of loaded via AJAX to avoid CORS restrictions
- **Local Library Hosting**: All external libraries (Plotly, jQuery, Bootstrap) are hosted locally in `lib/` for better caching and offline functionality
- **Shared Components**: Common functionality is extracted into reusable modules in `shared/`

### Directory Structure

```
/
├── lib/                        # Local copies of external libraries
│   ├── plotly.min.js          # Plotly.js for treemap visualizations
│   ├── jquery.min.js          # jQuery for DOM manipulation
│   ├── d3.min.js              # D3.js for network visualizations
│   └── bootstrap.min.css      # Bootstrap CSS for styling
├── shared/                     # Reusable components
│   ├── common.css             # Common styles for visualizations
│   ├── utils.js               # Utility functions (CSV parsing, export, filtering)
│   └── treemap.js             # Treemap visualization functions
├── data/                       # Data files in JSONP format
│   ├── job_data.js            # Main BLS data (window.BLS_DATA)
│   ├── states/                # State-level data
│   └── metros/                # Metropolitan area data
├── visualizations/             # HTML visualization pages
│   └── *.html                 # Individual treemap and visualization pages
├── treemaps/                   # Additional treemap-related files
│   ├── interactive_treemap.html
│   ├── enhanced_job_data.csv
│   └── combined_job_data.json
├── scripts/                    # Python scripts for data processing
│   ├── data_processing/       # BLS and O*NET data processing
│   ├── complexity/            # Complexity score calculations
│   ├── visualization/         # Visualization generation
│   └── update_data.py         # Main script to update data files
├── research/                   # Research and analysis files (not published)
│   ├── paper/                 # Academic paper and images
│   ├── complexity/            # Complexity analysis experiments
│   ├── job_space/             # Job space analysis
│   ├── docs/                  # Research documentation
│   │   ├── data_sources.md
│   │   ├── theoretical_analysis.md
│   │   ├── theory_validation.md
│   │   ├── updated_research_document.md
│   │   └── harvard_atlas_visualization_analysis.md
│   └── demo_architecture.py   # Demo/prototype scripts
└── index.html                  # Main landing page
```

### Key Architectural Patterns

1. **JSONP-Style Data Loading**: Data files like `data/job_data.js` export data to `window.BLS_DATA` to avoid CORS issues with static hosting

2. **Two Data Approaches**:
   - **Embedded Data**: Some HTML files have data embedded directly (older approach)
   - **Shared Data Files**: Newer files use `data/job_data.js` loaded via `<script>` tag

3. **Treemap Visualization Pattern**: Most visualizations follow a common pattern:
   - Load data (embedded or from `window.BLS_DATA`)
   - Provide dropdown controls for filtering (year, region type, region, parameter, color scheme)
   - Update Plotly treemap based on user selections
   - Support CSV export of filtered data

## Data Structure

### Primary Data Schema

The BLS job data contains these key fields:
- `year`: 2020-2024
- `Region_Type`: "National", "State", or "Metropolitan"
- `Region`: Geographic region name
- `SOC_Code`: Standard Occupational Classification code
- `OCC_TITLE`: Occupation title
- `SOC_Major_Group_Name`: Major occupation group
- `TOT_EMP`: Total employment
- `A_MEAN`: Annual mean wage
- `GDP`: Calculated as TOT_EMP × A_MEAN
- `complexity_score`: Job complexity metric derived from O*NET

## Common Development Commands

### Updating Data

To update the job data with new CSV files:

```bash
python scripts/update_data.py --csv path/to/enhanced_job_data.csv
```

This script:
- Reads CSV data with BLS job statistics
- Converts to JSONP format (`window.BLS_DATA = {...}`)
- Writes to `data/job_data.js`
- Preserves the CORS-free architecture

### Local Development

1. **Open HTML files directly**: Due to the CORS-free architecture, you can open visualization HTML files directly in a browser using the `file://` protocol

2. **Use a local server** (optional but recommended):
   ```bash
   # Python 3
   python -m http.server 8000

   # Then visit http://localhost:8000
   ```

### Data Processing Scripts

Located in `scripts/`:
- `data_processing/process_bls_onet_data_final.py`: Process raw BLS and O*NET data
- `complexity/calculate_complexity_final.py`: Calculate job complexity scores from O*NET task data
- `visualization/create_improved_treemaps.py`: Generate treemap visualizations
- `update_data.py`: Update `data/job_data.js` from CSV files

## Visualization Controls

All interactive treemaps support these dropdown controls:

1. **Year Selection**: Filter by year (2020-2024)
2. **Region Type**: National, State, or Metropolitan
3. **Region**: Specific geographic region (dynamically populated)
4. **Treemap Parameter**: Size by employment or GDP
5. **Color Scheme**: Color by complexity, employment, or wage
6. **Vocation Limit**: Show all occupations or top 50 by employment

## Working with Visualizations

### Creating New Visualizations

When creating new visualization HTML files:

1. **Use the shared architecture**:
   ```html
   <script src="../lib/plotly.min.js"></script>
   <script src="../lib/jquery.min.js"></script>
   <link rel="stylesheet" href="../shared/common.css">
   <script src="../shared/utils.js"></script>
   <script src="../shared/treemap.js"></script>
   <script src="../data/job_data.js"></script>
   ```

2. **Access data via `window.BLS_DATA`**:
   ```javascript
   const allData = window.BLS_DATA.jobData;
   ```

3. **Follow the common dropdown pattern**: See `visualizations/direct_html_job_treemap.html` for reference implementation

### Modifying Existing Visualizations

- **HTML files in `visualizations/`**: These contain the visualization pages
- **Shared components**: Modify `shared/treemap.js` or `shared/utils.js` to affect all visualizations
- **Data updates**: Never modify HTML files for data updates; use `scripts/update_data.py` instead

## Important Constraints

1. **No Backend Required**: This is a pure static site - avoid introducing server-side dependencies
2. **CORS-Free**: Always use the JSONP pattern (`window.BLS_DATA`) for data files, never use AJAX/fetch for data loading
3. **Relative Paths**: All file references must use relative paths to work both locally and on GitHub Pages
4. **Library Versions**: Libraries in `lib/` are pinned versions; test thoroughly before updating

## Deployment

### GitHub Pages

1. Push repository to GitHub
2. Enable GitHub Pages in repository settings (source: main branch, root directory)
3. Site will be available at `https://username.github.io/repository-name/`

All visualizations work identically in local development and on GitHub Pages due to the CORS-free architecture.

### Alternative Platforms

- **Netlify**: Drag and drop the entire directory
- **Vercel**: Use `vercel` CLI from the project root

## Documentation Files

### Production Documentation
- `LIGHTWEIGHT_ARCHITECTURE.md`: Detailed architecture explanation and migration guide
- `CORS_RESOLUTION.md`: Explanation of CORS issues and solutions
- `DROPDOWN_CONTROLS.md`: Guide to dropdown control functionality
- `deployment_instructions.md`: Step-by-step deployment guide

### Research Documentation (in `research/docs/`)
- `data_sources.md`: Information about BLS and O*NET data sources
- `theoretical_analysis.md`: Theoretical framework for job complexity
- `theory_validation.md`: Validation of theoretical models
- `updated_research_document.md`: Comprehensive research documentation
- `harvard_atlas_visualization_analysis.md`: Analysis of Harvard Atlas visualizations

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

## Data Pipeline

### Running the Pipeline

```bash
# Full pipeline (import CSVs + export JSONP)
python scripts/pipeline/run_pipeline.py --year 2024 --fresh

# Import only (rebuild SQLite DB)
python scripts/pipeline/run_pipeline.py --import-only --fresh

# Export only (from existing DB)
python scripts/pipeline/run_pipeline.py --export-only
```

### Pipeline Architecture
- Source CSVs → SQLite (`data/bls.db`) → Intermediate CSVs (`data/export/`) → JSONP (`data/job_data.js`)
- Multi-country extensible (US first, config in `scripts/pipeline/config.py`)
- Complexity placeholder: min-max normalized GDP per region
