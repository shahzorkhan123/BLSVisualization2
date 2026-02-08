import pandas as pd
import numpy as np
import os
from scipy import sparse
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

# Create output directories
os.makedirs('data/processed/complexity', exist_ok=True)
os.makedirs('visualizations/complexity', exist_ok=True)

print("Loading processed data...")
# Load processed data
df_job = pd.read_csv('data/processed/jobs.csv')
df_task = pd.read_csv('data/processed/tasks.csv')
job_task_matrix = pd.read_csv('data/processed/job_task_matrix.csv')
task_rating_dwa_wage = pd.read_csv('data/processed/task_rating_dwa_wage.csv')

# Load state and metro data
state_job_df = pd.read_csv('data/processed/states/state_job_data.csv')
metro_job_df = pd.read_csv('data/processed/metros/metro_job_data.csv')

print(f"Jobs data shape: {df_job.shape}")
print(f"Tasks data shape: {df_task.shape}")
print(f"Job-Task matrix shape: {job_task_matrix.shape}")
print(f"State jobs data shape: {state_job_df.shape}")
print(f"Metro jobs data shape: {metro_job_df.shape}")

print("Calculating job and task complexity for US data...")

def calculate_complexity(job_task_df, job_df, region_type='US', region_name='United States'):
    """
    Calculate job complexity index (JCI) and task complexity index (TCI) using the method from the R script.
    
    Parameters:
    job_task_df: DataFrame with job-task relationships (O_NET_SOC_Code, DWA_ID, RCA)
    job_df: DataFrame with job information (O_NET_SOC_Code, wage, employment)
    region_type: Type of region (US, State, Metro)
    region_name: Name of the region
    
    Returns:
    job_complexity_df: DataFrame with job complexity metrics
    task_complexity_df: DataFrame with task complexity metrics
    """
    print(f"Calculating complexity for {region_type}: {region_name}")
    
    # Filter job_task_df to only include jobs that are in job_df
    valid_jobs = job_df['O_NET_SOC_Code'].unique()
    job_task_filtered = job_task_df[job_task_df['O_NET_SOC_Code'].isin(valid_jobs)]
    
    # Get unique jobs and tasks after filtering
    job_codes = job_task_filtered['O_NET_SOC_Code'].unique()
    task_ids = job_task_filtered['DWA_ID'].unique()
    
    print(f"  Number of jobs after filtering: {len(job_codes)}")
    print(f"  Number of tasks after filtering: {len(task_ids)}")
    
    # Create dictionaries to map codes to indices
    job_to_idx = {code: i for i, code in enumerate(job_codes)}
    task_to_idx = {tid: i for i, tid in enumerate(task_ids)}
    
    # Create sparse matrix
    Nj = len(job_codes)
    Nt = len(task_ids)
    mjt = sparse.lil_matrix((Nj, Nt), dtype=np.float64)
    
    # Fill the matrix with RCA values
    for _, row in job_task_filtered.iterrows():
        job_idx = job_to_idx.get(row['O_NET_SOC_Code'])
        task_idx = task_to_idx.get(row['DWA_ID'])
        if job_idx is not None and task_idx is not None:
            mjt[job_idx, task_idx] = row['RCA']
    
    # Convert to CSR format for efficient operations
    mjt = mjt.tocsr()
    
    # Calculate number of tasks per job and number of jobs per task
    nj = np.array(mjt.sum(axis=1)).flatten()  # Number of tasks per job
    nt = np.array(mjt.sum(axis=0)).flatten()  # Number of jobs per task
    
    # Check for zero values to avoid division by zero
    nj[nj == 0] = 1
    nt[nt == 0] = 1
    
    # Create wage vector
    job_df_filtered = job_df[job_df['O_NET_SOC_Code'].isin(job_codes)]
    job_df_sorted = job_df_filtered.sort_values('O_NET_SOC_Code')
    job_df_sorted = job_df_sorted.set_index('O_NET_SOC_Code').loc[job_codes].reset_index()
    wj = job_df_sorted['A_MEAN'].values
    
    # Stage 1: Calculate initial task complexity (average wage)
    kt1 = np.zeros(Nt)
    for j in range(Nj):
        for t in mjt.getrow(j).nonzero()[1]:
            kt1[t] += wj[j]
    kt1 = kt1 / nt
    
    # Method 2: Iterative method for complexity calculation
    # Initialize with Stage 1 values
    kjn_1 = wj.copy()
    ktn_1 = kt1.copy()
    
    # Create diagonal matrices for normalization
    diag_nj = sparse.diags(1/nj)
    diag_nt = sparse.diags(1/nt)
    
    # Iterate 20 times as in the R script
    for i in range(20):
        # Calculate new complexity values
        kjn = diag_nj.dot(mjt.dot(ktn_1))
        ktn = diag_nt.dot(mjt.T.dot(kjn_1))
        
        # Update for next iteration
        kjn_1 = kjn
        ktn_1 = ktn
    
    # Final complexity values
    jci = kjn
    tci = ktn
    
    # Create DataFrames with results
    job_complexity_df = pd.DataFrame({
        'O_NET_SOC_Code': job_codes,
        'JCI': jci,
        'Wage': wj,
        'Region_Type': region_type,
        'Region': region_name
    })
    
    task_complexity_df = pd.DataFrame({
        'DWA_ID': task_ids,
        'TCI': tci,
        'Avg_Wage': kt1,
        'Region_Type': region_type,
        'Region': region_name
    })
    
    return job_complexity_df, task_complexity_df

# Calculate complexity for US data
us_job_complexity, us_task_complexity = calculate_complexity(
    job_task_matrix, 
    df_job
)

# Merge with job and task information
us_job_complexity = pd.merge(
    us_job_complexity,
    df_job[['O_NET_SOC_Code', 'OCC_TITLE', 'TOT_EMP']],
    on='O_NET_SOC_Code',
    how='left'
)

us_task_complexity = pd.merge(
    us_task_complexity,
    df_task[['DWA_ID', 'DWA_Title', 'Work_Activities_Group_ID', 'Work_Activities_Group_Name']],
    on='DWA_ID',
    how='left'
)

print("Calculating job and task complexity for states...")
# Calculate complexity for each state
state_job_complexity_list = []
state_task_complexity_list = []

# Get unique states
states = state_job_df['State'].unique()

# Process a subset of states for demonstration (to save time)
demo_states = states[:5]  # First 5 states for demo
for state in demo_states:
    # Filter data for this state
    state_data = state_job_df[state_job_df['State'] == state]
    
    # Create job-task matrix for this state
    state_job_task = job_task_matrix.copy()  # Use same job-task relationships
    
    # Calculate complexity
    job_complexity, task_complexity = calculate_complexity(
        state_job_task,
        state_data,
        region_type='State',
        region_name=state
    )
    
    # Add state column explicitly for merging
    job_complexity['State'] = state
    task_complexity['State'] = state
    
    # Add to lists
    state_job_complexity_list.append(job_complexity)
    state_task_complexity_list.append(task_complexity)

# Combine all state results
if state_job_complexity_list:
    all_state_job_complexity = pd.concat(state_job_complexity_list)
    all_state_task_complexity = pd.concat(state_task_complexity_list)
    
    # Merge with job and task information
    all_state_job_complexity = pd.merge(
        all_state_job_complexity,
        state_job_df[['State', 'O_NET_SOC_Code', 'OCC_TITLE', 'TOT_EMP']].drop_duplicates(),
        on=['State', 'O_NET_SOC_Code'],
        how='left'
    )
    
    all_state_task_complexity = pd.merge(
        all_state_task_complexity,
        df_task[['DWA_ID', 'DWA_Title', 'Work_Activities_Group_ID', 'Work_Activities_Group_Name']],
        on='DWA_ID',
        how='left'
    )

print("Calculating job and task complexity for metropolitan areas...")
# Calculate complexity for each metro area
metro_job_complexity_list = []
metro_task_complexity_list = []

# Get unique metros
metros = metro_job_df['Metro'].unique()

# Process a subset of metros for demonstration (to save time)
demo_metros = metros[:3]  # First 3 metros for demo
for metro in demo_metros:
    # Filter data for this metro
    metro_data = metro_job_df[metro_job_df['Metro'] == metro]
    
    # Create job-task matrix for this metro
    metro_job_task = job_task_matrix.copy()  # Use same job-task relationships
    
    # Calculate complexity
    job_complexity, task_complexity = calculate_complexity(
        metro_job_task,
        metro_data,
        region_type='Metro',
        region_name=metro
    )
    
    # Add metro column explicitly for merging
    job_complexity['Metro'] = metro
    task_complexity['Metro'] = metro
    
    # Add to lists
    metro_job_complexity_list.append(job_complexity)
    metro_task_complexity_list.append(task_complexity)

# Combine all metro results
if metro_job_complexity_list:
    all_metro_job_complexity = pd.concat(metro_job_complexity_list)
    all_metro_task_complexity = pd.concat(metro_task_complexity_list)
    
    # Merge with job and task information
    all_metro_job_complexity = pd.merge(
        all_metro_job_complexity,
        metro_job_df[['Metro', 'O_NET_SOC_Code', 'OCC_TITLE', 'TOT_EMP']].drop_duplicates(),
        on=['Metro', 'O_NET_SOC_Code'],
        how='left'
    )
    
    all_metro_task_complexity = pd.merge(
        all_metro_task_complexity,
        df_task[['DWA_ID', 'DWA_Title', 'Work_Activities_Group_ID', 'Work_Activities_Group_Name']],
        on='DWA_ID',
        how='left'
    )

# Combine all complexity results
all_job_complexity = pd.concat([
    us_job_complexity,
    all_state_job_complexity if 'all_state_job_complexity' in locals() else pd.DataFrame(),
    all_metro_job_complexity if 'all_metro_job_complexity' in locals() else pd.DataFrame()
])

all_task_complexity = pd.concat([
    us_task_complexity,
    all_state_task_complexity if 'all_state_task_complexity' in locals() else pd.DataFrame(),
    all_metro_task_complexity if 'all_metro_task_complexity' in locals() else pd.DataFrame()
])

# Save complexity results
all_job_complexity.to_csv('data/processed/complexity/job_complexity.csv', index=False)
all_task_complexity.to_csv('data/processed/complexity/task_complexity.csv', index=False)

print("Creating complexity visualizations...")
# Create scatter plot of wage vs JCI for US
fig = px.scatter(
    us_job_complexity,
    x='Wage',
    y='JCI',
    hover_name='OCC_TITLE',
    size='TOT_EMP',
    color='JCI',
    color_continuous_scale='Viridis',
    title='Job Complexity Index vs Wage (US)',
    labels={'Wage': 'Annual Mean Wage ($)', 'JCI': 'Job Complexity Index'},
)
fig.update_layout(width=900, height=700)
fig.write_html('visualizations/complexity/us_wage_vs_jci.html')

# Create scatter plot of average wage vs TCI for US
fig = px.scatter(
    us_task_complexity,
    x='Avg_Wage',
    y='TCI',
    hover_name='DWA_Title',
    color='Work_Activities_Group_Name',
    title='Task Complexity Index vs Average Wage (US)',
    labels={'Avg_Wage': 'Average Wage ($)', 'TCI': 'Task Complexity Index'},
)
fig.update_layout(width=900, height=700)
fig.write_html('visualizations/complexity/us_avg_wage_vs_tci.html')

# Create bar chart of top and bottom jobs by complexity
top_jobs = us_job_complexity.sort_values('JCI', ascending=False).head(10)
bottom_jobs = us_job_complexity.sort_values('JCI').head(10)

fig = go.Figure()
fig.add_trace(go.Bar(
    x=top_jobs['OCC_TITLE'],
    y=top_jobs['JCI'],
    name='Top 10 Jobs by Complexity',
    marker_color='green'
))
fig.update_layout(
    title='Top 10 Jobs by Complexity Index (US)',
    xaxis_title='Occupation',
    yaxis_title='Job Complexity Index',
    xaxis_tickangle=-45,
    width=900,
    height=600
)
fig.write_html('visualizations/complexity/us_top_jobs_by_complexity.html')

fig = go.Figure()
fig.add_trace(go.Bar(
    x=bottom_jobs['OCC_TITLE'],
    y=bottom_jobs['JCI'],
    name='Bottom 10 Jobs by Complexity',
    marker_color='red'
))
fig.update_layout(
    title='Bottom 10 Jobs by Complexity Index (US)',
    xaxis_title='Occupation',
    yaxis_title='Job Complexity Index',
    xaxis_tickangle=-45,
    width=900,
    height=600
)
fig.write_html('visualizations/complexity/us_bottom_jobs_by_complexity.html')

# Create comparison visualizations for states if available
if 'all_state_job_complexity' in locals():
    # Compare JCI across states for a few selected occupations
    selected_occupations = us_job_complexity.sort_values('TOT_EMP', ascending=False).head(5)['O_NET_SOC_Code'].tolist()
    state_comparison = all_state_job_complexity[all_state_job_complexity['O_NET_SOC_Code'].isin(selected_occupations)]
    
    fig = px.box(
        state_comparison,
        x='OCC_TITLE',
        y='JCI',
        color='OCC_TITLE',
        title='Job Complexity Index Variation Across States',
        labels={'OCC_TITLE': 'Occupation', 'JCI': 'Job Complexity Index'}
    )
    fig.update_layout(width=900, height=700, xaxis_tickangle=-45)
    fig.write_html('visualizations/complexity/state_jci_comparison.html')

# Create comparison visualizations for metros if available
if 'all_metro_job_complexity' in locals():
    # Compare JCI across metros for a few selected occupations
    metro_comparison = all_metro_job_complexity[all_metro_job_complexity['O_NET_SOC_Code'].isin(selected_occupations)]
    
    fig = px.box(
        metro_comparison,
        x='OCC_TITLE',
        y='JCI',
        color='OCC_TITLE',
        title='Job Complexity Index Variation Across Metropolitan Areas',
        labels={'OCC_TITLE': 'Occupation', 'JCI': 'Job Complexity Index'}
    )
    fig.update_layout(width=900, height=700, xaxis_tickangle=-45)
    fig.write_html('visualizations/complexity/metro_jci_comparison.html')

print("Creating Excel file with complexity data...")
# Create Excel writer
with pd.ExcelWriter('data/processed/complexity/job_task_complexity_data.xlsx') as writer:
    # Write US data
    us_job_complexity.to_excel(writer, sheet_name='US_Job_Complexity', index=False)
    us_task_complexity.to_excel(writer, sheet_name='US_Task_Complexity', index=False)
    
    # Write state data if available
    if 'all_state_job_complexity' in locals():
        all_state_job_complexity.to_excel(writer, sheet_name='State_Job_Complexity', index=False)
        all_state_task_complexity.to_excel(writer, sheet_name='State_Task_Complexity', index=False)
    
    # Write metro data if available
    if 'all_metro_job_complexity' in locals():
        all_metro_job_complexity.to_excel(writer, sheet_name='Metro_Job_Complexity', index=False)
        all_metro_task_complexity.to_excel(writer, sheet_name='Metro_Task_Complexity', index=False)

print("Job and task complexity calculation and visualization complete!")
