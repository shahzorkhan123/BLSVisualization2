# Cleanup Inventory

This document records all files removed during Phase 4 cleanup, with reasoning.

**Total before cleanup**: 195 HTML files, ~740MB
**Total after cleanup**: 5 HTML files, ~74KB
**Space freed**: ~740MB

## Files KEPT (Actively Used)

| File | Size | Reason |
|------|------|--------|
| `index.html` | 10KB | Main landing page |
| `visualizations/direct_html_job_treemap.html` | 16KB | Job Complexity Treemap (linked from index) |
| `visualizations/direct_html_compensation_treemap.html` | 16KB | Job Price Treemap (linked from index) |
| `visualizations/refined_job_space.html` | 27KB | Job Space Network (linked from index) |
| `documentation/reproducibility.html` | 6KB | Documentation (linked from index) |

Also kept: `lib/`, `shared/`, `data/`, `scripts/`, `research/`, `documentation/*.md`, root docs

## Category A: Root Test/Debug Files (5 files, ~28KB)

| File | Size | Reason for Removal |
|------|------|--------------------|
| `debug_visualizations.html` | 2KB | Debug file, not linked |
| `test_dropdowns.html` | 9KB | Test file, not linked |
| `test_visualizations.html` | 2KB | Test file, not linked |
| `test_visualizations_direct.html` | 2KB | Test file, not linked |
| `test_visualizations_fixed.html` | 2KB | Test file, not linked |

## Category B: Abandoned interactive_visualizations/ Directory (5 files, ~23MB)

All files contain embedded data (~4.7MB each), never linked from index.html.

| File | Size | Reason for Removal |
|------|------|--------------------|
| `interactive_visualizations/complexity_price_scatter.html` | 4.7MB | Embedded data, orphaned |
| `interactive_visualizations/country_rankings.html` | 4.7MB | Embedded data, orphaned |
| `interactive_visualizations/geographic_map.html` | 4.7MB | Embedded data, orphaned |
| `interactive_visualizations/metro_bubble_map.html` | 4.7MB | Embedded data, orphaned |
| `interactive_visualizations/us_states_map.html` | 4.7MB | Embedded data, orphaned |

## Category C: Orphaned Visualizations (42 files, ~111MB)

### C1: Test/Debug variants (4 files)
| File | Reason |
|------|--------|
| `visualizations/cors_fix_test.html` | CORS test file |
| `visualizations/debug_treemap.html` | Debug file |
| `visualizations/minimal_debug_treemap.html` | Debug file |
| `visualizations/minimal_test_treemap.html` | Test file |

### C2: _original, _fixed, _updated, _robust variants (8 files)
| File | Reason |
|------|--------|
| `visualizations/direct_html_compensation_treemap_original.html` | Superseded by current version |
| `visualizations/direct_html_job_treemap_original.html` | Superseded by current version |
| `visualizations/interactive_job_atlas_fixed.html` | _fixed variant |
| `visualizations/interactive_job_atlas_fixed_labels.html` | _fixed variant |
| `visualizations/interactive_job_atlas_robust.html` | _robust variant |
| `visualizations/interactive_job_atlas_updated.html` | _updated variant |
| `visualizations/job_complexity_treemap_fixed.html` | _fixed variant (4.7MB) |
| `visualizations/job_price_treemap_fixed.html` | _fixed variant (4.7MB) |
| `visualizations/job_space_network_fixed.html` | _fixed variant |

### C3: Large embedded-data visualizations (21 files, ~100MB)

All contain 4.5-5MB of embedded data. The active visualizations use `data/job_data.js` instead.

| File | Size |
|------|------|
| `visualizations/direct_treemap.html` | 5.0MB |
| `visualizations/fixed_label_compensation_treemap.html` | 4.7MB |
| `visualizations/fixed_label_full_treemap.html` | 4.7MB |
| `visualizations/fixed_label_treemap.html` | 4.7MB |
| `visualizations/fixed_treemap.html` | 4.9MB |
| `visualizations/fixed_treemap_compensation.html` | 4.9MB |
| `visualizations/full_treemap.html` | 4.7MB |
| `visualizations/job_complexity_sunburst.html` | 4.7MB |
| `visualizations/job_complexity_treemap.html` | 4.7MB |
| `visualizations/job_complexity_vs_price_scatter.html` | 4.8MB |
| `visualizations/job_price_treemap.html` | 4.7MB |
| `visualizations/job_space_simplified.html` | 4.7MB |
| `visualizations/minimal_treemap.html` | 4.7MB |
| `visualizations/most_complex_jobs_treemap.html` | 4.7MB |
| `visualizations/robust_treemap.html` | 4.7MB |
| `visualizations/robust_treemap_compensation.html` | 4.7MB |
| `visualizations/state_job_complexity_map.html` | 4.7MB |
| `visualizations/state_job_price_map.html` | 4.7MB |
| `visualizations/top_jobs_complexity_treemap.html` | 4.7MB |
| `visualizations/top50_jobs_bubble_chart.html` | 4.7MB |
| `visualizations/top50_treemap.html` | 4.7MB |

### C4: Small orphaned files not linked from index (9 files)
| File | Size | Reason |
|------|------|--------|
| `visualizations/direct_html_treemap.html` | 2KB | Incomplete/stub |
| `visualizations/fixed_approach_treemap.html` | 6KB | Not linked |
| `visualizations/gdp_treemap.html` | 10KB | Not linked |
| `visualizations/interactive_job_atlas.html` | 658KB | Not linked (has embedded data) |
| `visualizations/interactive_job_atlas_direct.html` | 12KB | Not linked |
| `visualizations/job_complexity_treemap_improved.html` | 645KB | Not linked |
| `visualizations/job_space_network.html` | 80KB | Superseded by refined_job_space.html |
| `visualizations/job_space_network_refined.html` | 85KB | Duplicate of refined_job_space.html |
| `visualizations/simplified_job_space.html` | 8KB | Not linked |

## Category D: Treemaps Root Files (7 files, ~28MB)

All contain embedded data. The interactive treemap uses legacy CSV loading.

| File | Size | Reason |
|------|------|--------|
| `treemaps/interactive_treemap.html` | 19KB | Legacy CSV loading, not linked |
| `treemaps/job_task_relationships.html` | 4.7MB | Embedded data |
| `treemaps/task_importance_by_occupation.html` | 4.7MB | Embedded data |
| `treemaps/tasks_by_work_activity_groups.html` | 4.7MB | Embedded data |
| `treemaps/tasks_detailed.html` | 4.7MB | Embedded data |
| `treemaps/us_labor_market_detailed.html` | 4.7MB | Embedded data |
| `treemaps/us_labor_market_major_groups.html` | 4.7MB | Embedded data |

Also removing legacy data files:
| File | Reason |
|------|--------|
| `treemaps/enhanced_job_data.csv` | Legacy data, replaced by data/job_data.js |
| `treemaps/combined_job_data.json` | Legacy data, replaced by data/job_data.js |

## Category E: Pre-generated State/Metro Treemaps (~580MB)

100 state treemaps + 30 metro treemaps, all with embedded data (~4.5MB each).
Redundant because the active visualizations dynamically filter by state/metro via dropdown controls.

- `treemaps/states/` - 100 HTML files (~445MB)
- `treemaps/metros/` - 30 HTML files (~134MB)
