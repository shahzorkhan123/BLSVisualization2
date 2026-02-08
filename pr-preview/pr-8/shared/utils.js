/**
 * Common utility functions for BLS Visualization pages
 */

// CSV parsing utility function
function parseCSV(text) {
    const lines = text.split('\n');
    const headers = lines[0].split(',');
    const data = [];
    
    for (let i = 1; i < lines.length; i++) {
        if (lines[i].trim()) {
            const values = lines[i].split(',');
            const obj = {};
            headers.forEach((header, index) => {
                const value = values[index];
                // Convert numeric fields
                if (['year', 'TOT_EMP', 'A_MEAN', 'GDP', 'complexity_score'].includes(header)) {
                    obj[header] = parseFloat(value);
                } else {
                    obj[header] = value;
                }
            });
            data.push(obj);
        }
    }
    return data;
}

// Data loading utility with fallback support
function loadData(dataUrl, fallbackData) {
    return new Promise((resolve, reject) => {
        // Try to load external data first
        fetch(dataUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.text();
            })
            .then(csvText => {
                const data = parseCSV(csvText);
                resolve(data);
            })
            .catch(error => {
                console.log('External data loading failed, using fallback data:', error);
                // Fall back to embedded data
                resolve(fallbackData);
            });
    });
}

// Export current data as CSV
function exportCurrentData(filteredData, filename) {
    const headers = ['year', 'Region_Type', 'Region', 'SOC_Code', 'OCC_TITLE', 'SOC_Major_Group_Name', 'TOT_EMP', 'A_MEAN', 'GDP', 'complexity_score'];
    let csvContent = headers.join(',') + '\n';
    
    filteredData.forEach(item => {
        const row = [
            item.year,
            item.Region_Type,
            item.Region,
            item.SOC_Code,
            `"${item.OCC_TITLE}"`,
            `"${item.SOC_Major_Group_Name}"`,
            item.TOT_EMP,
            item.A_MEAN,
            item.GDP,
            item.complexity_score
        ];
        csvContent += row.join(',') + '\n';
    });
    
    // Download file
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

// Get unique values from array of objects
function getUniqueValues(data, key) {
    return [...new Set(data.map(item => item[key]))].sort();
}

// Filter data by multiple criteria
function filterData(data, filters) {
    return data.filter(item => {
        return Object.keys(filters).every(key => {
            if (filters[key] === 'all' || filters[key] === '' || filters[key] === null) {
                return true;
            }
            return item[key] === filters[key];
        });
    });
}

// Update dropdown options
function updateDropdown(selectId, options, selectedValue = null) {
    const select = document.getElementById(selectId);
    if (!select) return;
    
    // Clear existing options
    select.innerHTML = '';
    
    // Add options
    options.forEach(option => {
        const optionElement = document.createElement('option');
        optionElement.value = option;
        optionElement.textContent = option;
        if (selectedValue && option === selectedValue) {
            optionElement.selected = true;
        }
        select.appendChild(optionElement);
    });
}

// Color schemes for visualizations
const ColorSchemes = {
    complexity: {
        name: 'Complexity',
        scale: 'Viridis',
        getColor: (value, min, max) => {
            const normalized = (value - min) / (max - min);
            return `hsl(${240 - normalized * 240}, 70%, ${50 + normalized * 30}%)`;
        }
    },
    employment: {
        name: 'Employment',
        scale: 'Blues',
        getColor: (value, min, max) => {
            const normalized = (value - min) / (max - min);
            return `hsl(210, ${70 + normalized * 30}%, ${80 - normalized * 30}%)`;
        }
    },
    wage: {
        name: 'Wage',
        scale: 'Oranges',
        getColor: (value, min, max) => {
            const normalized = (value - min) / (max - min);
            return `hsl(30, ${70 + normalized * 30}%, ${80 - normalized * 30}%)`;
        }
    }
};

// --- Lazy-loading support for split data files ---

var BLS_REGION_CACHE = {};

function loadRegionData(slug, year, country, callback) {
    var key = year + '.' + slug + '.' + country;
    if (BLS_REGION_CACHE[key]) {
        callback(BLS_REGION_CACHE[key]);
        return;
    }

    window.BLS_LOAD = function(rows) {
        var expanded = expandCompactRows(rows, slug, year);
        BLS_REGION_CACHE[key] = expanded;
        callback(expanded);
    };

    var script = document.createElement('script');
    script.src = '../data/regions/' + key + '.data.js';
    script.onerror = function() { callback([]); };
    document.head.appendChild(script);
}

function expandCompactRows(rows, slug, year) {
    var meta = window.BLS_META;
    if (!meta) return [];

    // Find region type and display name from slug
    var regionType = '';
    var regionName = '';
    var types = ['National', 'State', 'Metro'];
    for (var t = 0; t < types.length; t++) {
        var entries = meta.regions[types[t]] || [];
        for (var e = 0; e < entries.length; e++) {
            if (entries[e][0] === slug) {
                regionType = types[t];
                regionName = entries[e][1];
                break;
            }
        }
        if (regionType) break;
    }

    var result = [];
    for (var i = 0; i < rows.length; i++) {
        var row = rows[i];
        var occIdx = row[0];
        var occ = meta.occ[occIdx];
        result.push({
            year: year,
            Region_Type: regionType,
            Region: regionName,
            SOC_Code: occ[0],
            OCC_TITLE: occ[1],
            SOC_Major_Group: occ[2],
            SOC_Major_Group_Name: occ[3],
            TOT_EMP: row[1],
            A_MEAN: row[2],
            GDP: row[3],
            complexity_score: row[4]
        });
    }
    return result;
}

function findManifestEntry(regionType, regionName) {
    var meta = window.BLS_META;
    if (!meta || !meta.regions || !meta.regions[regionType]) return null;
    var entries = meta.regions[regionType];
    for (var i = 0; i < entries.length; i++) {
        if (entries[i][1] === regionName) {
            return { slug: entries[i][0], name: entries[i][1], country: entries[i][2] };
        }
    }
    return null;
}

// Debounce function for performance
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}