/**
 * Job data for BLS Visualizations
 * This file loads data from CSV files and provides a CORS-free interface
 * Format: JSONP-style to avoid CORS issues with static hosting
 * Last updated: 2025-06-30 02:19:21
 */

// Global data loader that reads from CSV files
window.BLS_DATA = {
    lastUpdated: '2025-06-30',
    dataSource: 'BLS OES Data + O*NET Complexity Scores',
    
    // Main dataset - loaded from CSV files
    jobData: null,
    
    // Load data from CSV file
    async loadData() {
        if (this.jobData) return this.jobData; // Return cached data if already loaded
        
        try {
            // Load the main occupational data CSV
            const response = await fetch('./data/us_occupational_data.csv');
            const csvText = await response.text();
            
            // Parse CSV data
            this.jobData = this.parseCSV(csvText);
            return this.jobData;
        } catch (error) {
            console.error('Failed to load job data:', error);
            // Fallback to sample data for demo purposes
            this.jobData = [
        {
                "year": 2024,
                "Region_Type": "National",
                "Region": "United States",
                "SOC_Code": "15-1252",
                "OCC_TITLE": "Software Developers",
                "SOC_Major_Group_Name": "Computer and Mathematical",
                "TOT_EMP": 1847900,
                "A_MEAN": 110140,
                "GDP": 203525346000,
                "complexity_score": 0.85
        },
        {
                "year": 2024,
                "Region_Type": "National",
                "Region": "United States",
                "SOC_Code": "29-1141",
                "OCC_TITLE": "Registered Nurses",
                "SOC_Major_Group_Name": "Healthcare Practitioners",
                "TOT_EMP": 3175390,
                "A_MEAN": 80010,
                "GDP": 254095239900,
                "complexity_score": 0.72
        },
        {
                "year": 2024,
                "Region_Type": "National",
                "Region": "United States",
                "SOC_Code": "25-2021",
                "OCC_TITLE": "Elementary School Teachers",
                "SOC_Major_Group_Name": "Education Training and Library",
                "TOT_EMP": 1424890,
                "A_MEAN": 60940,
                "GDP": 86824851600,
                "complexity_score": 0.68
        },
        {
                "year": 2023,
                "Region_Type": "National",
                "Region": "United States",
                "SOC_Code": "15-1252",
                "OCC_TITLE": "Software Developers",
                "SOC_Major_Group_Name": "Computer and Mathematical",
                "TOT_EMP": 1795600,
                "A_MEAN": 107510,
                "GDP": 192899356000,
                "complexity_score": 0.85
        },
        {
                "year": 2023,
                "Region_Type": "National",
                "Region": "United States",
                "SOC_Code": "29-1141",
                "OCC_TITLE": "Registered Nurses",
                "SOC_Major_Group_Name": "Healthcare Practitioners",
                "TOT_EMP": 3100250,
                "A_MEAN": 78500,
                "GDP": 243369625000,
                "complexity_score": 0.71
        },
        {
                "year": 2024,
                "Region_Type": "State",
                "Region": "California",
                "SOC_Code": "15-1252",
                "OCC_TITLE": "Software Developers",
                "SOC_Major_Group_Name": "Computer and Mathematical",
                "TOT_EMP": 425000,
                "A_MEAN": 145000,
                "GDP": 61625000000,
                "complexity_score": 0.85
        },
        {
                "year": 2024,
                "Region_Type": "State",
                "Region": "Texas",
                "SOC_Code": "15-1252",
                "OCC_TITLE": "Software Developers",
                "SOC_Major_Group_Name": "Computer and Mathematical",
                "TOT_EMP": 195000,
                "A_MEAN": 108000,
                "GDP": 21060000000,
                "complexity_score": 0.85
        },
        {
                "year": 2024,
                "Region_Type": "Metropolitan",
                "Region": "New York-Newark-Jersey City, NY-NJ-PA",
                "SOC_Code": "15-1252",
                "OCC_TITLE": "Software Developers",
                "SOC_Major_Group_Name": "Computer and Mathematical",
                "TOT_EMP": 156000,
                "A_MEAN": 135000,
                "GDP": 21060000000,
                "complexity_score": 0.85
        }
                {
                    occupation_code: "15-1252",
                    occupation_title: "Software Developers", 
                    employment: 1847900,
                    mean_annual_wage: 110140,
                    complexity_score: 0.85
                },
                {
                    occupation_code: "29-1141",
                    occupation_title: "Registered Nurses",
                    employment: 3175390, 
                    mean_annual_wage: 81220,
                    complexity_score: 0.7
                },
                {
                    occupation_code: "25-2031",
                    occupation_title: "Secondary School Teachers",
                    employment: 1057090, 
                    mean_annual_wage: 65220,
                    complexity_score: 0.68
                }
        }
    },
    
    // Parse CSV text into array of objects
    parseCSV(csvText) {
        const lines = csvText.trim().split('\n');
        const headers = lines[0].split(',');
        const data = [];
        
        for (let i = 1; i < lines.length; i++) {
            const values = lines[i].split(',');
            const row = {};
            
            headers.forEach((header, index) => {
                const value = values[index];
                // Convert numeric fields
                if (header === 'employment' || header === 'mean_annual_wage' || header === 'complexity_score') {
                    row[header] = parseFloat(value) || 0;
                } else {
                    row[header] = value;
                }
            });
            
            data.push(row);
        }
        
        return data;
    },
    
    // Metadata for dropdowns and filters
    metadata: {
        "years": [
                2023,
                2024
        ],
        "regionTypes": [
                "Metropolitan",
                "National",
                "State"
        ],
        "parameters": [
                "employment",
                "gdp"
        ],
        "colorSchemes": [
                "complexity",
                "employment",
                "wage"
        ],
        "limits": [
                "all",
                "top50"
        ],
        "regions": {
                "Metropolitan": [
                        "New York-Newark-Jersey City, NY-NJ-PA"
                ],
                "National": [
                        "United States"
                ],
                "State": [
                        "California",
                        "Texas"
                ]
        }
    }
};

// Helper function to get data (async now)
window.getBLSData = async function() {
    return await window.BLS_DATA.loadData();
};

// Helper function to get metadata
window.getBLSMetadata = function() {
    return window.BLS_DATA.metadata;
};

// Helper function for external updates (used by Python scripts)
window.updateBLSData = function(newData, newMetadata) {
    window.BLS_DATA.jobData = newData;
    if (newMetadata) {
        window.BLS_DATA.metadata = newMetadata;
    }
    window.BLS_DATA.lastUpdated = new Date().toISOString().split('T')[0];
    
    // Trigger update event for listening components
    const event = new CustomEvent('blsDataUpdated', { 
        detail: { data: newData, metadata: newMetadata } 
    });
    document.dispatchEvent(event);
};

console.log('BLS Data loader initialized - use getBLSData() to load data from CSV');