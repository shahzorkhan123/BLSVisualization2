/**
 * Treemap visualization functions using Plotly.js
 */

// Create treemap visualization
function createTreemap(data, containerId, options = {}) {
    const {
        year = 2024,
        regionType = 'National',
        region = 'United States',
        parameter = 'employment',
        colorScheme = 'complexity',
        limit = 'top50'
    } = options;

    // Filter data based on criteria
    let filteredData = data.filter(d => 
        d.year === year && 
        d.Region_Type === regionType && 
        d.Region === region
    );

    // Apply limit
    if (limit === 'top50') {
        filteredData = filteredData
            .sort((a, b) => b.TOT_EMP - a.TOT_EMP)
            .slice(0, 50);
    }

    if (filteredData.length === 0) {
        document.getElementById(containerId).innerHTML = '<p>No data available for the selected criteria.</p>';
        return;
    }

    // Prepare data for treemap
    const ids = ['All Jobs', ...filteredData.map(d => d.SOC_Code)];
    const labels = ['All Jobs', ...filteredData.map(d => d.OCC_TITLE)];
    const parents = ['', ...filteredData.map(d => 'All Jobs')];
    
    // Values based on parameter
    let values, colorValues;
    if (parameter === 'employment') {
        values = [filteredData.reduce((sum, d) => sum + d.TOT_EMP, 0), 
                 ...filteredData.map(d => d.TOT_EMP)];
    } else if (parameter === 'gdp') {
        values = [filteredData.reduce((sum, d) => sum + d.GDP, 0), 
                 ...filteredData.map(d => d.GDP)];
    }

    // Color values based on scheme
    if (colorScheme === 'complexity') {
        colorValues = [0, ...filteredData.map(d => d.complexity_score)];
    } else if (colorScheme === 'employment') {
        colorValues = [0, ...filteredData.map(d => d.TOT_EMP)];
    } else if (colorScheme === 'wage') {
        colorValues = [0, ...filteredData.map(d => d.A_MEAN)];
    }

    // Create treemap trace
    const trace = {
        type: 'treemap',
        labels: labels,
        parents: parents,
        values: values,
        ids: ids,
        textinfo: 'label+value+percent root',
        hovertemplate: '<b>%{label}</b><br>' +
                      'Value: %{value}<br>' +
                      'Percentage: %{percentRoot}<br>' +
                      '<extra></extra>',
        marker: {
            colorscale: getColorScale(colorScheme),
            colorbar: {
                title: getColorBarTitle(colorScheme),
                x: 1.02
            },
            line: {
                width: 2,
                color: 'white'
            }
        },
        pathbar: {
            visible: true,
            side: 'top',
            edgeshape: 'round',
            thickness: 20
        }
    };

    // Add color values if specified
    if (colorValues) {
        trace.marker.colorscale = getColorScale(colorScheme);
        trace.text = labels.map((label, i) => {
            if (i === 0) return label;
            const item = filteredData[i - 1];
            return `${label}<br>Complexity: ${item.complexity_score.toFixed(2)}`;
        });
    }

    const layout = {
        title: {
            text: `${parameter === 'employment' ? 'Employment' : 'GDP'} Treemap - ${year} - ${region}`,
            font: { size: 16 }
        },
        font: { size: 12 },
        margin: { t: 50, l: 0, r: 100, b: 0 },
        autosize: true,
        height: 600
    };

    const config = {
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
        displaylogo: false
    };

    Plotly.newPlot(containerId, [trace], layout, config);
    
    return filteredData;
}

// Get color scale based on scheme
function getColorScale(scheme) {
    const scales = {
        complexity: 'Viridis',
        employment: 'Blues', 
        wage: 'Oranges'
    };
    return scales[scheme] || 'Viridis';
}

// Get color bar title
function getColorBarTitle(scheme) {
    const titles = {
        complexity: 'Complexity Score',
        employment: 'Employment',
        wage: 'Average Wage ($)'
    };
    return titles[scheme] || 'Value';
}

// Update treemap with new parameters
function updateTreemap(data, containerId, options) {
    return createTreemap(data, containerId, options);
}