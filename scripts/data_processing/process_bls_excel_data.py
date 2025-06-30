import pandas as pd
import numpy as np
import os
import re
import json
from collections import defaultdict

# Create output directories
os.makedirs('/home/ubuntu/research_project/data/processed/national', exist_ok=True)
os.makedirs('/home/ubuntu/research_project/data/processed/states', exist_ok=True)
os.makedirs('/home/ubuntu/research_project/data/processed/complexity', exist_ok=True)

print("Processing BLS Excel data files...")

# Define paths to the Excel files
national_file = '/home/ubuntu/research_project/data/raw/bls/national/oesm24nat/national_M2024_dl.xlsx'
state_file = '/home/ubuntu/research_project/data/raw/bls/states/oesm24st/state_M2024_dl.xlsx'

# Function to convert occupation code to SOC format
def to_soc_format(occ_code):
    # Check if already in SOC format (XX-XXXX)
    if isinstance(occ_code, str) and '-' in occ_code:
        return occ_code
    
    # Convert to string if numeric
    if not isinstance(occ_code, str):
        occ_code = str(int(occ_code)).zfill(6)
    
    # Convert to SOC format (XX-XXXX)
    if len(occ_code) == 6:
        return f"{occ_code[:2]}-{occ_code[2:6]}"
    
    return occ_code

# Define major group names based on SOC classification
major_group_names = {
    '11': 'Management',
    '13': 'Business & Financial Operations',
    '15': 'Computer & Mathematical',
    '17': 'Architecture & Engineering',
    '19': 'Life, Physical, & Social Science',
    '21': 'Community & Social Service',
    '23': 'Legal',
    '25': 'Educational Instruction & Library',
    '27': 'Arts, Design, Entertainment, Sports, & Media',
    '29': 'Healthcare Practitioners & Technical',
    '31': 'Healthcare Support',
    '33': 'Protective Service',
    '35': 'Food Preparation & Serving Related',
    '37': 'Building & Grounds Cleaning & Maintenance',
    '39': 'Personal Care & Service',
    '41': 'Sales & Related',
    '43': 'Office & Administrative Support',
    '45': 'Farming, Fishing, & Forestry',
    '47': 'Construction & Extraction',
    '49': 'Installation, Maintenance, & Repair',
    '51': 'Production',
    '53': 'Transportation & Material Moving',
    '55': 'Military Specific',
}

# Create uber categories (broader groupings)
uber_categories = {
    'Management & Business': ['11', '13'],
    'STEM': ['15', '17', '19'],
    'Education & Social Services': ['21', '23', '25', '27'],
    'Healthcare': ['29', '31'],
    'Service': ['33', '35', '37', '39'],
    'Sales & Office': ['41', '43'],
    'Natural Resources & Construction': ['45', '47'],
    'Production & Transportation': ['49', '51', '53'],
    'Military': ['55']
}

# Create reverse mapping from major group to uber category
major_to_uber = {}
for uber, majors in uber_categories.items():
    for major in majors:
        major_to_uber[major] = uber

# Process national data
print("\nProcessing national BLS data...")
try:
    # Read the Excel file
    national_df = pd.read_excel(national_file)
    print(f"National data shape: {national_df.shape}")
    print(f"National data columns: {national_df.columns.tolist()}")
    
    # Display first few rows to understand structure
    print("\nSample of national data:")
    print(national_df.head())
    
    # Check for occupation code column
    occ_code_col = None
    for col in national_df.columns:
        if 'occ' in col.lower() and 'code' in col.lower():
            occ_code_col = col
            break
    
    if not occ_code_col:
        # Try to identify by looking at values
        for col in national_df.columns:
            if national_df[col].dtype == object:
                sample_vals = national_df[col].dropna().head(10).tolist()
                if any('-' in str(val) for val in sample_vals):
                    occ_code_col = col
                    print(f"Identified occupation code column: {occ_code_col}")
                    break
    
    if occ_code_col:
        print(f"Using occupation code column: {occ_code_col}")
    else:
        print("Could not identify occupation code column. Using first column as default.")
        occ_code_col = national_df.columns[0]
    
    # Check for employment and wage columns
    emp_col = None
    wage_cols = []
    
    for col in national_df.columns:
        col_lower = col.lower()
        if 'employment' in col_lower or 'emp' in col_lower:
            emp_col = col
        if 'wage' in col_lower or 'salary' in col_lower or 'earn' in col_lower:
            wage_cols.append(col)
    
    print(f"Employment column: {emp_col}")
    print(f"Wage columns: {wage_cols}")
    
    # Create a standardized dataframe
    std_national_df = pd.DataFrame()
    
    # Add occupation code
    if occ_code_col:
        std_national_df['occupation_code'] = national_df[occ_code_col]
        std_national_df['soc_code'] = std_national_df['occupation_code'].apply(to_soc_format)
    
    # Add occupation title if available
    title_col = None
    for col in national_df.columns:
        if 'title' in col.lower() or 'name' in col.lower() or 'occupation' in col.lower():
            title_col = col
            break
    
    if title_col:
        std_national_df['occupation_title'] = national_df[title_col]
    else:
        std_national_df['occupation_title'] = std_national_df['soc_code'].apply(lambda x: f"Occupation {x}")
    
    # Add employment data
    if emp_col:
        std_national_df['employment'] = national_df[emp_col]
    
    # Add wage data
    for col in wage_cols:
        col_name = col.lower().replace(' ', '_')
        if 'annual' in col_name and 'mean' in col_name:
            std_national_df['annual_mean_wage'] = national_df[col]
        elif 'annual' in col_name and 'median' in col_name:
            std_national_df['annual_median_wage'] = national_df[col]
        elif 'annual' in col_name and ('10' in col_name or 'tenth' in col_name):
            std_national_df['annual_10pct_wage'] = national_df[col]
        elif 'annual' in col_name and ('90' in col_name or 'ninetieth' in col_name):
            std_national_df['annual_90pct_wage'] = national_df[col]
        else:
            std_national_df[col_name] = national_df[col]
    
    # Add major group information
    std_national_df['major_group'] = std_national_df['soc_code'].apply(lambda x: x.split('-')[0] if isinstance(x, str) and '-' in x else '')
    std_national_df['major_group_name'] = std_national_df['major_group'].map(major_group_names)
    std_national_df['is_major_group'] = std_national_df['soc_code'].apply(lambda x: isinstance(x, str) and x.endswith('-0000'))
    
    # Add uber category
    std_national_df['uber_category'] = std_national_df['major_group'].map(
        lambda x: major_to_uber.get(x, 'Other') if pd.notna(x) else None
    )
    
    # Save the standardized national data
    std_national_df.to_csv('/home/ubuntu/research_project/data/processed/national/bls_national_data.csv', index=False)
    print(f"Saved standardized national data with {len(std_national_df)} rows")
    
    # Print summary statistics
    print("\nNational data summary:")
    print(f"Total occupations: {len(std_national_df)}")
    print(f"Major groups: {std_national_df['major_group'].nunique()}")
    print(f"Uber categories: {std_national_df['uber_category'].nunique()}")
    
except Exception as e:
    print(f"Error processing national data: {str(e)}")
    import traceback
    print(traceback.format_exc())

# Process state data
print("\nProcessing state BLS data...")
try:
    # Read the Excel file
    state_df = pd.read_excel(state_file)
    print(f"State data shape: {state_df.shape}")
    print(f"State data columns: {state_df.columns.tolist()}")
    
    # Display first few rows to understand structure
    print("\nSample of state data:")
    print(state_df.head())
    
    # Check for state, occupation code columns
    state_col = None
    occ_code_col = None
    
    for col in state_df.columns:
        col_lower = col.lower()
        if 'state' in col_lower:
            state_col = col
        if 'occ' in col_lower and 'code' in col_lower:
            occ_code_col = col
    
    if not occ_code_col:
        # Try to identify by looking at values
        for col in state_df.columns:
            if state_df[col].dtype == object:
                sample_vals = state_df[col].dropna().head(10).tolist()
                if any('-' in str(val) for val in sample_vals):
                    occ_code_col = col
                    print(f"Identified occupation code column: {occ_code_col}")
                    break
    
    if occ_code_col:
        print(f"Using occupation code column: {occ_code_col}")
    else:
        print("Could not identify occupation code column. Using first column as default.")
        occ_code_col = state_df.columns[0]
    
    if state_col:
        print(f"Using state column: {state_col}")
    else:
        print("Could not identify state column.")
    
    # Check for employment and wage columns
    emp_col = None
    wage_cols = []
    
    for col in state_df.columns:
        col_lower = col.lower()
        if 'employment' in col_lower or 'emp' in col_lower:
            emp_col = col
        if 'wage' in col_lower or 'salary' in col_lower or 'earn' in col_lower:
            wage_cols.append(col)
    
    print(f"Employment column: {emp_col}")
    print(f"Wage columns: {wage_cols}")
    
    # Create a standardized dataframe
    std_state_df = pd.DataFrame()
    
    # Add state information if available
    if state_col:
        std_state_df['state'] = state_df[state_col]
    
    # Add occupation code
    if occ_code_col:
        std_state_df['occupation_code'] = state_df[occ_code_col]
        std_state_df['soc_code'] = std_state_df['occupation_code'].apply(to_soc_format)
    
    # Add occupation title if available
    title_col = None
    for col in state_df.columns:
        if 'title' in col.lower() or 'name' in col.lower() or 'occupation' in col.lower():
            title_col = col
            break
    
    if title_col:
        std_state_df['occupation_title'] = state_df[title_col]
    else:
        std_state_df['occupation_title'] = std_state_df['soc_code'].apply(lambda x: f"Occupation {x}")
    
    # Add employment data
    if emp_col:
        std_state_df['employment'] = state_df[emp_col]
    
    # Add wage data
    for col in wage_cols:
        col_name = col.lower().replace(' ', '_')
        if 'annual' in col_name and 'mean' in col_name:
            std_state_df['annual_mean_wage'] = state_df[col]
        elif 'annual' in col_name and 'median' in col_name:
            std_state_df['annual_median_wage'] = state_df[col]
        elif 'annual' in col_name and ('10' in col_name or 'tenth' in col_name):
            std_state_df['annual_10pct_wage'] = state_df[col]
        elif 'annual' in col_name and ('90' in col_name or 'ninetieth' in col_name):
            std_state_df['annual_90pct_wage'] = state_df[col]
        else:
            std_state_df[col_name] = state_df[col]
    
    # Add major group information
    std_state_df['major_group'] = std_state_df['soc_code'].apply(lambda x: x.split('-')[0] if isinstance(x, str) and '-' in x else '')
    std_state_df['major_group_name'] = std_state_df['major_group'].map(major_group_names)
    std_state_df['is_major_group'] = std_state_df['soc_code'].apply(lambda x: isinstance(x, str) and x.endswith('-0000'))
    
    # Add uber category
    std_state_df['uber_category'] = std_state_df['major_group'].map(
        lambda x: major_to_uber.get(x, 'Other') if pd.notna(x) else None
    )
    
    # Save the standardized state data
    std_state_df.to_csv('/home/ubuntu/research_project/data/processed/states/bls_state_data.csv', index=False)
    print(f"Saved standardized state data with {len(std_state_df)} rows")
    
    # Print summary statistics
    print("\nState data summary:")
    print(f"Total records: {len(std_state_df)}")
    if state_col:
        print(f"States: {std_state_df['state'].nunique()}")
    print(f"Occupations per state: {len(std_state_df) / std_state_df['state'].nunique() if state_col else 'N/A'}")
    print(f"Major groups: {std_state_df['major_group'].nunique()}")
    print(f"Uber categories: {std_state_df['uber_category'].nunique()}")
    
except Exception as e:
    print(f"Error processing state data: {str(e)}")
    import traceback
    print(traceback.format_exc())

# Create Excel file with multiple sheets
try:
    with pd.ExcelWriter('/home/ubuntu/research_project/data/processed/bls_labor_market_data.xlsx') as writer:
        if 'std_national_df' in locals() and not std_national_df.empty:
            std_national_df.to_excel(writer, sheet_name='National', index=False)
        if 'std_state_df' in locals() and not std_state_df.empty:
            std_state_df.to_excel(writer, sheet_name='States', index=False)
    
    print("\nSaved comprehensive BLS labor market data Excel file")
except Exception as e:
    print(f"Error saving Excel file: {str(e)}")
    import traceback
    print(traceback.format_exc())

print("\nBLS data processing complete!")
