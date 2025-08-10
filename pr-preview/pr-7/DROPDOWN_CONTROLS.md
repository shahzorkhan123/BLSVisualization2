# BLS Visualization Dropdown Controls

This document describes the enhanced dropdown controls added to the BLS (Bureau of Labor Statistics) visualizations.

## New Dropdown Controls

### 1. Year Selection
- **Purpose**: Filter data by specific year
- **Options**: 2020, 2021, 2022, 2023, 2024
- **Default**: 2024
- **Usage**: Select different years to compare labor market data over time

### 2. Treemap Parameter Selection
- **Purpose**: Choose the parameter for treemap sizing
- **Options**: 
  - "Number of Employees" - Size rectangles by employment numbers
  - "GDP (Employees × Avg Salary)" - Size rectangles by calculated GDP contribution
- **Default**: Number of Employees
- **Usage**: Switch between employment-based and economic output-based visualizations

### 3. Vocations Limit
- **Purpose**: Control the number of occupations displayed
- **Options**:
  - "All Vocations" - Show all available occupations
  - "Top 50 Vocations" - Show only the top 50 occupations by employment
  - "Top 500 Vocations" - Show only the top 500 occupations by employment
- **Default**: Top 50 Vocations
- **Usage**: Focus on major occupations or see comprehensive view

### 4. Enhanced Color Options
- **Purpose**: Color treemap rectangles by different metrics
- **Options**:
  - Employment
  - Average Annual Wage
  - Job Complexity Score
- **Usage**: Visualize different aspects of the labor market data
- 
## Data Organization

### CSV Files Structure
The visualization now supports structured CSV data with the following format:

```csv
year,region_type,region,soc_code,occupation_title,major_group_name,employment,annual_mean_wage,gdp,complexity_score
2024,National,United States,15-1252,Software Developers,Computer and Mathematical,1847900,110140,203525346000,0.85
```

### Data Files
- `/data/processed/yearly_job_data.csv` - Multi-year BLS data
- `/treemaps/enhanced_job_data.json` - JSON format with year support
- Existing state-specific files in `/data/states/`

## Implementation Files

### Modified Files
1. `/treemaps/interactive_treemap.html` - Main treemap with full dropdown controls
2. `/visualizations/interactive_job_atlas_updated.html` - Interactive atlas with enhanced controls
3. `/visualizations/gdp_treemap.html` - New GDP-focused treemap

### Key Features Added
- Year-based data filtering
- GDP calculation (Employment × Average Wage)
- Top 50 vocations filtering
- CSV data export functionality
- Enhanced tooltips with more detailed information
- Responsive parameter updating

## Usage Instructions

1. **Select Year**: Choose the year for data analysis
2. **Choose Region**: Select between National, State, or Metropolitan area data
3. **Pick Treemap Parameter**: Decide whether to view by employment or GDP
4. **Set Vocation Limit**: Choose to see all occupations or focus on top 50
5. **Select Color Metric**: Pick the coloring scheme for the visualization
6. **Export Data**: Use the export button to download filtered data as CSV

## Technical Implementation

The dropdown controls work by:
1. Filtering the loaded JSON/CSV data based on user selections
2. Recalculating treemap values (employment vs GDP)
3. Applying vocation limits (top 50 filtering)
4. Updating visualization with new parameters
5. Providing data export functionality

## Data Sources

All data is based on Bureau of Labor Statistics (BLS) Occupational Employment and Wage Statistics (OEWS) surveys, with complexity scores derived from O*NET task and skill requirements.
