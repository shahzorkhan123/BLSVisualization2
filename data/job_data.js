/**
 * Job data for BLS Visualizations
 * This file can be updated by Python scripts without modifying HTML files
 * Format: JSONP-style to avoid CORS issues with static hosting
 * Last updated: 2025-06-30 02:13:13
 */

// Global data object that can be updated by Python scripts
window.BLS_DATA = {
    lastUpdated: '2025-06-30',
    dataSource: 'BLS OES Data + O*NET Complexity Scores',
    
    // Main dataset - updated by Python scripts
    jobData: [
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
                "year": 2024,
                "Region_Type": "National",
                "Region": "United States",
                "SOC_Code": "41-2031",
                "OCC_TITLE": "Retail Salespersons",
                "SOC_Major_Group_Name": "Sales and Related",
                "TOT_EMP": 4155020,
                "A_MEAN": 27080,
                "GDP": 112545342400,
                "complexity_score": 0.42
        },
        {
                "year": 2024,
                "Region_Type": "State",
                "Region": "California",
                "SOC_Code": "15-1252",
                "OCC_TITLE": "Software Developers",
                "SOC_Major_Group_Name": "Computer and Mathematical",
                "TOT_EMP": 395280,
                "A_MEAN": 142170,
                "GDP": 56214542960,
                "complexity_score": 0.87
        },
        {
                "year": 2024,
                "Region_Type": "State",
                "Region": "California",
                "SOC_Code": "29-1141",
                "OCC_TITLE": "Registered Nurses",
                "SOC_Major_Group_Name": "Healthcare Practitioners",
                "TOT_EMP": 330520,
                "A_MEAN": 124000,
                "GDP": 40984480000,
                "complexity_score": 0.74
        },
        {
                "year": 2023,
                "Region_Type": "National",
                "Region": "United States",
                "SOC_Code": "15-1252",
                "OCC_TITLE": "Software Developers",
                "SOC_Major_Group_Name": "Computer and Mathematical",
                "TOT_EMP": 1795600,
                "A_MEAN": 107800,
                "GDP": 193659280000,
                "complexity_score": 0.84
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
        }
],
    
    // Metadata for dropdowns and filters
    metadata: {
        "years": [
                2023,
                2024
        ],
        "regionTypes": [
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
                "National": [
                        "United States"
                ],
                "State": [
                        "California"
                ]
        }
}
};

// Helper function to get data
window.getBLSData = function() {
    return window.BLS_DATA.jobData;
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

console.log('BLS Data loaded:', window.BLS_DATA.jobData.length, 'records');