import pandas as pd
import numpy as np
import json
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

print("Creating treemap visualizations for job complexity data...")

# Create output directory for visualizations
os.makedirs('/home/ubuntu/research_project/visualizations', exist_ok=True)

# Load the job complexity data
job_complexity_file = '/home/ubuntu/research_project/data/processed/complexity/job_complexity.csv'
state_complexity_file = '/home/ubuntu/research_project/data/processed/complexity/state_complexity_metrics.csv'

print("Loading job complexity data...")
try:
    job_df = pd.read_csv(job_complexity_file)
    print(f"Loaded job complexity data with {len(job_df)} rows")
    print(f"Columns: {job_df.columns.tolist()}")
    
    # Check if we have state data
    state_metrics_exists = os.path.exists(state_complexity_file)
    if state_metrics_exists:
        state_df = pd.read_csv(state_complexity_file)
        print(f"Loaded state complexity data with {len(state_df)} rows")
        print(f"Columns: {state_df.columns.tolist()}")
    else:
        print("State complexity data not found")
    
    # Extract SOC major groups
    job_df['major_group'] = job_df['soc_code'].apply(lambda x: x.split('-')[0] if isinstance(x, str) and '-' in x else '')
    
    # Define major group names
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
    
    # Add major group names
    job_df['major_group_name'] = job_df['major_group'].map(major_group_names)
    
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
    
    # Add uber category
    job_df['uber_category'] = job_df['major_group'].map(major_to_uber)
    
    # Fill missing values
    job_df['uber_category'] = job_df['uber_category'].fillna('Other')
    job_df['major_group_name'] = job_df['major_group_name'].fillna('Other')
    
    # Ensure numeric columns are numeric
    numeric_cols = ['job_complexity_index', 'job_price_index', 'annual_mean_wage', 'employment']
    for col in numeric_cols:
        if col in job_df.columns:
            job_df[col] = pd.to_numeric(job_df[col], errors='coerce')
    
    # Filter out rows with missing key data
    job_df = job_df.dropna(subset=['job_complexity_index', 'employment'])
    
    # Create a size metric for visualization (log of employment)
    job_df['log_employment'] = np.log1p(job_df['employment'])
    
    # Create a color metric (job complexity index)
    job_df['color_metric'] = job_df['job_complexity_index']
    
    print(f"Prepared job data with {len(job_df)} rows")
    
    # Create treemap visualization
    print("Creating treemap visualization...")
    
    # Create hierarchical treemap (uber category > major group > occupation)
    fig = px.treemap(
        job_df,
        path=['uber_category', 'major_group_name', 'occupation_title'],
        values='employment',
        color='job_complexity_index',
        color_continuous_scale='RdBu',
        color_continuous_midpoint=1.0,
        hover_data={
            'soc_code': True,
            'job_complexity_index': ':.2f',
            'job_price_index': ':.2f',
            'annual_mean_wage': '$,.0f',
            'employment': ',.0f'
        },
        title='Job Complexity Treemap: Occupations by Employment and Complexity'
    )
    
    # Update layout
    fig.update_layout(
        margin=dict(t=50, l=25, r=25, b=25),
        font=dict(family="Arial, sans-serif", size=12),
        coloraxis_colorbar=dict(
            title="Job Complexity Index",
            tickvals=[0.5, 1.0, 1.5, 2.0, 2.5],
            ticktext=["0.5", "1.0 (median)", "1.5", "2.0", "2.5"]
        ),
        width=1200,
        height=800
    )
    
    # Save the figure
    fig.write_html('/home/ubuntu/research_project/visualizations/job_complexity_treemap.html')
    print("Saved treemap visualization to job_complexity_treemap.html")
    
    # Create a treemap by job price index
    fig_price = px.treemap(
        job_df,
        path=['uber_category', 'major_group_name', 'occupation_title'],
        values='employment',
        color='job_price_index',
        color_continuous_scale='Viridis',
        color_continuous_midpoint=1.0,
        hover_data={
            'soc_code': True,
            'job_complexity_index': ':.2f',
            'job_price_index': ':.2f',
            'annual_mean_wage': '$,.0f',
            'employment': ',.0f'
        },
        title='Job Price Treemap: Occupations by Employment and Price Index'
    )
    
    # Update layout
    fig_price.update_layout(
        margin=dict(t=50, l=25, r=25, b=25),
        font=dict(family="Arial, sans-serif", size=12),
        coloraxis_colorbar=dict(
            title="Job Price Index",
            tickvals=[0.5, 1.0, 1.5, 2.0, 2.5],
            ticktext=["0.5", "1.0 (median)", "1.5", "2.0", "2.5"]
        ),
        width=1200,
        height=800
    )
    
    # Save the figure
    fig_price.write_html('/home/ubuntu/research_project/visualizations/job_price_treemap.html')
    print("Saved price treemap visualization to job_price_treemap.html")
    
    # Create state-level visualization if state data exists
    if state_metrics_exists:
        print("Creating state-level visualizations...")
        
        # Create a choropleth map of job complexity by state
        fig_state = px.choropleth(
            state_df,
            locations='state',
            locationmode='USA-states',
            color='job_complexity_index',
            scope='usa',
            color_continuous_scale='RdBu',
            color_continuous_midpoint=1.0,
            hover_data={
                'job_complexity_index': ':.2f',
                'job_price_index': ':.2f',
                'annual_mean_wage': '$,.0f',
                'employment': ',.0f'
            },
            title='Job Complexity by State'
        )
        
        # Update layout
        fig_state.update_layout(
            margin=dict(t=50, l=25, r=25, b=25),
            font=dict(family="Arial, sans-serif", size=12),
            coloraxis_colorbar=dict(
                title="Job Complexity Index",
                tickvals=[0.8, 0.9, 1.0, 1.1, 1.2],
                ticktext=["0.8", "0.9", "1.0 (median)", "1.1", "1.2"]
            ),
            width=1000,
            height=600
        )
        
        # Save the figure
        fig_state.write_html('/home/ubuntu/research_project/visualizations/state_job_complexity_map.html')
        print("Saved state-level visualization to state_job_complexity_map.html")
        
        # Create a choropleth map of job price by state
        fig_state_price = px.choropleth(
            state_df,
            locations='state',
            locationmode='USA-states',
            color='job_price_index',
            scope='usa',
            color_continuous_scale='Viridis',
            color_continuous_midpoint=1.0,
            hover_data={
                'job_complexity_index': ':.2f',
                'job_price_index': ':.2f',
                'annual_mean_wage': '$,.0f',
                'employment': ',.0f'
            },
            title='Job Price Index by State'
        )
        
        # Update layout
        fig_state_price.update_layout(
            margin=dict(t=50, l=25, r=25, b=25),
            font=dict(family="Arial, sans-serif", size=12),
            coloraxis_colorbar=dict(
                title="Job Price Index",
                tickvals=[0.8, 0.9, 1.0, 1.1, 1.2],
                ticktext=["0.8", "0.9", "1.0 (median)", "1.1", "1.2"]
            ),
            width=1000,
            height=600
        )
        
        # Save the figure
        fig_state_price.write_html('/home/ubuntu/research_project/visualizations/state_job_price_map.html')
        print("Saved state-level price visualization to state_job_price_map.html")
    
    # Create a filtered version for top occupations by employment
    top_jobs = job_df.sort_values('employment', ascending=False).head(100)
    
    fig_top = px.treemap(
        top_jobs,
        path=['uber_category', 'major_group_name', 'occupation_title'],
        values='employment',
        color='job_complexity_index',
        color_continuous_scale='RdBu',
        color_continuous_midpoint=1.0,
        hover_data={
            'soc_code': True,
            'job_complexity_index': ':.2f',
            'job_price_index': ':.2f',
            'annual_mean_wage': '$,.0f',
            'employment': ',.0f'
        },
        title='Top 100 Occupations by Employment: Job Complexity Treemap'
    )
    
    # Update layout
    fig_top.update_layout(
        margin=dict(t=50, l=25, r=25, b=25),
        font=dict(family="Arial, sans-serif", size=12),
        coloraxis_colorbar=dict(
            title="Job Complexity Index",
            tickvals=[0.5, 1.0, 1.5, 2.0, 2.5],
            ticktext=["0.5", "1.0 (median)", "1.5", "2.0", "2.5"]
        ),
        width=1200,
        height=800
    )
    
    # Save the figure
    fig_top.write_html('/home/ubuntu/research_project/visualizations/top_jobs_complexity_treemap.html')
    print("Saved top jobs treemap visualization to top_jobs_complexity_treemap.html")
    
    # Create a filtered version for top occupations by complexity
    top_complex_jobs = job_df.sort_values('job_complexity_index', ascending=False).head(100)
    
    fig_top_complex = px.treemap(
        top_complex_jobs,
        path=['uber_category', 'major_group_name', 'occupation_title'],
        values='employment',
        color='job_complexity_index',
        color_continuous_scale='RdBu',
        color_continuous_midpoint=1.0,
        hover_data={
            'soc_code': True,
            'job_complexity_index': ':.2f',
            'job_price_index': ':.2f',
            'annual_mean_wage': '$,.0f',
            'employment': ',.0f'
        },
        title='Top 100 Most Complex Occupations: Job Complexity Treemap'
    )
    
    # Update layout
    fig_top_complex.update_layout(
        margin=dict(t=50, l=25, r=25, b=25),
        font=dict(family="Arial, sans-serif", size=12),
        coloraxis_colorbar=dict(
            title="Job Complexity Index",
            tickvals=[0.5, 1.0, 1.5, 2.0, 2.5],
            ticktext=["0.5", "1.0 (median)", "1.5", "2.0", "2.5"]
        ),
        width=1200,
        height=800
    )
    
    # Save the figure
    fig_top_complex.write_html('/home/ubuntu/research_project/visualizations/most_complex_jobs_treemap.html')
    print("Saved most complex jobs treemap visualization to most_complex_jobs_treemap.html")
    
    # Create a sunburst chart as an alternative visualization
    fig_sunburst = px.sunburst(
        job_df,
        path=['uber_category', 'major_group_name', 'occupation_title'],
        values='employment',
        color='job_complexity_index',
        color_continuous_scale='RdBu',
        color_continuous_midpoint=1.0,
        hover_data={
            'job_complexity_index': ':.2f',
            'annual_mean_wage': '$,.0f',
            'employment': ',.0f'
        },
        title='Job Complexity Sunburst: Occupations by Employment and Complexity'
    )
    
    # Update layout
    fig_sunburst.update_layout(
        margin=dict(t=50, l=25, r=25, b=25),
        font=dict(family="Arial, sans-serif", size=12),
        coloraxis_colorbar=dict(
            title="Job Complexity Index",
            tickvals=[0.5, 1.0, 1.5, 2.0, 2.5],
            ticktext=["0.5", "1.0 (median)", "1.5", "2.0", "2.5"]
        ),
        width=1000,
        height=1000
    )
    
    # Save the figure
    fig_sunburst.write_html('/home/ubuntu/research_project/visualizations/job_complexity_sunburst.html')
    print("Saved sunburst visualization to job_complexity_sunburst.html")
    
    # Create a scatter plot of job complexity vs. job price
    fig_scatter = px.scatter(
        job_df,
        x='job_complexity_index',
        y='job_price_index',
        size='employment',
        color='uber_category',
        hover_name='occupation_title',
        hover_data={
            'soc_code': True,
            'job_complexity_index': ':.2f',
            'job_price_index': ':.2f',
            'annual_mean_wage': '$,.0f',
            'employment': ',.0f'
        },
        title='Job Complexity vs. Job Price Index',
        labels={
            'job_complexity_index': 'Job Complexity Index',
            'job_price_index': 'Job Price Index',
            'uber_category': 'Category'
        }
    )
    
    # Update layout
    fig_scatter.update_layout(
        margin=dict(t=50, l=25, r=25, b=25),
        font=dict(family="Arial, sans-serif", size=12),
        width=1200,
        height=800,
        xaxis=dict(
            title='Job Complexity Index',
            tickvals=[0.5, 1.0, 1.5, 2.0, 2.5],
            ticktext=["0.5", "1.0 (median)", "1.5", "2.0", "2.5"]
        ),
        yaxis=dict(
            title='Job Price Index',
            tickvals=[0.5, 1.0, 1.5, 2.0, 2.5],
            ticktext=["0.5", "1.0 (median)", "1.5", "2.0", "2.5"]
        )
    )
    
    # Save the figure
    fig_scatter.write_html('/home/ubuntu/research_project/visualizations/job_complexity_vs_price_scatter.html')
    print("Saved scatter plot to job_complexity_vs_price_scatter.html")
    
    # Create a bubble chart of top 50 occupations by employment
    top50_jobs = job_df.sort_values('employment', ascending=False).head(50)
    
    fig_bubble = px.scatter(
        top50_jobs,
        x='job_complexity_index',
        y='job_price_index',
        size='employment',
        color='uber_category',
        hover_name='occupation_title',
        text='occupation_title',
        hover_data={
            'soc_code': True,
            'job_complexity_index': ':.2f',
            'job_price_index': ':.2f',
            'annual_mean_wage': '$,.0f',
            'employment': ',.0f'
        },
        title='Top 50 Occupations by Employment: Complexity vs. Price',
        labels={
            'job_complexity_index': 'Job Complexity Index',
            'job_price_index': 'Job Price Index',
            'uber_category': 'Category'
        }
    )
    
    # Update layout
    fig_bubble.update_layout(
        margin=dict(t=50, l=25, r=25, b=25),
        font=dict(family="Arial, sans-serif", size=12),
        width=1200,
        height=800,
        xaxis=dict(
            title='Job Complexity Index',
            tickvals=[0.5, 1.0, 1.5, 2.0, 2.5],
            ticktext=["0.5", "1.0 (median)", "1.5", "2.0", "2.5"]
        ),
        yaxis=dict(
            title='Job Price Index',
            tickvals=[0.5, 1.0, 1.5, 2.0, 2.5],
            ticktext=["0.5", "1.0 (median)", "1.5", "2.0", "2.5"]
        )
    )
    
    # Update text position
    fig_bubble.update_traces(textposition='top center')
    
    # Save the figure
    fig_bubble.write_html('/home/ubuntu/research_project/visualizations/top50_jobs_bubble_chart.html')
    print("Saved bubble chart to top50_jobs_bubble_chart.html")
    
    # Create a JSON file for the website
    print("Creating JSON data for website integration...")
    
    # Prepare data for JSON export
    json_data = {
        'occupations': [],
        'major_groups': [],
        'uber_categories': []
    }
    
    # Add occupation data
    for _, row in job_df.iterrows():
        json_data['occupations'].append({
            'soc_code': row['soc_code'],
            'title': row['occupation_title'],
            'major_group': row['major_group'],
            'major_group_name': row['major_group_name'],
            'uber_category': row['uber_category'],
            'complexity_index': float(row['job_complexity_index']),
            'price_index': float(row['job_price_index']),
            'annual_wage': float(row['annual_mean_wage']),
            'employment': int(row['employment'])
        })
    
    # Add major group data
    for code, name in major_group_names.items():
        group_data = job_df[job_df['major_group'] == code]
        if len(group_data) > 0:
            json_data['major_groups'].append({
                'code': code,
                'name': name,
                'uber_category': major_to_uber.get(code, 'Other'),
                'avg_complexity': float(group_data['job_complexity_index'].mean()),
                'avg_price': float(group_data['job_price_index'].mean()),
                'total_employment': int(group_data['employment'].sum())
            })
    
    # Add uber category data
    for uber, majors in uber_categories.items():
        category_data = job_df[job_df['uber_category'] == uber]
        if len(category_data) > 0:
            json_data['uber_categories'].append({
                'name': uber,
                'avg_complexity': float(category_data['job_complexity_index'].mean()),
                'avg_price': float(category_data['job_price_index'].mean()),
                'total_employment': int(category_data['employment'].sum())
            })
    
    # Save JSON data
    with open('/home/ubuntu/research_project/visualizations/job_complexity_data.json', 'w') as f:
        json.dump(json_data, f)
    
    print("Saved JSON data for website integration")
    
except Exception as e:
    print(f"Error creating treemap visualizations: {str(e)}")
    import traceback
    print(traceback.format_exc())

print("Treemap visualization creation complete!")
