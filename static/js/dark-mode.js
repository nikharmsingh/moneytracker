// Enhanced Dark Mode Functionality with Animations
document.addEventListener('DOMContentLoaded', function() {
    // Check for saved dark mode preference
    const darkModeEnabled = localStorage.getItem('darkModeEnabled') === 'true';
    const darkModeToggle = document.getElementById('darkModeToggle');
    const toggleLabel = document.querySelector('.checkbox-label');
    
    // Apply dark mode if enabled
    if (darkModeEnabled) {
        document.body.classList.add('dark-mode');
        darkModeToggle.checked = true;
        
        // Add a small delay to ensure the animation doesn't play on page load
        setTimeout(() => {
            document.documentElement.style.setProperty('--theme-transition', 'background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease');
        }, 300);
    }
    
    // Add hover effect for the toggle
    if (toggleLabel) {
        toggleLabel.addEventListener('mouseenter', function() {
            this.classList.add('toggle-hover');
        });
        
        toggleLabel.addEventListener('mouseleave', function() {
            this.classList.remove('toggle-hover');
        });
    }
    
    // Toggle dark mode when switch is clicked with enhanced animation
    darkModeToggle.addEventListener('change', function() {
        // Enable transitions for smooth animation
        document.documentElement.style.setProperty('--theme-transition', 'background-color 0.6s cubic-bezier(0.68, -0.55, 0.27, 1.55), color 0.6s ease, border-color 0.6s ease, box-shadow 0.6s ease');
        
        if (this.checked) {
            // Add animation class before adding dark-mode
            document.body.classList.add('theme-transition');
            
            // Slight delay for smoother transition
            setTimeout(() => {
                document.body.classList.add('dark-mode');
                localStorage.setItem('darkModeEnabled', 'true');
                
                // Update chart colors if charts exist
                updateChartsForDarkMode(true);
                
                // Add stars animation to background
                addStarsAnimation();
            }, 50);
        } else {
            // Add animation class before removing dark-mode
            document.body.classList.add('theme-transition');
            
            // Slight delay for smoother transition
            setTimeout(() => {
                document.body.classList.remove('dark-mode');
                localStorage.setItem('darkModeEnabled', 'false');
                
                // Update chart colors if charts exist
                updateChartsForDarkMode(false);
                
                // Remove stars animation
                removeStarsAnimation();
            }, 50);
        }
        
        // Remove the transition class after animation completes
        setTimeout(() => {
            document.body.classList.remove('theme-transition');
        }, 700);
    });
    
    // Initialize charts with appropriate colors based on current mode
    if (darkModeEnabled) {
        updateChartsForDarkMode(true);
        
        // Add stars animation if dark mode is enabled on load
        setTimeout(() => {
            addStarsAnimation();
        }, 500);
    }
    
    // Add hover effect to toggle
    const darkModeToggleLabel = document.querySelector('.dark-mode-toggle');
    darkModeToggleLabel.addEventListener('mouseenter', function() {
        this.classList.add('toggle-hover');
    });
    
    darkModeToggleLabel.addEventListener('mouseleave', function() {
        this.classList.remove('toggle-hover');
    });
});

// Function to add stars animation to background in dark mode
function addStarsAnimation() {
    // Only add stars if they don't already exist
    if (!document.querySelector('.stars-container')) {
        const starsContainer = document.createElement('div');
        starsContainer.className = 'stars-container';
        
        // Create stars with different sizes and animations
        for (let i = 0; i < 50; i++) {
            const star = document.createElement('div');
            star.className = 'star';
            
            // Random position
            star.style.top = `${Math.random() * 100}%`;
            star.style.left = `${Math.random() * 100}%`;
            
            // Random size
            const size = 0.5 + Math.random() * 2;
            star.style.width = `${size}px`;
            star.style.height = `${size}px`;
            
            // Random animation delay
            star.style.animationDelay = `${Math.random() * 5}s`;
            
            starsContainer.appendChild(star);
        }
        
        document.body.appendChild(starsContainer);
        
        // Add CSS for stars animation if it doesn't exist
        if (!document.getElementById('stars-style')) {
            const style = document.createElement('style');
            style.id = 'stars-style';
            style.textContent = `
                .stars-container {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    pointer-events: none;
                    z-index: -1;
                    opacity: 0;
                    transition: opacity 1s ease;
                }
                
                body.dark-mode .stars-container {
                    opacity: 1;
                }
                
                .star {
                    position: absolute;
                    background-color: white;
                    border-radius: 50%;
                    animation: twinkle 5s infinite ease-in-out;
                }
                
                @keyframes twinkle {
                    0%, 100% { opacity: 0.2; }
                    50% { opacity: 1; }
                }
            `;
            document.head.appendChild(style);
        }
    }
}

// Function to remove stars animation
function removeStarsAnimation() {
    const starsContainer = document.querySelector('.stars-container');
    if (starsContainer) {
        starsContainer.style.opacity = '0';
        setTimeout(() => {
            if (starsContainer.parentNode) {
                starsContainer.parentNode.removeChild(starsContainer);
            }
        }, 1000);
    }
}

// Function to update chart colors for dark mode
function updateChartsForDarkMode(isDarkMode) {
    // Check if Chart is defined (charts.js is loaded)
    if (typeof Chart !== 'undefined') {
        // Define color palettes for light and dark modes
        const darkModeColors = [
            '#6a8fff', // blue
            '#4fc3f7', // light blue
            '#2ebd59', // green
            '#ffcc33', // yellow
            '#e05260', // red
            '#ba68c8', // purple
            '#f57c00', // orange
            '#26a69a'  // teal
        ];
        
        const lightModeColors = [
            '#4a6bff', // blue
            '#17a2b8', // light blue
            '#28a745', // green
            '#ffc107', // yellow
            '#dc3545', // red
            '#9c27b0', // purple
            '#fd7e14', // orange
            '#20c997'  // teal
        ];
        
        // Update default chart colors for current mode
        Chart.defaults.color = isDarkMode ? '#e0e0e0' : '#666';
        Chart.defaults.borderColor = isDarkMode ? '#333333' : '#ddd';
        
        // Update all existing charts
        Chart.instances.forEach(chart => {
            // Update grid lines
            if (chart.config.options.scales && chart.config.options.scales.x) {
                chart.config.options.scales.x.grid.color = isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
                chart.config.options.scales.x.ticks.color = isDarkMode ? '#e0e0e0' : '#666';
            }
            if (chart.config.options.scales && chart.config.options.scales.y) {
                chart.config.options.scales.y.grid.color = isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
                chart.config.options.scales.y.ticks.color = isDarkMode ? '#e0e0e0' : '#666';
            }
            
            // Update text colors
            if (chart.config.options.plugins && chart.config.options.plugins.legend) {
                // Ensure legend labels are visible
                chart.config.options.plugins.legend.labels.color = isDarkMode ? '#e0e0e0' : '#666';
                chart.config.options.plugins.legend.labels.font = {
                    weight: isDarkMode ? 'bold' : 'normal',
                    size: 12
                };
                // Make sure legend is visible
                chart.config.options.plugins.legend.display = true;
                // Improve legend contrast
                if (isDarkMode) {
                    chart.config.options.plugins.legend.labels.boxWidth = 15;
                    chart.config.options.plugins.legend.labels.padding = 15;
                    // Add a subtle text shadow for better readability
                    chart.config.options.plugins.legend.labels.textStrokeColor = 'rgba(0, 0, 0, 0.5)';
                    chart.config.options.plugins.legend.labels.textStrokeWidth = 1;
                }
            }
            
            if (chart.config.options.plugins && chart.config.options.plugins.title) {
                chart.config.options.plugins.title.color = isDarkMode ? '#e0e0e0' : '#666';
                chart.config.options.plugins.title.font = {
                    weight: isDarkMode ? 'bold' : 'normal',
                    size: 16
                };
            }
            
            // Update dataset colors if they exist
            if (chart.config.data && chart.config.data.datasets) {
                chart.config.data.datasets.forEach((dataset, index) => {
                    // For pie/doughnut charts with multiple colors
                    if (dataset.backgroundColor && Array.isArray(dataset.backgroundColor)) {
                        dataset.backgroundColor = isDarkMode ? darkModeColors : lightModeColors;
                    } 
                    // For bar/line charts with a single color
                    else if (dataset.backgroundColor) {
                        const colorIndex = index % darkModeColors.length;
                        dataset.backgroundColor = isDarkMode ? darkModeColors[colorIndex] : lightModeColors[colorIndex];
                        
                        // If it's a line chart, also update borderColor
                        if (dataset.borderColor) {
                            dataset.borderColor = isDarkMode ? darkModeColors[colorIndex] : lightModeColors[colorIndex];
                        }
                    }
                });
            }
            
            // Update the chart
            chart.update();
        });
    }
}