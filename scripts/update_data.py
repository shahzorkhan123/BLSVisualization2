#!/usr/bin/env python3
"""
BLS Data Updater Script

This script updates the job_data.js file with new data from CSV files,
allowing Python-based data updates without modifying HTML files.

Usage:
    python update_data.py --csv enhanced_job_data.csv
    python update_data.py --parquet job_data.parquet --year 2024
"""

import argparse
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import os


def csv_to_js_data(csv_file):
    """Convert CSV file to JavaScript data format."""
    try:
        df = pd.read_csv(csv_file)
        
        # Ensure required columns exist
        required_cols = ['year', 'Region_Type', 'Region', 'SOC_Code', 'OCC_TITLE', 
                        'SOC_Major_Group_Name', 'TOT_EMP', 'A_MEAN', 'GDP', 'complexity_score']
        
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            print(f"Warning: Missing columns: {missing_cols}")
        
        # Convert to records
        records = df.to_dict('records')
        return records
        
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return []


def parquet_to_js_data(parquet_file, year_filter=None):
    """Convert Parquet file to JavaScript data format."""
    try:
        df = pd.read_parquet(parquet_file)
        
        if year_filter:
            df = df[df['year'] == year_filter]
        
        # Convert to records
        records = df.to_dict('records')
        return records
        
    except Exception as e:
        print(f"Error reading Parquet file: {e}")
        return []


def generate_metadata(data):
    """Generate metadata for dropdowns and filters."""
    df = pd.DataFrame(data)
    
    metadata = {
        'years': sorted(df['year'].unique().tolist()) if 'year' in df.columns else [2024],
        'regionTypes': sorted(df['Region_Type'].unique().tolist()) if 'Region_Type' in df.columns else ['National'],
        'parameters': ['employment', 'gdp'],
        'colorSchemes': ['complexity', 'employment', 'wage'],
        'limits': ['all', 'top50']
    }
    
    # Generate region mapping
    regions = {}
    if 'Region_Type' in df.columns and 'Region' in df.columns:
        for region_type in metadata['regionTypes']:
            regions[region_type] = sorted(
                df[df['Region_Type'] == region_type]['Region'].unique().tolist()
            )
    else:
        regions = {'National': ['United States']}
    
    metadata['regions'] = regions
    return metadata


def update_js_data_file(data, metadata, output_file):
    """Update the JavaScript data file with new data."""
    
    # Generate JavaScript content
    js_content = f'''/**
 * Job data for BLS Visualizations
 * This file can be updated by Python scripts without modifying HTML files
 * Format: JSONP-style to avoid CORS issues with static hosting
 * Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
 */

// Global data object that can be updated by Python scripts
window.BLS_DATA = {{
    lastUpdated: '{datetime.now().strftime('%Y-%m-%d')}',
    dataSource: 'BLS OES Data + O*NET Complexity Scores',
    
    // Main dataset - updated by Python scripts
    jobData: {json.dumps(data, indent=8)},
    
    // Metadata for dropdowns and filters
    metadata: {json.dumps(metadata, indent=8)}
}};

// Helper function to get data
window.getBLSData = function() {{
    return window.BLS_DATA.jobData;
}};

// Helper function to get metadata
window.getBLSMetadata = function() {{
    return window.BLS_DATA.metadata;
}};

// Helper function for external updates (used by Python scripts)
window.updateBLSData = function(newData, newMetadata) {{
    window.BLS_DATA.jobData = newData;
    if (newMetadata) {{
        window.BLS_DATA.metadata = newMetadata;
    }}
    window.BLS_DATA.lastUpdated = new Date().toISOString().split('T')[0];
    
    // Trigger update event for listening components
    const event = new CustomEvent('blsDataUpdated', {{ 
        detail: {{ data: newData, metadata: newMetadata }} 
    }});
    document.dispatchEvent(event);
}};

console.log('BLS Data loaded:', window.BLS_DATA.jobData.length, 'records');'''

    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print(f"Updated {output_file} with {len(data)} records")


def main():
    parser = argparse.ArgumentParser(description='Update BLS data for visualizations')
    parser.add_argument('--csv', help='Input CSV file path')
    parser.add_argument('--parquet', help='Input Parquet file path')
    parser.add_argument('--year', type=int, help='Filter data by year (for Parquet)')
    parser.add_argument('--output', default='data/job_data.js', help='Output JavaScript file')
    
    args = parser.parse_args()
    
    if not args.csv and not args.parquet:
        print("Error: Either --csv or --parquet must be specified")
        return
    
    # Load data
    if args.csv:
        data = csv_to_js_data(args.csv)
        print(f"Loaded {len(data)} records from CSV: {args.csv}")
    elif args.parquet:
        data = parquet_to_js_data(args.parquet, args.year)
        print(f"Loaded {len(data)} records from Parquet: {args.parquet}")
    
    if not data:
        print("Error: No data loaded")
        return
    
    # Generate metadata
    metadata = generate_metadata(data)
    print(f"Generated metadata: {len(metadata['years'])} years, {len(metadata['regionTypes'])} region types")
    
    # Create output directory if it doesn't exist
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Update JavaScript file
    update_js_data_file(data, metadata, args.output)
    
    print("Data update completed successfully!")


if __name__ == '__main__':
    main()