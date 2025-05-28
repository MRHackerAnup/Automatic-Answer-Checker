/**
 * Chart utilities and configurations for Automatic Answer Checker
 */

// Define color schemes for charts
const chartColors = {
    primary: '#0d6efd',
    success: '#198754',
    danger: '#dc3545',
    warning: '#ffc107',
    info: '#0dcaf0',
    secondary: '#6c757d',
    light: '#f8f9fa',
    dark: '#212529',
    
    // Color arrays for multiple datasets
    scoreColors: ['#dc3545', '#fd7e14', '#ffc107', '#20c997', '#198754'],
    chartPalette: ['#0d6efd', '#198754', '#dc3545', '#ffc107', '#0dcaf0', '#6c757d']
};

/**
 * Creates a score distribution chart
 * @param {string} elementId - The canvas element ID
 * @param {Object} data - The score distribution data object
 * @param {Object} options - Additional chart options
 */
function createScoreDistributionChart(elementId, data, options = {}) {
    const ctx = document.getElementById(elementId)?.getContext('2d');
    if (!ctx) return;
    
    const defaultOptions = {
        type: 'doughnut',
        data: {
            labels: Object.keys(data),
            datasets: [{
                data: Object.values(data),
                backgroundColor: chartColors.scoreColors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: options.legendPosition || 'right',
                    labels: {
                        font: {
                            size: 11
                        }
                    }
                },
                title: {
                    display: options.showTitle !== false,
                    text: options.title || 'Score Distribution'
                }
            }
        }
    };
    
    // Merge custom options with defaults
    const chartOptions = {
        ...defaultOptions,
        options: {
            ...defaultOptions.options,
            ...options,
            plugins: {
                ...defaultOptions.options.plugins,
                ...(options.plugins || {})
            }
        }
    };
    
    return new Chart(ctx, chartOptions);
}

/**
 * Creates a performance trend line chart
 * @param {string} elementId - The canvas element ID
 * @param {Array} labels - The x-axis labels (dates/exams)
 * @param {Array} scores - The score values
 * @param {Object} options - Additional chart options
 */
function createPerformanceTrendChart(elementId, labels, scores, options = {}) {
    const ctx = document.getElementById(elementId)?.getContext('2d');
    if (!ctx) return;
    
    const defaultOptions = {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: options.dataLabel || 'Score (%)',
                data: scores,
                borderColor: options.lineColor || chartColors.primary,
                backgroundColor: options.fillColor || 'rgba(13, 110, 253, 0.1)',
                fill: true,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: options.showTitle !== false,
                    text: options.title || 'Performance Trend'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Score (%)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: options.xAxisLabel || 'Exam Date'
                    }
                }
            }
        }
    };
    
    // Merge custom options with defaults
    const chartOptions = {
        ...defaultOptions,
        options: {
            ...defaultOptions.options,
            ...options,
            plugins: {
                ...defaultOptions.options.plugins,
                ...(options.plugins || {})
            },
            scales: {
                ...defaultOptions.options.scales,
                ...(options.scales || {})
            }
        }
    };
    
    return new Chart(ctx, chartOptions);
}

/**
 * Creates a bar chart for multiple choice answer distribution
 * @param {string} elementId - The canvas element ID
 * @param {Array} labels - The answer options
 * @param {Array} counts - The count of responses for each option
 * @param {string} correctAnswer - The correct answer option
 * @param {Object} options - Additional chart options
 */
function createAnswerDistributionChart(elementId, labels, counts, correctAnswer, options = {}) {
    const ctx = document.getElementById(elementId)?.getContext('2d');
    if (!ctx) return;
    
    // Create color array, highlighting the correct answer
    const backgroundColor = labels.map(label => 
        label === correctAnswer ? chartColors.success : chartColors.primary
    );
    
    const defaultOptions = {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: options.dataLabel || 'Number of Responses',
                data: counts,
                backgroundColor: backgroundColor
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: options.showTitle !== false,
                    text: options.title || 'Student Answer Choices'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Students'
                    },
                    ticks: {
                        precision: 0
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Answer Options'
                    }
                }
            }
        }
    };
    
    // Merge custom options with defaults
    const chartOptions = {
        ...defaultOptions,
        options: {
            ...defaultOptions.options,
            ...options,
            plugins: {
                ...defaultOptions.options.plugins,
                ...(options.plugins || {})
            },
            scales: {
                ...defaultOptions.options.scales,
                ...(options.scales || {})
            }
        }
    };
    
    return new Chart(ctx, chartOptions);
}

/**
 * Calculates and formats score distribution data
 * @param {Array} scores - Array of numeric scores (0-100)
 * @returns {Object} Formatted score distribution object
 */
function calculateScoreDistribution(scores) {
    const distribution = {
        '0-20%': 0,
        '21-40%': 0,
        '41-60%': 0,
        '61-80%': 0,
        '81-100%': 0
    };
    
    scores.forEach(score => {
        if (score <= 20) {
            distribution['0-20%']++;
        } else if (score <= 40) {
            distribution['21-40%']++;
        } else if (score <= 60) {
            distribution['41-60%']++;
        } else if (score <= 80) {
            distribution['61-80%']++;
        } else {
            distribution['81-100%']++;
        }
    });
    
    return distribution;
}
