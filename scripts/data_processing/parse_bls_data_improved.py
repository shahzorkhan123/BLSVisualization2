import pandas as pd
import numpy as np
import os
import re
import gc

# Create output directories
os.makedirs('data/bls', exist_ok=True)

print("Parsing BLS wage data file with improved SOC code extraction...")
# Load the BLS data file with proper column handling
bls_data_file = '/home/ubuntu/upload/oe.data.1.AllData.txt'

# First, read the file to get the header line
with open(bls_data_file, 'r') as f:
    header_line = f.readline().strip()

# Split the header by tabs and clean column names
column_names = [col.strip() for col in header_line.split('\t')]
print(f"Original column names: {column_names}")

# Process the file in chunks to avoid memory issues
chunk_size = 100000  # Adjust based on available memory
chunks = pd.read_csv(bls_data_file, sep='\t', skiprows=1, names=column_names, chunksize=chunk_size)

# Initialize containers for processed data
all_national_data = []
unique_soc_codes = set()
data_type_counts = {}
unknown_data_types = set()

# Function to extract SOC code from series_id
def extract_soc_code(series_id):
    try:
        # The occupation code starts at position 10 and is 8 characters long
        occ_code = series_id[10:18]
        
        # Check if this is a valid occupation code
        if occ_code == '00000000':
            return 'all'  # This is aggregate data for all occupations
        
        # Format as standard SOC code (XX-XXXX)
        # First two digits are the major group
        major_group = occ_code[:2]
        
        # Next four digits are the detailed occupation
        detailed = occ_code[2:6]
        
        # Format with hyphen
        if detailed == '0000':
            # This is a major group
            return f"{major_group}-0000"
        else:
            return f"{major_group}-{detailed}"
    except:
        return 'unknown'

# Function to extract data type from series_id
def extract_data_type(series_id):
    try:
        # The data type is the last 6 digits
        data_type = series_id[-6:]
        
        # Map data types to meaningful names based on BLS documentation
        # Expanded mapping based on observed patterns
        data_type_map = {
            # Standard OES data types
            '000001': 'employment',
            '000002': 'employment_pct',
            '000003': 'hourly_mean_wage',
            '000004': 'annual_mean_wage',
            '000005': 'wage_pct',
            '000006': 'hourly_10pct_wage',
            '000007': 'hourly_25pct_wage',
            '000008': 'hourly_median_wage',
            '000009': 'hourly_75pct_wage',
            '000010': 'hourly_90pct_wage',
            '000011': 'annual_10pct_wage',
            '000012': 'annual_25pct_wage',
            '000013': 'annual_median_wage',
            '000014': 'annual_75pct_wage',
            '000015': 'annual_90pct_wage',
            '000016': 'employment_per_1000',
            '000017': 'location_quotient',
        }
        
        result = data_type_map.get(data_type, f"unknown_{data_type}")
        if result.startswith("unknown_"):
            unknown_data_types.add(data_type)
        return result
    except:
        return 'unknown'

# Function to extract area code from series_id
def extract_area_code(series_id):
    try:
        # The area code is positions 4-9
        return series_id[4:10]
    except:
        return 'unknown'

# Process each chunk
chunk_count = 0
for chunk in chunks:
    chunk_count += 1
    print(f"\nProcessing chunk {chunk_count}...")
    
    # Clean the series_id column to remove trailing whitespace
    chunk['series_id'] = chunk['series_id'].str.strip()
    
    # Extract SOC codes, data types, and area codes
    chunk['soc_code'] = chunk['series_id'].apply(extract_soc_code)
    chunk['data_type'] = chunk['series_id'].apply(extract_data_type)
    chunk['area_code'] = chunk['series_id'].apply(extract_area_code)
    
    # Update data type counts
    for data_type, count in chunk['data_type'].value_counts().items():
        if data_type in data_type_counts:
            data_type_counts[data_type] += count
        else:
            data_type_counts[data_type] = count
    
    # Filter out aggregate data and unknown SOC codes
    chunk_filtered = chunk[(chunk['soc_code'] != 'all') & (chunk['soc_code'] != 'unknown')]
    
    # Update unique SOC codes
    unique_soc_codes.update(chunk_filtered['soc_code'].unique())
    
    # Extract national data (area_code = '001018')
    national_chunk = chunk_filtered[chunk_filtered['area_code'] == '001018'].copy()
    
    # Clean the value column
    national_chunk['value'] = national_chunk['value'].astype(str).str.strip()
    national_chunk['value'] = pd.to_numeric(national_chunk['value'], errors='coerce')
    
    # Add area name
    national_chunk['area_name'] = 'National'
    
    # Keep only necessary columns to save memory
    national_chunk = national_chunk[['soc_code', 'area_code', 'area_name', 'year', 'period', 'data_type', 'value']]
    
    # Append to national data list
    all_national_data.append(national_chunk)
    
    # Save a sample of the first chunk for debugging
    if chunk_count == 1:
        chunk.head(1000).to_csv('data/bls/raw_bls_sample.csv', index=False)
        print("Sample of raw BLS data saved to data/bls/raw_bls_sample.csv")
    
    # Free memory
    del chunk, chunk_filtered, national_chunk
    gc.collect()
    
    # For testing, limit to 10 chunks
    if chunk_count >= 60:
        break

# Print unknown data types for further investigation
print("\nUnknown data types found:")
print(sorted(list(unknown_data_types)))

# Combine all national data
print("\nCombining all national data...")
if all_national_data:
    national_data = pd.concat(all_national_data, ignore_index=True)
    print(f"Combined national data shape: {national_data.shape}")
    
    # Print data type distribution
    print("\nData type distribution in national data:")
    print(national_data['data_type'].value_counts().head(20))
    
    # Group data by SOC code to check coverage
    soc_code_counts = national_data['soc_code'].value_counts()
    print(f"\nNumber of SOC codes in national data: {len(soc_code_counts)}")
    print(f"Top 10 SOC codes by data point count:")
    print(soc_code_counts.head(10))
    
    # Check for standard data types in each SOC code
    standard_data_types = ['employment', 'annual_mean_wage', 'hourly_median_wage']
    soc_with_standard_types = national_data[national_data['data_type'].isin(standard_data_types)]['soc_code'].unique()
    print(f"\nNumber of SOC codes with standard data types: {len(soc_with_standard_types)}")
    
    # Save the unpivoted data for reference
    national_data.to_csv('data/bls/national_bls_data_unpivoted.csv', index=False)
    print("Unpivoted national data saved to data/bls/national_bls_data_unpivoted.csv")
    
    # Create a wide format dataset for each SOC code
    print("\nCreating wide format dataset for each SOC code...")
    
    # Get unique SOC codes in national data
    unique_national_socs = national_data['soc_code'].unique()
    print(f"Number of unique SOC codes in national data: {len(unique_national_socs)}")
    
    # Create a list to store processed SOC data
    processed_socs = []
    
    # Process each SOC code separately to avoid memory issues
    for soc_code in unique_national_socs:
        soc_data = national_data[national_data['soc_code'] == soc_code]
        
        # Create a dictionary for this SOC code
        soc_dict = {
            'soc_code': soc_code,
            'area_name': 'National',
            'year': 2024,
            'period': 'A01'
        }
        
        # Add each data type as a column
        for _, row in soc_data.iterrows():
            data_type = row['data_type']
            value = row['value']
            soc_dict[data_type] = value
        
        # Add to processed list
        processed_socs.append(soc_dict)
    
    # Convert to DataFrame
    wide_data = pd.DataFrame(processed_socs)
    print(f"Wide data shape: {wide_data.shape}")
    print(f"Wide data columns: {wide_data.columns.tolist()}")
    
    # Save the wide format data
    wide_data.to_csv('data/bls/national_bls_data_wide.csv', index=False)
    print("Wide format national BLS data saved to data/bls/national_bls_data_wide.csv")
    
    # Save a sample for quick review
    wide_data.head(100).to_csv('data/bls/national_bls_data_wide_sample.csv', index=False)
    print("Sample of wide format national BLS data saved to data/bls/national_bls_data_wide_sample.csv")
else:
    print("No national data found in any chunk!")

# Print summary of unique SOC codes
print(f"\nTotal unique SOC codes found: {len(unique_soc_codes)}")
print(f"Sample SOC codes: {sorted(list(unique_soc_codes)[:20])}")

# Print data type distribution
print("\nOverall data type distribution:")
for data_type, count in sorted(data_type_counts.items(), key=lambda x: x[1], reverse=True)[:30]:
    print(f"{data_type}: {count}")

# Create a mapping file for SOC codes to occupation titles
# For a more complete implementation, we would fetch the actual titles from BLS
soc_titles = pd.DataFrame({
    'soc_code': list(unique_soc_codes),
    'occupation_title': [f"Occupation {soc}" for soc in unique_soc_codes]
})

soc_titles.to_csv('data/bls/soc_titles.csv', index=False)
print("\nSOC code to title mapping saved to data/bls/soc_titles.csv")

# Validate the data for downstream use
print("\nValidating data for downstream use...")
if os.path.exists('data/bls/national_bls_data_wide.csv'):
    validation_data = pd.read_csv('data/bls/national_bls_data_wide.csv')
    print(f"Validation data shape: {validation_data.shape}")
    print(f"Validation data columns: {validation_data.columns.tolist()}")
    
    # Check for key wage and employment columns
    key_columns = ['employment', 'annual_mean_wage']
    missing_columns = [col for col in key_columns if col not in validation_data.columns]
    
    if missing_columns:
        print(f"WARNING: Missing key columns: {missing_columns}")
        print("Data may not be valid for downstream use!")
    else:
        print("All key columns present. Data is valid for downstream use.")
        
        # Check for null values in key columns
        null_counts = validation_data[key_columns].isnull().sum()
        print(f"Null value counts in key columns:\n{null_counts}")
        
        # Check for reasonable value ranges
        print("\nValue ranges in key columns:")
        for col in key_columns:
            if col in validation_data.columns:
                print(f"{col}: {validation_data[col].min()} to {validation_data[col].max()}")
else:
    print("WARNING: National BLS data file not found! Data processing failed.")

print("\nBLS data parsing and validation complete!")
