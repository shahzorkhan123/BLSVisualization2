# Design Decisions

## Region_Type: "Metro" not "Metropolitan"
- HTML dropdown `<option value="Metro">` sends "Metro" as the filter value
- Data must use "Metro" to match (not "Metropolitan")
- Tests updated to validate "Metro"

## SQLite as Source of Truth
- Not DuckDB-WASM (too heavy for static site)
- SQLite DB is intermediate artifact, gitignored
- CSVs are the original source, JSONP is the output

## Complexity Score: GDP Placeholder
- Real complexity from O*NET deferred
- Current: `complexity_score = min-max normalized GDP per (year, region)`
- Per-region normalization ensures each treemap view gets full 0-1 color range
- If all GDPs equal in a region, set 0.5

## Code Systems
- US: SOC codes (XX-XXXX format, e.g., "11-0000")
- International: ISCO-based (OC1-OC9 format)
- Detection via regex on first occupation code in CSV

## Metro-to-Country Mapping
- US metros: default to 'USA'
- International metros mapped explicitly (london→GBR, mumbai→IND, etc.)

## String Pooling Deferred
- Not needed until data volume warrants it
- Current ~720 US records is manageable without optimization

## Employment Values
- Import as-is from CSV (no multiplication)
- If scaling needed later, add `employment_multiplier` to country config
