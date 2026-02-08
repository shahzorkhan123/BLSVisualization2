# Requirements

## Architecture Constraints
- **CORS-free**: JSONP pattern (`window.BLS_DATA`), never use fetch/AJAX for data loading
- **No backend**: Pure static site, no server-side dependencies
- **No synthetic data**: All data must come from real BLS/O*NET sources
- **Relative paths**: Must work both locally (file://) and on GitHub Pages

## User Requirements
- Mobile-friendly visualizations
- Extensible to multiple countries (US first, then India, Egypt, UK, etc.)
- Complexity = GDP placeholder for now (real O*NET framework later)
- User manages git commits manually (never auto-commit)
- Intermediate CSV exports for Excel analysis

## Data Requirements
- SOC codes for US occupations (XX-XXXX format)
- ISCO codes for international (OC1-OC9 format)
- GDP = employment x mean_annual_wage
- Complexity score: 0-1 range, min-max normalized GDP per region
- Region_Type values: "National", "State", "Metro" (matches HTML dropdowns)
