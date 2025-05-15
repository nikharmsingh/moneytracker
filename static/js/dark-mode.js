// Dark Mode Functionality
document.addEventListener('DOMContentLoaded', function() {
    // Check for saved dark mode preference
    const darkModeEnabled = localStorage.getItem('darkModeEnabled') === 'true';
    
    // Apply dark mode if enabled
    if (darkModeEnabled) {
        document.body.classList.add('dark-mode');
        document.getElementById('darkModeToggle').checked = true;
    }
    
    // Toggle dark mode when switch is clicked
    document.getElementById('darkModeToggle').addEventListener('change', function() {
        if (this.checked) {
            document.body.classList.add('dark-mode');
            localStorage.setItem('darkModeEnabled', 'true');
            
            // Update chart colors if charts exist
            updateChartsForDarkMode(true);
        } else {
            document.body.classList.remove('dark-mode');
            localStorage.setItem('darkModeEnabled', 'false');
            
            // Update chart colors if charts exist
            updateChartsForDarkMode(false);
        }
    });
    
    // Initialize charts with appropriate colors based on current mode
    if (darkModeEnabled) {
        updateChartsForDarkMode(true);
    }
});

// Function to update chart colors for dark mode
function updateChartsForDarkMode(isDarkMode) {
    // Check if Chart is defined (charts.js is loaded)
    if (typeof Chart !== 'undefined') {
        // Update default chart colors for dark mode
        Chart.defaults.color = isDarkMode ? '#e0e0e0' : '#666';
        Chart.defaults.borderColor = isDarkMode ? '#333333' : '#ddd';
        
        // Update all existing charts
        Chart.instances.forEach(chart => {
            // Update grid lines
            if (chart.config.options.scales && chart.config.options.scales.x) {
                chart.config.options.scales.x.grid.color = isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
            }
            if (chart.config.options.scales && chart.config.options.scales.y) {
                chart.config.options.scales.y.grid.color = isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
            }
            
            // Update text colors
            chart.config.options.plugins.legend.labels.color = isDarkMode ? '#e0e0e0' : '#666';
            chart.config.options.plugins.title.color = isDarkMode ? '#e0e0e0' : '#666';
            
            // Update the chart
            chart.update();
        });
    }
}