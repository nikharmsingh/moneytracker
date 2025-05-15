// Enhanced Data Visualization
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all charts when the page loads
    initializeCharts();
    
    // Re-initialize charts when window is resized for responsiveness
    window.addEventListener('resize', function() {
        // Use debounce to prevent excessive redraws
        clearTimeout(window.resizeTimer);
        window.resizeTimer = setTimeout(function() {
            initializeCharts();
        }, 250);
    });
});

function initializeCharts() {
    // Check if we're on a page with charts
    if (document.getElementById('expenseChart')) {
        initializeExpenseChart();
    }
    
    if (document.getElementById('categoryChart')) {
        initializeCategoryChart();
    }
    
    if (document.getElementById('trendChart')) {
        initializeTrendChart();
    }
    
    if (document.getElementById('budgetChart')) {
        initializeBudgetChart();
    }
    
    if (document.getElementById('savingsChart')) {
        initializeSavingsChart();
    }
}

function initializeExpenseChart() {
    const ctx = document.getElementById('expenseChart').getContext('2d');
    
    // Get data from the data attributes
    const chartData = JSON.parse(document.getElementById('expenseChart').dataset.chartData || '{}');
    const labels = chartData.labels || [];
    const expenseData = chartData.expenses || [];
    const incomeData = chartData.income || [];
    
    // Check if we have existing chart instance and destroy it
    if (window.expenseChart instanceof Chart) {
        window.expenseChart.destroy();
    }
    
    // Create new chart
    window.expenseChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Expenses',
                    data: expenseData,
                    backgroundColor: 'rgba(255, 99, 132, 0.7)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Income',
                    data: incomeData,
                    backgroundColor: 'rgba(75, 192, 192, 0.7)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += new Intl.NumberFormat('en-US', { 
                                    style: 'currency', 
                                    currency: 'USD',
                                    minimumFractionDigits: 0,
                                    maximumFractionDigits: 0
                                }).format(context.parsed.y);
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    }
                },
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return new Intl.NumberFormat('en-US', { 
                                style: 'currency', 
                                currency: 'USD',
                                minimumFractionDigits: 0,
                                maximumFractionDigits: 0
                            }).format(value);
                        }
                    }
                }
            }
        }
    });
}

function initializeCategoryChart() {
    const ctx = document.getElementById('categoryChart').getContext('2d');
    
    // Get data from the data attributes
    const chartData = JSON.parse(document.getElementById('categoryChart').dataset.chartData || '{}');
    const labels = chartData.labels || [];
    const data = chartData.data || [];
    
    // Generate colors for each category
    const backgroundColors = generateColorPalette(labels.length);
    
    // Check if we have existing chart instance and destroy it
    if (window.categoryChart instanceof Chart) {
        window.categoryChart.destroy();
    }
    
    // Create new chart
    window.categoryChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: backgroundColors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed !== null) {
                                label += new Intl.NumberFormat('en-US', { 
                                    style: 'currency', 
                                    currency: 'USD',
                                    minimumFractionDigits: 0,
                                    maximumFractionDigits: 0
                                }).format(context.parsed);
                                
                                // Add percentage
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = Math.round((context.parsed / total) * 100);
                                label += ` (${percentage}%)`;
                            }
                            return label;
                        }
                    }
                }
            }
        }
    });
}

function initializeTrendChart() {
    const ctx = document.getElementById('trendChart').getContext('2d');
    
    // Get data from the data attributes
    const chartData = JSON.parse(document.getElementById('trendChart').dataset.chartData || '{}');
    const labels = chartData.labels || [];
    const expenseData = chartData.expenses || [];
    const incomeData = chartData.income || [];
    const savingsData = chartData.savings || [];
    
    // Check if we have existing chart instance and destroy it
    if (window.trendChart instanceof Chart) {
        window.trendChart.destroy();
    }
    
    // Create new chart
    window.trendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Expenses',
                    data: expenseData,
                    borderColor: 'rgba(255, 99, 132, 1)',
                    backgroundColor: 'rgba(255, 99, 132, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Income',
                    data: incomeData,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Savings',
                    data: savingsData,
                    borderColor: 'rgba(54, 162, 235, 1)',
                    backgroundColor: 'rgba(54, 162, 235, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += new Intl.NumberFormat('en-US', { 
                                    style: 'currency', 
                                    currency: 'USD',
                                    minimumFractionDigits: 0,
                                    maximumFractionDigits: 0
                                }).format(context.parsed.y);
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    }
                },
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return new Intl.NumberFormat('en-US', { 
                                style: 'currency', 
                                currency: 'USD',
                                minimumFractionDigits: 0,
                                maximumFractionDigits: 0
                            }).format(value);
                        }
                    }
                }
            }
        }
    });
}

function initializeBudgetChart() {
    const ctx = document.getElementById('budgetChart').getContext('2d');
    
    // Get data from the data attributes
    const chartData = JSON.parse(document.getElementById('budgetChart').dataset.chartData || '{}');
    const labels = chartData.labels || [];
    const actualData = chartData.actual || [];
    const budgetData = chartData.budget || [];
    
    // Check if we have existing chart instance and destroy it
    if (window.budgetChart instanceof Chart) {
        window.budgetChart.destroy();
    }
    
    // Create new chart
    window.budgetChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Actual Spending',
                    data: actualData,
                    backgroundColor: actualData.map((value, index) => {
                        // Red if over budget, green if under
                        return value > budgetData[index] ? 
                            'rgba(255, 99, 132, 0.7)' : 
                            'rgba(75, 192, 192, 0.7)';
                    }),
                    borderColor: actualData.map((value, index) => {
                        return value > budgetData[index] ? 
                            'rgba(255, 99, 132, 1)' : 
                            'rgba(75, 192, 192, 1)';
                    }),
                    borderWidth: 1
                },
                {
                    label: 'Budget',
                    data: budgetData,
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1,
                    // Make this a line on top of the bars
                    type: 'line',
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += new Intl.NumberFormat('en-US', { 
                                    style: 'currency', 
                                    currency: 'USD',
                                    minimumFractionDigits: 0,
                                    maximumFractionDigits: 0
                                }).format(context.parsed.y);
                            }
                            return label;
                        },
                        afterLabel: function(context) {
                            // Only add this for the actual spending dataset
                            if (context.datasetIndex === 0) {
                                const actual = context.parsed.y;
                                const budget = budgetData[context.dataIndex];
                                const diff = budget - actual;
                                const percentage = Math.round((actual / budget) * 100);
                                
                                if (diff >= 0) {
                                    return `${percentage}% of budget (${new Intl.NumberFormat('en-US', { 
                                        style: 'currency', 
                                        currency: 'USD',
                                        minimumFractionDigits: 0,
                                        maximumFractionDigits: 0
                                    }).format(diff)} under budget)`;
                                } else {
                                    return `${percentage}% of budget (${new Intl.NumberFormat('en-US', { 
                                        style: 'currency', 
                                        currency: 'USD',
                                        minimumFractionDigits: 0,
                                        maximumFractionDigits: 0
                                    }).format(Math.abs(diff))} over budget)`;
                                }
                            }
                            return null;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    }
                },
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return new Intl.NumberFormat('en-US', { 
                                style: 'currency', 
                                currency: 'USD',
                                minimumFractionDigits: 0,
                                maximumFractionDigits: 0
                            }).format(value);
                        }
                    }
                }
            }
        }
    });
}

function initializeSavingsChart() {
    const ctx = document.getElementById('savingsChart').getContext('2d');
    
    // Get data from the data attributes
    const chartData = JSON.parse(document.getElementById('savingsChart').dataset.chartData || '{}');
    const labels = chartData.labels || [];
    const data = chartData.data || [];
    
    // Check if we have existing chart instance and destroy it
    if (window.savingsChart instanceof Chart) {
        window.savingsChart.destroy();
    }
    
    // Calculate cumulative savings
    const cumulativeData = [];
    let sum = 0;
    for (let i = 0; i < data.length; i++) {
        sum += data[i];
        cumulativeData.push(sum);
    }
    
    // Create new chart
    window.savingsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Monthly Savings',
                    data: data,
                    backgroundColor: 'rgba(75, 192, 192, 0.7)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 2,
                    type: 'bar'
                },
                {
                    label: 'Cumulative Savings',
                    data: cumulativeData,
                    backgroundColor: 'rgba(54, 162, 235, 0.1)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 2,
                    type: 'line',
                    fill: true,
                    tension: 0.4,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += new Intl.NumberFormat('en-US', { 
                                    style: 'currency', 
                                    currency: 'USD',
                                    minimumFractionDigits: 0,
                                    maximumFractionDigits: 0
                                }).format(context.parsed.y);
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    }
                },
                y: {
                    beginAtZero: true,
                    position: 'left',
                    ticks: {
                        callback: function(value) {
                            return new Intl.NumberFormat('en-US', { 
                                style: 'currency', 
                                currency: 'USD',
                                minimumFractionDigits: 0,
                                maximumFractionDigits: 0
                            }).format(value);
                        }
                    }
                },
                y1: {
                    beginAtZero: true,
                    position: 'right',
                    grid: {
                        drawOnChartArea: false
                    },
                    ticks: {
                        callback: function(value) {
                            return new Intl.NumberFormat('en-US', { 
                                style: 'currency', 
                                currency: 'USD',
                                minimumFractionDigits: 0,
                                maximumFractionDigits: 0
                            }).format(value);
                        }
                    }
                }
            }
        }
    });
}

// Helper function to generate a color palette
function generateColorPalette(count) {
    const baseColors = [
        'rgba(255, 99, 132, 0.7)',   // Red
        'rgba(54, 162, 235, 0.7)',   // Blue
        'rgba(255, 206, 86, 0.7)',   // Yellow
        'rgba(75, 192, 192, 0.7)',   // Green
        'rgba(153, 102, 255, 0.7)',  // Purple
        'rgba(255, 159, 64, 0.7)',   // Orange
        'rgba(199, 199, 199, 0.7)',  // Gray
        'rgba(83, 102, 255, 0.7)',   // Indigo
        'rgba(255, 99, 255, 0.7)',   // Pink
        'rgba(0, 162, 150, 0.7)'     // Teal
    ];
    
    // If we need more colors than in our base set, generate them
    if (count <= baseColors.length) {
        return baseColors.slice(0, count);
    } else {
        const colors = [...baseColors];
        for (let i = baseColors.length; i < count; i++) {
            const r = Math.floor(Math.random() * 255);
            const g = Math.floor(Math.random() * 255);
            const b = Math.floor(Math.random() * 255);
            colors.push(`rgba(${r}, ${g}, ${b}, 0.7)`);
        }
        return colors;
    }
}