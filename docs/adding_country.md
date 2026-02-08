# Adding a New Country

This guide explains how to add occupational data for a new country to the BLS visualization pipeline.

## Prerequisites

- Python 3.10+
- CSV data file with occupational statistics

## CSV Format

Your CSV file must have these columns (header row required):

```csv
occupation_code,occupation_title,employment,mean_annual_wage,complexity_score
```

- **occupation_code**: SOC format (`XX-XXXX`) for US, or ISCO format (`OC1`-`OC9`) for international
- **occupation_title**: Human-readable occupation name
- **employment**: Number of workers (integer)
- **mean_annual_wage**: Average annual wage in local currency (integer)
- **complexity_score**: Will be ignored by the pipeline (recomputed as normalized GDP)

## Steps

### 1. Add Country Configuration

Edit `scripts/pipeline/config.py` and add an entry to the `COUNTRIES` dict:

```python
COUNTRIES = {
    # ... existing countries ...
    "BRA": {
        "name": "Brazil",
        "code_system": "ISCO",
        "currency": "BRL",
        "national_csv": DATA_DIR / "bra_occupational_data.csv",
        "national_region_name": "Brazil",
    },
}
```

### 2. Place CSV Data

Put the national CSV file at the configured path:
```
data/bra_occupational_data.csv
```

### 3. Add Metro Data (Optional)

If the country has metropolitan-area data:

1. Place CSV files in `data/metros/`:
   ```
   data/metros/sao_paulo_occupational_data.csv
   data/metros/rio_de_janeiro_occupational_data.csv
   ```

2. Add metro-to-country mapping in `config.py`:
   ```python
   METRO_COUNTRY_MAP = {
       # ... existing entries ...
       "sao_paulo": "BRA",
       "rio_de_janeiro": "BRA",
   }
   ```

3. Add display names in `config.py`:
   ```python
   METRO_DISPLAY_NAMES = {
       # ... existing entries ...
       "sao_paulo": "São Paulo",
       "rio_de_janeiro": "Rio de Janeiro",
   }
   ```

### 4. Add State/Province Data (Optional)

If the country has state-level data:

1. Create a directory: `data/states_bra/` (or similar)
2. Place state CSVs inside
3. Add `states_dir` to the country config:
   ```python
   "BRA": {
       ...
       "states_dir": DATA_DIR / "states_bra",
   },
   ```

### 5. Run the Pipeline

```bash
# Rebuild everything
python scripts/pipeline/run_pipeline.py --year 2024 --fresh

# Export including the new country
python scripts/pipeline/run_pipeline.py --export-only --export-country USA BRA
```

### 6. Verify

1. Check the pipeline output summary for your country's record counts
2. Open `data/export/combined_data.csv` to verify data in Excel
3. If exporting to JSONP, open the treemap in a browser to verify rendering

## Code System Detection

The pipeline auto-detects the code system from the first occupation code:
- `XX-XXXX` pattern → SOC (US Bureau of Labor Statistics)
- `OC1`-`OC9` pattern → ISCO (International Standard Classification)

If your country uses a different code format, you'll need to update `import_csv.py:detect_code_system()`.

## Notes

- Complexity scores from CSVs are **ignored** — the pipeline recomputes them as min-max normalized GDP per region
- GDP is auto-calculated as `employment × mean_annual_wage`
- Each region gets its own normalized complexity range (0-1) so treemaps always show full color variation
- The default JSONP export only includes USA. Use `--export-country` to include additional countries.
