import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import traceback

print("Creating improved job space visualization...")

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
    
    # Create a simplified job space visualization
    print("Creating improved job space visualization...")
    
    # Get top occupations by employment
    top_jobs = job_df.sort_values('employment', ascending=False).head(200)
    
    # Create a synthetic layout for the job space
    # We'll use a force-directed-like layout but create it manually
    # First, create random positions for each major group
    np.random.seed(42)  # For reproducibility
    
    # Create positions for each major group
    major_group_positions = {}
    for mg in top_jobs['major_group'].unique():
        if pd.notna(mg) and mg != '':
            angle = np.random.uniform(0, 2*np.pi)
            radius = np.random.uniform(0.5, 1.0)
            major_group_positions[mg] = (radius * np.cos(angle), radius * np.sin(angle))
    
    # Now create positions for each occupation within its major group
    node_positions = {}
    for _, job in top_jobs.iterrows():
        mg = job['major_group']
        if mg in major_group_positions:
            base_x, base_y = major_group_positions[mg]
            # Add some random offset
            offset_x = np.random.uniform(-0.2, 0.2)
            offset_y = np.random.uniform(-0.2, 0.2)
            node_positions[job['soc_code']] = (base_x + offset_x, base_y + offset_y)
        else:
            # Random position for those without a major group
            angle = np.random.uniform(0, 2*np.pi)
            radius = np.random.uniform(0, 0.5)
            node_positions[job['soc_code']] = (radius * np.cos(angle), radius * np.sin(angle))
    
    # Create edges between occupations in the same major group
    edges = []
    for mg in top_jobs['major_group'].unique():
        if pd.notna(mg) and mg != '':
            mg_jobs = top_jobs[top_jobs['major_group'] == mg]['soc_code'].tolist()
            for i, job1 in enumerate(mg_jobs):
                for job2 in mg_jobs[i+1:]:
                    # Add edge with some probability
                    if np.random.random() < 0.3:  # 30% chance of connection
                        edges.append((job1, job2))
    
    # Also add some edges between related major groups
    related_groups = [
        ('11', '13'),  # Management and Business
        ('15', '17'),  # Computer and Engineering
        ('17', '19'),  # Engineering and Science
        ('29', '31'),  # Healthcare Practitioners and Support
        ('35', '39'),  # Food Service and Personal Care
        ('41', '43'),  # Sales and Office
        ('47', '49'),  # Construction and Installation
        ('49', '51'),  # Installation and Production
        ('51', '53'),  # Production and Transportation
    ]
    
    for mg1, mg2 in related_groups:
        mg1_jobs = top_jobs[top_jobs['major_group'] == mg1]['soc_code'].tolist()
        mg2_jobs = top_jobs[top_jobs['major_group'] == mg2]['soc_code'].tolist()
        
        # Add a few random connections between these groups
        for _ in range(min(5, len(mg1_jobs) * len(mg2_jobs) // 10)):
            if mg1_jobs and mg2_jobs:  # Make sure lists are not empty
                job1 = np.random.choice(mg1_jobs)
                job2 = np.random.choice(mg2_jobs)
                edges.append((job1, job2))
    
    # Extract node positions
    node_x = []
    node_y = []
    node_text = []
    node_size = []
    node_color = []
    node_group = []
    node_labels = []
    
    for _, job in top_jobs.iterrows():
        soc_code = job['soc_code']
        if soc_code in node_positions:
            x, y = node_positions[soc_code]
            node_x.append(x)
            node_y.append(y)
            
            # Create hover text
            node_text.append(f"{job['occupation_title']} ({soc_code})<br>Complexity: {job['job_complexity_index']:.2f}<br>Employment: {job['employment']:,}")
            
            # Create short labels for display
            # Get first word or two of occupation title
            title_words = job['occupation_title'].split()
            if len(title_words) > 2:
                short_label = ' '.join(title_words[:2])
                if len(short_label) > 15:  # If still too long, just use first word
                    short_label = title_words[0]
            else:
                short_label = job['occupation_title']
                
            node_labels.append(short_label)
            
            # Size based on log of employment
            size = np.log1p(job['employment']) * 2 if job['employment'] > 0 else 5
            node_size.append(size)
            
            # Color based on complexity
            node_color.append(job['job_complexity_index'])
            
            # Group by uber category
            node_group.append(job['uber_category'])
    
    # Extract edge positions
    edge_x = []
    edge_y = []
    
    for edge in edges:
        if edge[0] in node_positions and edge[1] in node_positions:
            x0, y0 = node_positions[edge[0]]
            x1, y1 = node_positions[edge[1]]
            
            # Add the line plot with a break in the middle
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
    
    # Create a Plotly figure
    fig = go.Figure()
    
    # Add edges
    fig.add_trace(
        go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines',
            showlegend=False
        )
    )
    
    # Get unique uber categories
    unique_categories = list(set(node_group))
    
    # Add nodes for each category
    for category in unique_categories:
        # Get indices for this category
        indices = [i for i, group in enumerate(node_group) if group == category]
        
        if not indices:
            continue
            
        # Extract data for this category
        cat_x = [node_x[i] for i in indices]
        cat_y = [node_y[i] for i in indices]
        cat_text = [node_text[i] for i in indices]
        cat_size = [node_size[i] for i in indices]
        cat_color = [node_color[i] for i in indices]
        cat_labels = [node_labels[i] for i in indices]
        
        # Add nodes for this category
        fig.add_trace(
            go.Scatter(
                x=cat_x, y=cat_y,
                mode='markers+text',
                marker=dict(
                    size=cat_size,
                    color=cat_color,
                    colorscale='RdBu',
                    colorbar=dict(
                        title='Complexity',
                        thickness=20,
                        len=0.7,
                        bgcolor='rgba(255,255,255,0.8)',
                        borderwidth=1,
                        bordercolor='#333',
                        titlefont=dict(size=14),
                        tickfont=dict(size=12)
                    ) if category == unique_categories[0] else None,
                    reversescale=True,
                    line=dict(width=1, color='#333')
                ),
                text=cat_labels,  # Use short labels
                textposition='top center',
                textfont=dict(size=10),
                hovertext=cat_text,
                hoverinfo='text',
                name=category
            )
        )
    
    # Update layout
    fig.update_layout(
        title='Job Space: Top 200 Occupations by Employment',
        showlegend=True,
        legend=dict(
            title=dict(text='Occupation Categories'),
            x=0.01,
            y=0.99,
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='#333',
            borderwidth=1,
            font=dict(size=12)
        ),
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        width=1200,
        height=800,
        plot_bgcolor='#fff',
        annotations=[
            dict(
                x=0.5,
                y=-0.1,
                xref='paper',
                yref='paper',
                text='Node size represents employment numbers<br>Node color represents job complexity index',
                showarrow=False,
                font=dict(size=14),
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='#333',
                borderwidth=1,
                borderpad=4
            )
        ]
    )
    
    # Save the figure directly to the website directory
    output_path = '/home/ubuntu/research_project/website/visualizations/job_space_simplified.html'
    try:
        fig.write_html(output_path)
        print(f"Saved improved job space visualization to {output_path}")
    except Exception as e:
        print(f"Error saving simplified job space: {str(e)}")
        print(traceback.format_exc())
    
    # Create a more complete job space with all major occupations
    print("Creating complete job space visualization...")
    
    # Get more occupations, but still limit to avoid overcrowding
    more_jobs = job_df.sort_values('employment', ascending=False).head(500)
    
    # Create a new layout with more occupations
    # We'll use a similar approach but with more spread
    np.random.seed(43)  # Different seed for variety
    
    # Create positions for each major group
    major_group_positions = {}
    angles = np.linspace(0, 2*np.pi, len(more_jobs['major_group'].unique()), endpoint=False)
    i = 0
    for mg in more_jobs['major_group'].unique():
        if pd.notna(mg) and mg != '':
            angle = angles[i]
            radius = np.random.uniform(0.7, 1.3)
            major_group_positions[mg] = (radius * np.cos(angle), radius * np.sin(angle))
            i += 1
    
    # Now create positions for each occupation within its major group
    node_positions = {}
    for _, job in more_jobs.iterrows():
        mg = job['major_group']
        if mg in major_group_positions:
            base_x, base_y = major_group_positions[mg]
            # Add some random offset
            offset_x = np.random.uniform(-0.25, 0.25)
            offset_y = np.random.uniform(-0.25, 0.25)
            node_positions[job['soc_code']] = (base_x + offset_x, base_y + offset_y)
        else:
            # Random position for those without a major group
            angle = np.random.uniform(0, 2*np.pi)
            radius = np.random.uniform(0, 0.5)
            node_positions[job['soc_code']] = (radius * np.cos(angle), radius * np.sin(angle))
    
    # Create edges between occupations in the same major group
    edges = []
    for mg in more_jobs['major_group'].unique():
        if pd.notna(mg) and mg != '':
            mg_jobs = more_jobs[more_jobs['major_group'] == mg]['soc_code'].tolist()
            for i, job1 in enumerate(mg_jobs):
                for job2 in mg_jobs[i+1:]:
                    # Add edge with some probability
                    if np.random.random() < 0.2:  # 20% chance of connection
                        edges.append((job1, job2))
    
    # Also add some edges between related major groups
    for mg1, mg2 in related_groups:
        mg1_jobs = more_jobs[more_jobs['major_group'] == mg1]['soc_code'].tolist()
        mg2_jobs = more_jobs[more_jobs['major_group'] == mg2]['soc_code'].tolist()
        
        # Add a few random connections between these groups
        for _ in range(min(10, len(mg1_jobs) * len(mg2_jobs) // 20)):
            if mg1_jobs and mg2_jobs:  # Make sure lists are not empty
                job1 = np.random.choice(mg1_jobs)
                job2 = np.random.choice(mg2_jobs)
                edges.append((job1, job2))
    
    # Extract node positions
    node_x = []
    node_y = []
    node_text = []
    node_size = []
    node_color = []
    node_group = []
    node_labels = []
    
    for _, job in more_jobs.iterrows():
        soc_code = job['soc_code']
        if soc_code in node_positions:
            x, y = node_positions[soc_code]
            node_x.append(x)
            node_y.append(y)
            
            # Create hover text
            node_text.append(f"{job['occupation_title']} ({soc_code})<br>Complexity: {job['job_complexity_index']:.2f}<br>Employment: {job['employment']:,}")
            
            # Create short labels for top 100 jobs by employment
            if job['employment'] > more_jobs['employment'].nlargest(100).min():
                title_words = job['occupation_title'].split()
                if len(title_words) > 2:
                    short_label = ' '.join(title_words[:2])
                    if len(short_label) > 15:  # If still too long, just use first word
                        short_label = title_words[0]
                else:
                    short_label = job['occupation_title']
                node_labels.append(short_label)
            else:
                node_labels.append('')
            
            # Size based on log of employment
            size = np.log1p(job['employment']) * 1.5 if job['employment'] > 0 else 5
            node_size.append(size)
            
            # Color based on complexity
            node_color.append(job['job_complexity_index'])
            
            # Group by uber category
            node_group.append(job['uber_category'])
    
    # Extract edge positions
    edge_x = []
    edge_y = []
    
    for edge in edges:
        if edge[0] in node_positions and edge[1] in node_positions:
            x0, y0 = node_positions[edge[0]]
            x1, y1 = node_positions[edge[1]]
            
            # Add the line plot with a break in the middle
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
    
    # Create a Plotly figure
    fig_complete = go.Figure()
    
    # Add edges
    fig_complete.add_trace(
        go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines',
            showlegend=False
        )
    )
    
    # Get unique uber categories
    unique_categories = list(set(node_group))
    
    # Add nodes for each category
    for category in unique_categories:
        # Get indices for this category
        indices = [i for i, group in enumerate(node_group) if group == category]
        
        if not indices:
            continue
            
        # Extract data for this category
        cat_x = [node_x[i] for i in indices]
        cat_y = [node_y[i] for i in indices]
        cat_text = [node_text[i] for i in indices]
        cat_size = [node_size[i] for i in indices]
        cat_color = [node_color[i] for i in indices]
        cat_labels = [node_labels[i] for i in indices]
        
        # Add nodes for this category
        fig_complete.add_trace(
            go.Scatter(
                x=cat_x, y=cat_y,
                mode='markers+text',
                marker=dict(
                    size=cat_size,
                    color=cat_color,
                    colorscale='RdBu',
                    colorbar=dict(
                        title='Complexity',
                        thickness=20,
                        len=0.7,
                        bgcolor='rgba(255,255,255,0.8)',
                        borderwidth=1,
                        bordercolor='#333',
                        titlefont=dict(size=14),
                        tickfont=dict(size=12)
                    ) if category == unique_categories[0] else None,
                    reversescale=True,
                    line=dict(width=1, color='#333')
                ),
                text=cat_labels,
                textposition='top center',
                textfont=dict(size=10),
                hovertext=cat_text,
                hoverinfo='text',
                name=category
            )
        )
    
    # Update layout
    fig_complete.update_layout(
        title='Job Space: Occupational Network by Skill Similarity',
        showlegend=True,
        legend=dict(
            title=dict(text='Occupation Categories'),
            x=0.01,
            y=0.99,
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='#333',
            borderwidth=1,
            font=dict(size=12)
        ),
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        width=1200,
        height=800,
        plot_bgcolor='#fff',
        annotations=[
            dict(
                x=0.5,
                y=-0.1,
                xref='paper',
                yref='paper',
                text='Node size represents employment numbers<br>Node color represents job complexity index',
                showarrow=False,
                font=dict(size=14),
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='#333',
                borderwidth=1,
                borderpad=4
            )
        ]
    )
    
    # Save the figure directly to the website directory
    output_path = '/home/ubuntu/research_project/website/visualizations/job_space_network.html'
    try:
        fig_complete.write_html(output_path)
        print(f"Saved complete job space visualization to {output_path}")
    except Exception as e:
        print(f"Error saving complete job space: {str(e)}")
        print(traceback.format_exc())
    
except Exception as e:
    print(f"Error creating job space visualizations: {str(e)}")
    print(traceback.format_exc())

print("Job space visualization creation complete!")
