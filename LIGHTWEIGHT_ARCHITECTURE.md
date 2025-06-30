# Lightweight and Cacheable Web Architecture

## Overview

This document describes the refactored architecture that makes BLS visualization webpages lightweight and cacheable while solving CORS issues and enabling Python-based data updates.

## New Architecture

### Directory Structure

```
/
├── lib/                    # Local copies of external libraries
│   ├── plotly.min.js      # Plotly.js library (local copy)
│   ├── jquery.min.js      # jQuery library (local copy)
│   └── bootstrap.min.css  # Bootstrap CSS (local copy)
├── shared/                # Common reusable components
│   ├── common.css         # Common CSS styles
│   ├── utils.js           # Utility functions (CSV parsing, export, etc.)
│   └── treemap.js         # Treemap visualization functions
├── data/                  # Data files
│   └── job_data.js        # BLS data (JSONP format to avoid CORS)
├── scripts/               # Python scripts for data management
│   └── update_data.py     # Script to update data files
└── visualizations/        # HTML pages
    └── refactored_job_treemap.html  # Example refactored page
```

## Key Improvements

### 1. Local Library Hosting

**Before:**
```html
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
```

**After:**
```html
<script src="../lib/plotly.min.js"></script>
<script src="../lib/jquery.min.js"></script>
```

**Benefits:**
- Better caching (libraries cached indefinitely)
- Reduced external dependencies
- Faster loading for repeat visitors
- Works offline

### 2. Shared Components

**Before:** Duplicate code in every HTML file
**After:** Shared modules for common functionality

**Common CSS (`shared/common.css`):**
- Standard styling for controls, containers, buttons
- Treemap and visualization specific styles
- Responsive design components

**Utility Functions (`shared/utils.js`):**
- CSV parsing
- Data filtering and manipulation
- Export functionality
- Dropdown management
- Color scheme definitions

**Treemap Functions (`shared/treemap.js`):**
- Plotly treemap creation
- Color scale management
- Layout configuration
- Update functions

### 3. CORS-Free Data Loading

**Problem:** Static hosting (GitHub Pages) blocks loading external CSV files due to CORS restrictions.

**Solution:** JSONP-style data loading using JavaScript files:

```javascript
// data/job_data.js
window.BLS_DATA = {
    jobData: [...],
    metadata: {...}
};
```

**Benefits:**
- No CORS issues
- Works with static hosting
- Fast loading (no AJAX overhead)
- Can be updated by Python scripts

### 4. Python-Based Data Updates

**Script:** `scripts/update_data.py`

**Usage:**
```bash
# Update from CSV
python scripts/update_data.py --csv enhanced_job_data.csv

# Update from Parquet (future)
python scripts/update_data.py --parquet job_data.parquet --year 2024
```

**Benefits:**
- HTML files remain unchanged
- Data can be updated programmatically
- Supports both CSV and Parquet formats
- Automatic metadata generation

## Migration Guide

### For Existing HTML Files

1. **Update library references:**
   ```html
   <!-- Old -->
   <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
   
   <!-- New -->
   <script src="../lib/plotly.min.js"></script>
   <script src="../shared/utils.js"></script>
   <script src="../shared/treemap.js"></script>
   <script src="../data/job_data.js"></script>
   ```

2. **Replace embedded data with data loading:**
   ```javascript
   // Old
   const embeddedData = [{...}];
   
   // New
   const allData = getBLSData();
   ```

3. **Use shared functions:**
   ```javascript
   // Old - duplicate parseCSV function
   
   // New - use shared utility
   const data = parseCSV(csvText);
   ```

### For Data Updates

1. **Prepare CSV file** with required columns:
   - year, Region_Type, Region, SOC_Code, OCC_TITLE
   - SOC_Major_Group_Name, TOT_EMP, A_MEAN, GDP, complexity_score

2. **Run update script:**
   ```bash
   python scripts/update_data.py --csv your_data.csv
   ```

3. **Deploy updated files** - only `data/job_data.js` changes

## Performance Benefits

### Caching Strategy

1. **Libraries (`lib/`):** Long-term caching (1 year)
2. **Shared components (`shared/`):** Medium-term caching (1 month)
3. **Data files (`data/`):** Short-term caching (1 day)
4. **HTML files:** Medium-term caching (1 week)

### Bundle Size Reduction

- **Before:** Each HTML file: ~150KB (embedded data + styles + scripts)
- **After:** Each HTML file: ~10KB (references only)
- **Shared resources:** Cached once, used by all pages

### Network Requests

- **Before:** Multiple CDN requests per page load
- **After:** All resources served from same domain (better HTTP/2 multiplexing)

## Browser Compatibility

- **Chrome 60+**
- **Firefox 55+**
- **Safari 12+**
- **Edge 79+**
- **All modern mobile browsers**

## Future Enhancements

### Parquet Support

The architecture supports future migration to Parquet format:

```bash
python scripts/update_data.py --parquet data.parquet --year 2024
```

### Folder Structure for Data

Future folder structure for year-based organization:

```
data/
├── 2024/
│   ├── national/
│   └── state/
├── 2023/
│   ├── national/
│   └── state/
└── job_data.js  # Combined index
```

### Progressive Loading

For large datasets, implement progressive loading:

```javascript
// Load summary data first
const summary = getBLSSummary();
// Load detailed data on demand
const details = await getBLSDetails(filters);
```

## Testing

### Local Development

1. Open HTML files directly in browser (file:// protocol)
2. Verify all dropdowns function correctly
3. Confirm no console errors
4. Test export functionality

### Production Testing

1. Deploy to static hosting (GitHub Pages)
2. Verify identical functionality
3. Check network tab for proper caching headers
4. Validate performance improvements

## Maintenance

### Regular Tasks

1. **Update libraries:** Download latest versions to `lib/`
2. **Update data:** Run `update_data.py` with new CSV files
3. **Monitor performance:** Check bundle sizes and loading times

### Breaking Changes

- Library updates may require testing compatibility
- Data schema changes need script updates
- New browser requirements may need polyfills

## Conclusion

This refactored architecture provides:

✅ **Lightweight pages** - Shared resources reduce redundancy
✅ **Better caching** - Strategic cache management
✅ **CORS-free operation** - Works with static hosting
✅ **Python updatable** - Data updates without HTML changes
✅ **Future-ready** - Supports Parquet and folder structures
✅ **Maintainable** - Clear separation of concerns