import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import traceback

print("Creating improved treemap visualizations...")

# Create output directory for visualizations
os.makedirs('/home/ubuntu/research_project/website/visualizations', exist_ok=True)

# Load the job complexity data
job_complexity_file = '/home/ubuntu/research_project/data/processed/complexity/job_complexity.csv'

print("Loading job complexity data...")
try:
    job_df = pd.read_csv(job_complexity_file)
    print(f"Loaded job complexity data with {len(job_df)} rows")
    
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
    
    print(f"Prepared job data with {len(job_df)} rows")
    
    # Create a function to generate treemap for different metrics
    def create_treemap(metric='employment', color_by='complexity'):
        print(f"Creating treemap with size by {metric} and color by {color_by}...")
        
        # Prepare data
        if metric == 'employment':
            size_col = 'employment'
            size_title = 'Employment'
        else:  # total_compensation
            # Calculate total compensation (employment * annual wage)
            job_df['total_compensation'] = job_df['employment'] * job_df['annual_mean_wage']
            size_col = 'total_compensation'
            size_title = 'Total Compensation'
        
        if color_by == 'complexity':
            color_col = 'job_complexity_index'
            color_title = 'Job Complexity Index'
        else:  # price
            color_col = 'job_price_index'
            color_title = 'Job Price Index'
        
        # Create labels with job titles
        job_df['label'] = job_df['occupation_title'].apply(lambda x: x[:20] + '...' if len(x) > 20 else x)
        
        # Create hover text
        job_df['hover_text'] = job_df.apply(
            lambda row: f"{row['occupation_title']} ({row['soc_code']})<br>"
                       f"Employment: {row['employment']:,.0f}<br>"
                       f"Annual Wage: ${row['annual_mean_wage']:,.0f}<br>"
                       f"Complexity: {row['job_complexity_index']:.2f}<br>"
                       f"Price Index: {row['job_price_index']:.2f}",
            axis=1
        )
        
        # Create treemap data
        labels = []
        parents = []
        values = []
        colors = []
        hovers = []
        
        # Add uber categories
        for uber in uber_categories.keys():
            labels.append(uber)
            parents.append("")
            values.append(0)  # Will be summed from children
            colors.append(0)  # Placeholder
            hovers.append(f"{uber}")
        
        # Add major groups
        for mg, name in major_group_names.items():
            if mg in major_to_uber:
                uber = major_to_uber[mg]
                labels.append(name)
                parents.append(uber)
                values.append(0)  # Will be summed from children
                colors.append(0)  # Placeholder
                hovers.append(f"{name}")
        
        # Add occupations
        for _, row in job_df.iterrows():
            if pd.notna(row['major_group_name']) and pd.notna(row[size_col]) and pd.notna(row[color_col]):
                labels.append(row['label'])
                parents.append(row['major_group_name'])
                values.append(row[size_col])
                colors.append(row[color_col])
                hovers.append(row['hover_text'])
        
        # Create figure
        fig = go.Figure(go.Treemap(
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total",
            marker=dict(
                colors=colors,
                colorscale='RdBu',
                reversescale=True,
                colorbar=dict(
                    title=color_title,
                    thickness=20,
                    len=0.7,
                    bgcolor='rgba(255,255,255,0.8)',
                    borderwidth=1,
                    bordercolor='#333',
                    titlefont=dict(size=14),
                    tickfont=dict(size=12)
                ),
            ),
            hovertext=hovers,
            hoverinfo="text",
            textposition="middle center",
            textfont=dict(size=12),
            pathbar=dict(visible=True),
        ))
        
        # Update layout
        title = f"Job {color_title.split(' ')[1]} Treemap: Occupations by {size_title} and {color_title}"
        fig.update_layout(
            title=title,
            margin=dict(t=50, l=25, r=25, b=25),
            width=1200,
            height=800,
        )
        
        # Add dropdown menus for interactivity
        fig.update_layout(
            updatemenus=[
                # Size by dropdown
                dict(
                    buttons=list([
                        dict(
                            args=[{"values": [v if i >= len(uber_categories) + len(major_group_names) else 0 for i, v in enumerate(values)]}],
                            label="Size by Employment",
                            method="update"
                        ),
                        dict(
                            args=[{"values": [job_df.loc[i-len(uber_categories)-len(major_group_names), 'total_compensation'] 
                                            if i >= len(uber_categories) + len(major_group_names) else 0 
                                            for i in range(len(labels))]}],
                            label="Size by Total Compensation",
                            method="update"
                        )
                    ]),
                    direction="down",
                    pad={"r": 10, "t": 10},
                    showactive=True,
                    x=0.1,
                    xanchor="left",
                    y=1.15,
                    yanchor="top",
                    bgcolor='rgba(255,255,255,0.8)',
                    bordercolor='#333',
                    borderwidth=1,
                ),
                # Color by dropdown
                dict(
                    buttons=list([
                        dict(
                            args=[{"marker.colors": [c if i >= len(uber_categories) + len(major_group_names) else 0 for i, c in enumerate(colors)],
                                  "marker.colorbar.title": "Job Complexity Index"}],
                            label="Color by Complexity",
                            method="update"
                        ),
                        dict(
                            args=[{"marker.colors": [job_df.loc[i-len(uber_categories)-len(major_group_names), 'job_price_index'] 
                                                   if i >= len(uber_categories) + len(major_group_names) else 0 
                                                   for i in range(len(labels))],
                                  "marker.colorbar.title": "Job Price Index"}],
                            label="Color by Price",
                            method="update"
                        )
                    ]),
                    direction="down",
                    pad={"r": 10, "t": 10},
                    showactive=True,
                    x=0.35,
                    xanchor="left",
                    y=1.15,
                    yanchor="top",
                    bgcolor='rgba(255,255,255,0.8)',
                    bordercolor='#333',
                    borderwidth=1,
                )
            ],
            annotations=[
                dict(text="Size by:", x=0.05, y=1.15, xref="paper", yref="paper", showarrow=False),
                dict(text="Color by:", x=0.3, y=1.15, xref="paper", yref="paper", showarrow=False)
            ]
        )
        
        return fig, title
    
    # Create treemaps with different metrics
    # 1. Employment size, complexity color
    fig_complexity, title_complexity = create_treemap(metric='employment', color_by='complexity')
    output_path = '/home/ubuntu/research_project/website/visualizations/job_complexity_treemap_improved.html'
    try:
        fig_complexity.write_html(output_path)
        print(f"Saved improved complexity treemap to {output_path}")
    except Exception as e:
        print(f"Error saving complexity treemap: {str(e)}")
        print(traceback.format_exc())
    
    # 2. Employment size, price color
    fig_price, title_price = create_treemap(metric='employment', color_by='price')
    output_path = '/home/ubuntu/research_project/website/visualizations/job_price_treemap_improved.html'
    try:
        fig_price.write_html(output_path)
        print(f"Saved improved price treemap to {output_path}")
    except Exception as e:
        print(f"Error saving price treemap: {str(e)}")
        print(traceback.format_exc())
    
    # 3. Total compensation size, complexity color
    fig_comp_complexity, title_comp_complexity = create_treemap(metric='total_compensation', color_by='complexity')
    output_path = '/home/ubuntu/research_project/website/visualizations/job_complexity_by_compensation_treemap.html'
    try:
        fig_comp_complexity.write_html(output_path)
        print(f"Saved complexity by compensation treemap to {output_path}")
    except Exception as e:
        print(f"Error saving complexity by compensation treemap: {str(e)}")
        print(traceback.format_exc())
    
    # 4. Total compensation size, price color
    fig_comp_price, title_comp_price = create_treemap(metric='total_compensation', color_by='price')
    output_path = '/home/ubuntu/research_project/website/visualizations/job_price_by_compensation_treemap.html'
    try:
        fig_comp_price.write_html(output_path)
        print(f"Saved price by compensation treemap to {output_path}")
    except Exception as e:
        print(f"Error saving price by compensation treemap: {str(e)}")
        print(traceback.format_exc())
    
except Exception as e:
    print(f"Error creating treemap visualizations: {str(e)}")
    print(traceback.format_exc())

print("Treemap visualization creation complete!")
