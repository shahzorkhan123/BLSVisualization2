# Reproducibility Guide

This document provides detailed instructions on how to reproduce the data analysis and visualizations in the Job and Task Complexity Atlas. By following these steps, you can recreate our results, extend the analysis to different years or countries, and verify the correctness of our methodology.

## Prerequisites

To reproduce this analysis, you'll need:

1. **Python 3.8+** with the following packages:
   - pandas
   - numpy
   - plotly
   - openpyxl
   - requests
   - matplotlib
   - seaborn

2. **Data Sources**:
   - BLS Occupational Employment and Wage Statistics (OEWS) data
   - O*NET Database (tasks, skills, and abilities)

## Step 1: Download the Required Data

### BLS Occupational Employment and Wage Statistics

1. Visit the [BLS OEWS website](https://www.bls.gov/oes/tables.htm)
2. Download the national and state-level data files:
   - National data: `oesm[YY]nat.zip` (where YY is the year)
   - State data: `oesm[YY]st.zip`

For different years, adjust the file names accordingly. The BLS typically releases updated data annually.

### O*NET Database

1. Visit the [O*NET Resource Center](https://www.onetcenter.org/database.html)
2. Download the latest database release (Excel format)

## Step 2: Process the BLS Data

Use the scripts in the `scripts/data_processing` directory to process the BLS data:

```bash
# Process national data
python process_bls_excel_data.py --input_path /path/to/oesm24nat.xlsx --output_path /path/to/output/national_data.csv

# Process state data
python process_bls_excel_data.py --input_path /path/to/oesm24st.xlsx --output_path /path/to/output/state_data.csv
```

This will extract the relevant occupation data, including employment numbers and wage information.

## Step 3: Process the O*NET Data

Use the O*NET processing script to extract task and skill information:

```bash
python process_bls_onet_data_final.py --onet_dir /path/to/onet/database --output_path /path/to/output/onet_processed.csv
```

This script extracts task importance, task frequency, and skill requirements for each occupation.

## Step 4: Calculate Complexity Metrics

Calculate job and task complexity metrics using the scripts in the `scripts/complexity` directory:

```bash
python calculate_complexity_final.py --bls_data /path/to/national_data.csv --onet_data /path/to/onet_processed.csv --output_dir /path/to/output/complexity/
```

This will generate:
- `job_complexity.csv`: Job complexity index for each occupation
- `task_complexity.csv`: Task complexity index for each occupation

## Step 5: Create Visualizations

Generate the visualizations using the scripts in the `scripts/visualization` directory:

```bash
# Create treemap visualizations
python create_improved_treemaps.py --complexity_data /path/to/job_complexity.csv --output_dir /path/to/visualizations/

# Create job space network visualization
python create_improved_job_space.py --complexity_data /path/to/job_complexity.csv --output_dir /path/to/visualizations/
```

## Extending the Analysis

### Using Different Years of Data

To extend the analysis to different years:

1. Download BLS OEWS data for the desired year
2. Adjust file paths in the processing scripts
3. Run the same workflow as described above

The BLS occasionally changes their data format. If you encounter issues with older or newer data, you may need to modify the data processing scripts accordingly.

### Extending to Different Countries

To extend the analysis to different countries:

1. Obtain occupational employment and wage data for the target country
2. Convert the occupation classifications to match the SOC system used by O*NET
   - Many countries have crosswalks between their national occupation classification and ISCO or SOC
3. Modify the data processing scripts to handle the country-specific data format
4. Run the complexity calculation and visualization scripts as described above

Key considerations for international extension:
- Ensure occupation classifications are compatible or properly mapped
- Account for currency differences in wage data
- Consider differences in labor market structures and reporting

## Verifying Correctness

To verify the correctness of the analysis:

1. Check intermediate outputs at each step
2. Compare complexity rankings with expected patterns (e.g., higher complexity for occupations requiring more education)
3. Validate employment numbers against official statistics
4. Cross-check wage data with other sources

## Common Issues and Solutions

- **Missing data**: Some occupations may have incomplete data in either BLS or O*NET. The scripts handle missing data by imputation or exclusion, depending on the context.
- **Classification changes**: The SOC system is updated periodically. Be aware of which version your data uses.
- **Memory issues**: Processing large datasets may require significant RAM. Consider using chunking for very large datasets.

## Additional Resources

- [BLS OEWS Technical Notes](https://www.bls.gov/oes/current/oes_tec.htm)
- [O*NET Content Model Reference](https://www.onetcenter.org/content.html)
- [SOC Classification System](https://www.bls.gov/soc/)
