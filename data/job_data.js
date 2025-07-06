/**
 * Job data for BLS Visualizations
 * This file contains embedded job data in JSONP format to avoid CORS issues
 * Format: Static JavaScript data for CORS-free access
 * Last updated: 2025-06-30 02:19:21
 */

// Embedded job data - CORS-free approach
window.BLS_DATA = {
    lastUpdated: '2025-06-30',
    dataSource: 'BLS OES Data + O*NET Complexity Scores',
    
    // Main dataset - embedded directly to avoid CORS issues
    jobData: [
        {
            "year": 2024,
            "Region_Type": "National",
            "Region": "United States",
            "SOC_Code": "11-0000",
            "OCC_TITLE": "Management Occupations",
            "SOC_Major_Group": "11",
            "SOC_Major_Group_Name": "Management",
            "TOT_EMP": 9270000,
            "A_MEAN": 126480,
            "GDP": 1173000000000,
            "complexity_score": 0.85
        },
        {
            "year": 2024,
            "Region_Type": "National",
            "Region": "United States",
            "SOC_Code": "13-0000",
            "OCC_TITLE": "Business and Financial Operations",
            "SOC_Major_Group": "13",
            "SOC_Major_Group_Name": "Business and Financial",
            "TOT_EMP": 8916000,
            "A_MEAN": 79940,
            "GDP": 712800000000,
            "complexity_score": 0.75
        },
        {
            "year": 2024,
            "Region_Type": "National",
            "Region": "United States",
            "SOC_Code": "15-0000",
            "OCC_TITLE": "Computer and Mathematical",
            "SOC_Major_Group": "15",
            "SOC_Major_Group_Name": "Computer and Mathematical",
            "TOT_EMP": 4552000,
            "A_MEAN": 99860,
            "GDP": 454700000000,
            "complexity_score": 0.82
        },
        {
            "year": 2024,
            "Region_Type": "National",
            "Region": "United States",
            "SOC_Code": "17-0000",
            "OCC_TITLE": "Architecture and Engineering",
            "SOC_Major_Group": "17",
            "SOC_Major_Group_Name": "Architecture and Engineering",
            "TOT_EMP": 2449000,
            "A_MEAN": 90300,
            "GDP": 221200000000,
            "complexity_score": 0.80
        },
        {
            "year": 2024,
            "Region_Type": "National",
            "Region": "United States",
            "SOC_Code": "19-0000",
            "OCC_TITLE": "Life, Physical, and Social Science",
            "SOC_Major_Group": "19",
            "SOC_Major_Group_Name": "Life, Physical, and Social Science",
            "TOT_EMP": 1288000,
            "A_MEAN": 80730,
            "GDP": 104000000000,
            "complexity_score": 0.78
        },
        {
            "year": 2024,
            "Region_Type": "National",
            "Region": "United States",
            "SOC_Code": "21-0000",
            "OCC_TITLE": "Community and Social Service",
            "SOC_Major_Group": "21",
            "SOC_Major_Group_Name": "Community and Social Service",
            "TOT_EMP": 2321000,
            "A_MEAN": 53480,
            "GDP": 124100000000,
            "complexity_score": 0.65
        },
        {
            "year": 2024,
            "Region_Type": "National",
            "Region": "United States",
            "SOC_Code": "23-0000",
            "OCC_TITLE": "Legal Occupations",
            "SOC_Major_Group": "23",
            "SOC_Major_Group_Name": "Legal",
            "TOT_EMP": 1247000,
            "A_MEAN": 112320,
            "GDP": 140100000000,
            "complexity_score": 0.83
        },
        {
            "year": 2024,
            "Region_Type": "National",
            "Region": "United States",
            "SOC_Code": "25-0000",
            "OCC_TITLE": "Educational Instruction",
            "SOC_Major_Group": "25",
            "SOC_Major_Group_Name": "Educational Instruction",
            "TOT_EMP": 8636000,
            "A_MEAN": 63010,
            "GDP": 544000000000,
            "complexity_score": 0.70
        },
        {
            "year": 2024,
            "Region_Type": "National",
            "Region": "United States",
            "SOC_Code": "27-0000",
            "OCC_TITLE": "Arts, Design, Entertainment",
            "SOC_Major_Group": "27",
            "SOC_Major_Group_Name": "Arts, Design, Entertainment",
            "TOT_EMP": 1951000,
            "A_MEAN": 66100,
            "GDP": 129000000000,
            "complexity_score": 0.68
        },
        {
            "year": 2024,
            "Region_Type": "National",
            "Region": "United States",
            "SOC_Code": "29-0000",
            "OCC_TITLE": "Healthcare Practitioner",
            "SOC_Major_Group": "29",
            "SOC_Major_Group_Name": "Healthcare Practitioner",
            "TOT_EMP": 9043000,
            "A_MEAN": 94350,
            "GDP": 853300000000,
            "complexity_score": 0.76
        }
    ],
    
    // Simple synchronous data access - no CORS issues
    getData() {
        console.log('BLS Data loaded successfully - ', this.jobData.length, 'records available');
        return this.jobData;
    },
    
    // Metadata for dropdown controls and filtering
    metadata: {
        "years": [2024],
        "regionTypes": ["National", "State", "Metropolitan"],
        "parameters": ["complexity", "employment", "wage"],
        "limits": ["all", "top50"],
        "regions": {
            "Metropolitan": ["New York-Newark-Jersey City, NY-NJ-PA"],
            "National": ["United States"],
            "State": ["California", "Texas"]
        }
    }
};

// Helper function to get data (synchronous - no CORS issues)
window.getBLSData = function() {
    return window.BLS_DATA.getData();
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

console.log('BLS Data loader initialized - use getBLSData() to access embedded data (CORS-free)');