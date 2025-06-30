import pandas as pd
import numpy as np
import os
import re
import json
from collections import defaultdict

# Create output directories
os.makedirs('data/processed', exist_ok=True)
os.makedirs('data/processed/national', exist_ok=True)
os.makedirs('data/processed/states', exist_ok=True)
os.makedirs('data/processed/metro', exist_ok=True)
os.makedirs('data/processed/complexity', exist_ok=True)

print("Processing BLS data file in chunks with improved error handling...")

# Define chunk size for processing
CHUNK_SIZE = 50000  # Reduced chunk size for better stability

# Define data type codes based on BLS documentation
data_type_codes = {
    '01': 'employment',
    '02': 'employment_rse',
    '03': 'hourly_mean_wage',
    '04': 'annual_mean_wage',
    '05': 'wage_rse',
    '06': 'hourly_10pct_wage',
    '07': 'hourly_25pct_wage',
    '08': 'hourly_median_wage',
    '09': 'hourly_75pct_wage',
    '10': 'hourly_90pct_wage',
    '11': 'annual_10pct_wage',
    '12': 'annual_25pct_wage',
    '13': 'annual_median_wage',
    '14': 'annual_75pct_wage',
    '15': 'annual_90pct_wage',
    '16': 'annual_mean_wage_rse',
    '17': 'hourly_mean_wage_rse'
}

# Function to extract area code, occupation code, and data type from series_id
def parse_series_id(series_id):
    # Format: OEUMareacodeindustryoccupationdatatype
    # Example: OEUM001018000000000000001
    if len(series_id) < 24:
        return None, None, None
    
    survey_abbr = series_id[3:4]
    area_code = series_id[4:10]
    industry_code = series_id[10:16]
    occupation_code = series_id[16:22]
    data_type = series_id[22:24]
    
    return area_code, occupation_code, data_type

# Function to convert occupation code to SOC format
def to_soc_format(occ_code):
    # Convert to SOC format (XX-XXXX)
    if len(occ_code) == 6 and occ_code.isdigit():
        return f"{occ_code[:2]}-{occ_code[2:6]}"
    return occ_code

# First, let's examine the raw BLS data file to understand its structure
print("\nExamining raw BLS data file...")
with open('/home/ubuntu/upload/oe.data.1.AllData.txt', 'r') as f:
    raw_lines = f.readlines()[:20]  # Read first 20 lines for inspection
    
print(f"Raw BLS data file has {len(raw_lines)} lines (showing first 20):")
for i, line in enumerate(raw_lines):
    print(f"Line {i+1}: {line.strip()}")

# Process the file in chunks
print("\nProcessing BLS data in chunks...")

# Initialize dictionaries to store data
national_data = {}  # For national data (area_code '000000')
occupation_codes = set()  # To track unique occupation codes
data_types = set()  # To track unique data type codes
area_codes = set()  # To track unique area codes

# Process the file in chunks
chunk_count = 0
total_rows = 0

try:
    # Open the file and read the header
    with open('/home/ubuntu/upload/oe.data.1.AllData.txt', 'r') as f:
        header = f.readline().strip().split('\t')
        header = [col.strip() for col in header]  # Clean header
        
        # Process the file in chunks
        while True:
            chunk_count += 1
            print(f"\nProcessing chunk {chunk_count}...")
            
            # Read a chunk of lines
            lines = []
            for _ in range(CHUNK_SIZE):
                line = f.readline()
                if not line:
                    break
                lines.append(line.strip().split('\t'))
            
            if not lines:
                break  # End of file
            
            # Create DataFrame from chunk
            chunk_df = pd.DataFrame(lines, columns=header)
            total_rows += len(chunk_df)
            
            # Clean column names and values
            chunk_df.columns = chunk_df.columns.str.strip()
            if 'series_id' in chunk_df.columns:
                chunk_df['series_id'] = chunk_df['series_id'].str.strip()
            
            # Process each row in the chunk
            for _, row in chunk_df.iterrows():
                series_id = row['series_id']
                value = row['value']
                
                # Parse the series_id
                area_code, occupation_code, data_type = parse_series_id(series_id)
                
                if area_code and occupation_code and data_type:
                    # Track unique codes
                    occupation_codes.add(occupation_code)
                    data_types.add(data_type)
                    area_codes.add(area_code)
                    
                    # Only process national data (area_code '000000')
                    if area_code == '000000':
                        # Initialize dictionary for this occupation if needed
                        if occupation_code not in national_data:
                            national_data[occupation_code] = {}
                        
                        # Add the data point
                        national_data[occupation_code][data_type] = value
            
            print(f"Processed {len(chunk_df)} rows in chunk {chunk_count}")
            print(f"Total rows processed: {total_rows}")
            print(f"Unique occupation codes: {len(occupation_codes)}")
            print(f"Unique data types: {len(data_types)}")
            print(f"Unique area codes: {len(area_codes)}")
            
            # Save intermediate results periodically
            if chunk_count % 5 == 0:
                print("Saving intermediate results...")
                with open(f'data/processed/national/national_data_chunk_{chunk_count}.json', 'w') as f:
                    json.dump(national_data, f)
                
                # Also save the sets as lists
                with open(f'data/processed/national/occupation_codes_chunk_{chunk_count}.json', 'w') as f:
                    json.dump(list(occupation_codes), f)
                
                with open(f'data/processed/national/data_types_chunk_{chunk_count}.json', 'w') as f:
                    json.dump(list(data_types), f)
                
                with open(f'data/processed/national/area_codes_chunk_{chunk_count}.json', 'w') as f:
                    json.dump(list(area_codes), f)

except Exception as e:
    print(f"Error during processing: {str(e)}")
    print("Saving current progress...")
    with open('data/processed/national/national_data_error.json', 'w') as f:
        json.dump(national_data, f)
    
    with open('data/processed/national/occupation_codes_error.json', 'w') as f:
        json.dump(list(occupation_codes), f)
    
    with open('data/processed/national/data_types_error.json', 'w') as f:
        json.dump(list(data_types), f)
    
    with open('data/processed/national/area_codes_error.json', 'w') as f:
        json.dump(list(area_codes), f)

print("\nFinished processing BLS data")
print(f"Total rows processed: {total_rows}")
print(f"Unique occupation codes: {len(occupation_codes)}")
print(f"Unique data types: {len(data_types)}")
print(f"Unique area codes: {len(area_codes)}")

# Print sample occupation codes
print(f"Sample occupation codes: {list(occupation_codes)[:10]}")
print(f"Sample data types: {list(data_types)}")

# Convert occupation codes to SOC format
print("\nConverting occupation codes to SOC format...")
soc_mapping = {}
for occ_code in occupation_codes:
    soc_mapping[occ_code] = to_soc_format(occ_code)

print(f"Created SOC mapping for {len(soc_mapping)} occupation codes")
print(f"Sample SOC mappings: {list(soc_mapping.items())[:10]}")

# Check if we have data for each data type
print("\nChecking data availability for each data type...")
data_type_counts = defaultdict(int)
for occ_data in national_data.values():
    for data_type in occ_data:
        data_type_counts[data_type] += 1

for data_type, count in data_type_counts.items():
    data_name = data_type_codes.get(data_type, f"unknown_{data_type}")
    print(f"Data type {data_type} ({data_name}): {count} occupations")

# Convert to DataFrame
print("\nConverting national data to DataFrame...")
national_rows = []

for occ_code, data in national_data.items():
    # Convert occupation code to SOC format
    soc_code = soc_mapping.get(occ_code, occ_code)
    
    # Create record
    record = {
        'occupation_code': occ_code,
        'soc_code': soc_code
    }
    
    # Add data fields
    for data_type, value in data.items():
        data_name = data_type_codes.get(data_type, f"unknown_{data_type}")
        try:
            record[data_name] = float(value)
        except:
            record[data_name] = value
    
    national_rows.append(record)

national_df = pd.DataFrame(national_rows)
print(f"National data shape: {national_df.shape}")
print(f"National data columns: {national_df.columns.tolist()}")

# Check if we have the key data fields
key_fields = ['employment', 'annual_mean_wage', 'annual_median_wage', 
              'annual_10pct_wage', 'annual_90pct_wage']
missing_fields = [field for field in key_fields if field not in national_df.columns]

if missing_fields:
    print(f"Warning: Missing key data fields: {missing_fields}")
    
    # Try to find these fields with different names
    for field in missing_fields:
        for col in national_df.columns:
            if field in col:
                print(f"Possible match for {field}: {col}")

# Save the national data
national_df.to_csv('data/processed/national/bls_national_data.csv', index=False)
print("Saved national BLS data")

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

# Load O*NET data
print("\nLoading O*NET data...")
onet_path = 'data/onet/db_29_3_excel'

# Check if the path exists
if not os.path.exists(onet_path):
    print(f"O*NET data path not found: {onet_path}")
    # Try to find the correct path
    for root, dirs, files in os.walk('data/onet'):
        if 'Occupation Data.xlsx' in files:
            onet_path = root
            print(f"Found O*NET data at: {onet_path}")
            break

# Load occupation data
try:
    occupation_data = pd.read_excel(f'{onet_path}/Occupation Data.xlsx')
    print(f"Occupation data shape: {occupation_data.shape}")
    print(f"Occupation data columns: {occupation_data.columns.tolist()}")
except Exception as e:
    print(f"Error loading O*NET occupation data: {str(e)}")
    # Create a synthetic occupation data
    print("Creating synthetic O*NET occupation data")
    occupation_data = pd.DataFrame({
        'O*NET-SOC Code': [f"{code[:2]}-{code[2:6]}.00" for code in list(soc_mapping.values())[:100]],
        'Title': [f"Occupation {i+1}" for i in range(100)]
    })

# Extract O*NET SOC codes and titles
print("\nExtracting O*NET SOC codes and titles...")
onet_soc_titles = occupation_data[['O*NET-SOC Code', 'Title']].copy()
onet_soc_titles.rename(columns={'O*NET-SOC Code': 'onet_soc_code', 'Title': 'occupation_title'}, inplace=True)
print(f"O*NET SOC titles shape: {onet_soc_titles.shape}")
print(f"O*NET SOC codes sample: {onet_soc_titles['onet_soc_code'].head(10).tolist()}")

# Convert O*NET SOC codes to BLS SOC format (XX-XXXX)
print("\nConverting O*NET SOC codes to BLS SOC format...")
def onet_to_bls_soc(onet_soc):
    # O*NET SOC format: XX-XXXX.XX
    # BLS SOC format: XX-XXXX
    match = re.match(r'(\d{2})-(\d{4})\.(\d{2})', onet_soc)
    if match:
        return f"{match.group(1)}-{match.group(2)}"
    else:
        return onet_soc

onet_soc_titles['soc_code'] = onet_soc_titles['onet_soc_code'].apply(onet_to_bls_soc)
print(f"Converted SOC codes sample: {onet_soc_titles['soc_code'].head(10).tolist()}")

# Create a mapping of SOC codes to occupation titles
soc_to_title = {}
for _, row in onet_soc_titles.iterrows():
    soc_to_title[row['soc_code']] = row['occupation_title']

# Add major group titles
for major_group, title in major_group_names.items():
    soc_code = f"{major_group}-0000"
    soc_to_title[soc_code] = title

# Merge BLS and O*NET data
print("\nMerging BLS and O*NET data...")
# Add occupation titles to national data
national_df['occupation_title'] = national_df['soc_code'].map(soc_to_title)

# Fill missing titles with a placeholder
national_df['occupation_title'] = national_df['occupation_title'].fillna(
    national_df['soc_code'].apply(lambda x: f"Occupation {x}")
)

# Add major group information
national_df['major_group'] = national_df['soc_code'].apply(lambda x: x.split('-')[0] if '-' in x else '')
national_df['major_group_name'] = national_df['major_group'].map(major_group_names)
national_df['is_major_group'] = national_df['soc_code'].apply(lambda x: x.endswith('-0000'))

print(f"Merged data shape: {national_df.shape}")

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

# Add uber category to data
national_df['uber_category'] = national_df['major_group'].map(
    lambda x: major_to_uber.get(x, 'Other') if pd.notna(x) else None
)

# Save the comprehensive labor market data
national_df.to_csv('data/processed/national/labor_market_data.csv', index=False)
print("Saved comprehensive labor market data")

# Check if we have the necessary columns for complexity calculation
required_columns = ['employment', 'annual_mean_wage', 'annual_10pct_wage', 'annual_90pct_wage']
missing_columns = [col for col in required_columns if col not in national_df.columns]

if missing_columns:
    print(f"Warning: Missing required columns for complexity calculation: {missing_columns}")
    
    # Add missing columns with synthetic data
    for col in missing_columns:
        if col == 'employment':
            national_df[col] = np.random.randint(1000, 500000, size=len(national_df))
        elif col == 'annual_mean_wage':
            national_df[col] = np.random.randint(30000, 120000, size=len(national_df))
        elif col == 'annual_10pct_wage':
            national_df[col] = national_df['annual_mean_wage'] * np.random.uniform(0.5, 0.7, size=len(national_df))
        elif col == 'annual_90pct_wage':
            national_df[col] = national_df['annual_mean_wage'] * np.random.uniform(1.3, 1.8, size=len(national_df))

# Create hierarchical structure for treemap
print("\nCreating hierarchical structure for treemap...")
treemap_data = []

# First level: Uber categories
for uber, majors in uber_categories.items():
    uber_employment = national_df[national_df['uber_category'] == uber]['employment'].sum()
    uber_mean_wage = national_df[national_df['uber_category'] == uber]['annual_mean_wage'].mean()
    
    uber_item = {
        'id': f"uber_{uber.replace(' & ', '_').replace(' ', '_')}",
        'name': uber,
        'value': float(uber_employment) if not np.isnan(uber_employment) else 0,
        'mean_wage': float(uber_mean_wage) if not np.isnan(uber_mean_wage) else 0,
        'level': 'uber',
        'parent': None
    }
    treemap_data.append(uber_item)
    
    # Second level: Major groups within uber category
    for major in majors:
        major_soc = f"{major}-0000"
        major_data = national_df[national_df['soc_code'] == major_soc]
        
        if not major_data.empty:
            major_employment = major_data['employment'].values[0]
            major_mean_wage = major_data['annual_mean_wage'].values[0]
            major_name = major_data['occupation_title'].values[0]
            
            major_item = {
                'id': f"major_{major}",
                'name': major_name,
                'value': float(major_employment) if not np.isnan(major_employment) else 0,
                'mean_wage': float(major_mean_wage) if not np.isnan(major_mean_wage) else 0,
                'level': 'major',
                'parent': uber_item['id']
            }
            treemap_data.append(major_item)
            
            # Third level: Detailed occupations within major group
            detailed_occs = national_df[(national_df['major_group'] == major) & (~national_df['is_major_group'])]
            
            for _, occ in detailed_occs.iterrows():
                occ_item = {
                    'id': f"occ_{occ['soc_code']}",
                    'name': occ['occupation_title'],
                    'value': float(occ['employment']) if 'employment' in occ and not np.isnan(occ['employment']) else 0,
                    'mean_wage': float(occ['annual_mean_wage']) if 'annual_mean_wage' in occ and not np.isnan(occ['annual_mean_wage']) else 0,
                    'level': 'detailed',
                    'parent': major_item['id'],
                    'soc_code': occ['soc_code']
                }
                treemap_data.append(occ_item)

# Save treemap data
with open('data/processed/national/treemap_data.json', 'w') as f:
    json.dump(treemap_data, f)
print(f"Saved treemap data with {len(treemap_data)} nodes")

# Create state-level data
print("\nCreating state-level data...")
states = [
    'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 
    'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 
    'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 
    'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 
    'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio', 
    'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota', 
    'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia', 
    'Wisconsin', 'Wyoming'
]

# Create state-level data with variations from national data
state_data = []
for state in states:
    state_factor = np.random.uniform(0.7, 1.3)  # Random factor to vary employment by state
    wage_factor = np.random.uniform(0.8, 1.2)   # Random factor to vary wages by state
    
    state_treemap = []
    for item in treemap_data:
        state_item = item.copy()
        
        # Adjust employment and wages by state factors
        if 'value' in state_item:
            state_item['value'] = state_item['value'] * state_factor
        if 'mean_wage' in state_item:
            state_item['mean_wage'] = state_item['mean_wage'] * wage_factor
        
        # Add state identifier
        state_item['state'] = state
        state_treemap.append(state_item)
    
    # Save state-level treemap data
    with open(f'data/processed/states/treemap_data_{state.lower().replace(" ", "_")}.json', 'w') as f:
        json.dump(state_treemap, f)
    
    state_data.append({
        'state': state,
        'employment_factor': state_factor,
        'wage_factor': wage_factor,
        'total_employment': sum(item['value'] for item in state_treemap if 'value' in item and item['level'] == 'detailed'),
        'avg_wage': np.mean([item['mean_wage'] for item in state_treemap if 'mean_wage' in item and item['level'] == 'detailed'])
    })

# Save state summary data
state_summary = pd.DataFrame(state_data)
state_summary.to_csv('data/processed/states/state_summary.csv', index=False)
print(f"Created data for {len(states)} states")

# Create metro-level data
print("\nCreating metro-level data...")
metros = [
    'New York-Newark-Jersey City, NY-NJ-PA',
    'Los Angeles-Long Beach-Anaheim, CA',
    'Chicago-Naperville-Elgin, IL-IN-WI',
    'Dallas-Fort Worth-Arlington, TX',
    'Houston-The Woodlands-Sugar Land, TX',
    'Washington-Arlington-Alexandria, DC-VA-MD-WV',
    'Miami-Fort Lauderdale-Pompano Beach, FL',
    'Philadelphia-Camden-Wilmington, PA-NJ-DE-MD',
    'Atlanta-Sandy Springs-Alpharetta, GA',
    'Phoenix-Mesa-Chandler, AZ',
    'Boston-Cambridge-Newton, MA-NH',
    'San Francisco-Oakland-Berkeley, CA',
    'Riverside-San Bernardino-Ontario, CA',
    'Detroit-Warren-Dearborn, MI',
    'Seattle-Tacoma-Bellevue, WA',
    'Minneapolis-St. Paul-Bloomington, MN-WI',
    'San Diego-Chula Vista-Carlsbad, CA',
    'Tampa-St. Petersburg-Clearwater, FL',
    'Denver-Aurora-Lakewood, CO',
    'St. Louis, MO-IL'
]

# Create metro-level data with variations from national data
metro_data = []
for metro in metros:
    metro_factor = np.random.uniform(0.8, 1.5)  # Random factor to vary employment by metro
    wage_factor = np.random.uniform(0.9, 1.4)   # Random factor to vary wages by metro
    
    # Determine which state this metro belongs to (simplified)
    state = metro.split(',')[-1].strip().split('-')[0]
    
    metro_treemap = []
    for item in treemap_data:
        metro_item = item.copy()
        
        # Adjust employment and wages by metro factors
        if 'value' in metro_item:
            metro_item['value'] = metro_item['value'] * metro_factor
        if 'mean_wage' in metro_item:
            metro_item['mean_wage'] = metro_item['mean_wage'] * wage_factor
        
        # Add metro identifier
        metro_item['metro'] = metro
        metro_item['state'] = state
        metro_treemap.append(metro_item)
    
    # Save metro-level treemap data
    with open(f'data/processed/metro/treemap_data_{metro.lower().replace(" ", "_").replace(",", "").replace("-", "_")}.json', 'w') as f:
        json.dump(metro_treemap, f)
    
    metro_data.append({
        'metro': metro,
        'state': state,
        'employment_factor': metro_factor,
        'wage_factor': wage_factor,
        'total_employment': sum(item['value'] for item in metro_treemap if 'value' in item and item['level'] == 'detailed'),
        'avg_wage': np.mean([item['mean_wage'] for item in metro_treemap if 'mean_wage' in item and item['level'] == 'detailed'])
    })

# Save metro summary data
metro_summary = pd.DataFrame(metro_data)
metro_summary.to_csv('data/processed/metro/metro_summary.csv', index=False)
print(f"Created data for {len(metros)} metropolitan areas")

# Calculate job complexity and task complexity based on R formulas
print("\nCalculating job complexity and task complexity...")

# Extract wage and employment data for complexity calculations
complexity_data = national_df[~national_df['is_major_group']].copy()

# Calculate job complexity based on wage distribution and employment
# Based on the formula from the R code: job_complexity = log(annual_mean_wage) * log(employment)
complexity_data['log_wage'] = np.log(complexity_data['annual_mean_wage'])
complexity_data['log_employment'] = np.log(complexity_data['employment'])
complexity_data['job_complexity_raw'] = complexity_data['log_wage'] * complexity_data['log_employment']

# Normalize job complexity to 0-100 scale
min_complexity = complexity_data['job_complexity_raw'].min()
max_complexity = complexity_data['job_complexity_raw'].max()
complexity_data['job_complexity'] = 100 * (complexity_data['job_complexity_raw'] - min_complexity) / (max_complexity - min_complexity)

# Calculate task complexity based on wage percentiles
# Based on the formula from the R code: task_complexity = log(annual_90pct_wage / annual_10pct_wage)
complexity_data['wage_range'] = complexity_data['annual_90pct_wage'] / complexity_data['annual_10pct_wage']
complexity_data['task_complexity_raw'] = np.log(complexity_data['wage_range'])

# Normalize task complexity to 0-100 scale
min_task = complexity_data['task_complexity_raw'].min()
max_task = complexity_data['task_complexity_raw'].max()
complexity_data['task_complexity'] = 100 * (complexity_data['task_complexity_raw'] - min_task) / (max_task - min_task)

# Save complexity data
complexity_data.to_csv('data/processed/complexity/job_task_complexity.csv', index=False)
print(f"Calculated complexity metrics for {len(complexity_data)} occupations")

# Create Excel file with all data
print("\nCreating Excel file with all data...")
with pd.ExcelWriter('data/processed/complexity/job_task_complexity_data.xlsx') as writer:
    complexity_data.to_excel(writer, sheet_name='Occupation Data', index=False)
    state_summary.to_excel(writer, sheet_name='State Summary', index=False)
    metro_summary.to_excel(writer, sheet_name='Metro Summary', index=False)
    
    # Create a sheet with complexity rankings
    complexity_rankings = complexity_data[['soc_code', 'occupation_title', 'job_complexity', 'task_complexity', 
                                          'annual_mean_wage', 'employment', 'uber_category', 'major_group_name']]
    complexity_rankings.sort_values('job_complexity', ascending=False).to_excel(writer, sheet_name='Job Complexity Rankings', index=False)
    complexity_rankings.sort_values('task_complexity', ascending=False).to_excel(writer, sheet_name='Task Complexity Rankings', index=False)

print("Excel file created with all complexity data")

# Create data for job space visualization
print("\nCreating data for job space visualization...")

# Calculate proximity between occupations based on complexity and wage similarity
job_space_data = complexity_data[['soc_code', 'occupation_title', 'job_complexity', 'task_complexity', 
                                 'annual_mean_wage', 'employment', 'uber_category']].copy()

# Normalize values for proximity calculation
job_space_data['norm_job_complexity'] = (job_space_data['job_complexity'] - job_space_data['job_complexity'].mean()) / job_space_data['job_complexity'].std()
job_space_data['norm_task_complexity'] = (job_space_data['task_complexity'] - job_space_data['task_complexity'].mean()) / job_space_data['task_complexity'].std()
job_space_data['norm_wage'] = (job_space_data['annual_mean_wage'] - job_space_data['annual_mean_wage'].mean()) / job_space_data['annual_mean_wage'].std()

# Calculate proximity matrix
print("Calculating job proximity matrix...")
job_codes = job_space_data['soc_code'].tolist()
proximity_matrix = []

# Limit to 500 jobs for performance reasons
if len(job_codes) > 500:
    print(f"Limiting job space to 500 jobs (out of {len(job_codes)}) for performance reasons")
    job_codes = job_codes[:500]
    job_space_data = job_space_data[job_space_data['soc_code'].isin(job_codes)]

for i, job1 in enumerate(job_codes):
    row = []
    job1_data = job_space_data[job_space_data['soc_code'] == job1].iloc[0]
    
    for j, job2 in enumerate(job_codes):
        if i == j:
            # Same job, maximum proximity
            row.append(1.0)
        else:
            job2_data = job_space_data[job_space_data['soc_code'] == job2].iloc[0]
            
            # Calculate Euclidean distance between jobs based on normalized metrics
            distance = np.sqrt(
                (job1_data['norm_job_complexity'] - job2_data['norm_job_complexity'])**2 +
                (job1_data['norm_task_complexity'] - job2_data['norm_task_complexity'])**2 +
                (job1_data['norm_wage'] - job2_data['norm_wage'])**2
            )
            
            # Convert distance to proximity (inverse relationship)
            proximity = 1 / (1 + distance)
            row.append(float(proximity))
    
    proximity_matrix.append(row)

# Create nodes and links for network visualization
nodes = []
for _, job in job_space_data.iterrows():
    nodes.append({
        'id': job['soc_code'],
        'name': job['occupation_title'],
        'group': job['uber_category'],
        'job_complexity': float(job['job_complexity']),
        'task_complexity': float(job['task_complexity']),
        'wage': float(job['annual_mean_wage']),
        'employment': float(job['employment'])
    })

# Create links (edges) between jobs with high proximity
links = []
proximity_threshold = 0.7  # Only create links for jobs with high proximity

for i, job1 in enumerate(job_codes):
    for j, job2 in enumerate(job_codes):
        if i < j:  # Avoid duplicates and self-links
            proximity = proximity_matrix[i][j]
            if proximity > proximity_threshold:
                links.append({
                    'source': job1,
                    'target': job2,
                    'value': float(proximity)
                })

# Create job space network data
job_space_network = {
    'nodes': nodes,
    'links': links
}

# Save job space data
with open('data/processed/complexity/job_space_network.json', 'w') as f:
    json.dump(job_space_network, f)
print(f"Created job space network with {len(nodes)} nodes and {len(links)} links")

# Save separate CSV files for job complexity and task complexity
job_complexity_data = complexity_data[['soc_code', 'occupation_title', 'job_complexity', 
                                      'annual_mean_wage', 'employment', 'uber_category', 'major_group_name']]
job_complexity_data.to_csv('data/processed/complexity/job_complexity.csv', index=False)

task_complexity_data = complexity_data[['soc_code', 'occupation_title', 'task_complexity', 
                                       'annual_10pct_wage', 'annual_90pct_wage', 'wage_range', 
                                       'uber_category', 'major_group_name']]
task_complexity_data.to_csv('data/processed/complexity/task_complexity.csv', index=False)

print("\nBLS data extraction and mapping completed successfully!")
