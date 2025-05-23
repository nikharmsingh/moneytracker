// Guided Tour for Money Tracker
document.addEventListener('DOMContentLoaded', function() {
    // Check if this is the user's first visit
    const hasSeenTour = localStorage.getItem('hasSeenTour');
    
    // If it's a first-time user and they're on the dashboard, offer the tour
    if (!hasSeenTour && document.querySelector('.dashboard-container')) {
        setTimeout(() => {
            showTourPrompt();
        }, 1000);
    }
    
    // Add event listener for manual tour start
    const startTourBtn = document.getElementById('start-tour-btn');
    if (startTourBtn) {
        startTourBtn.addEventListener('click', startGuidedTour);
    }
});

function showTourPrompt() {
    // Create a modal to ask if the user wants a tour
    const modalHTML = `
    <div class="modal fade" id="tourPromptModal" tabindex="-1" aria-labelledby="tourPromptModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="tourPromptModalLabel">Welcome to Money Tracker!</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <p>Would you like a quick tour to learn how to use the app?</p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal" id="skip-tour-btn">Skip Tour</button>
                    <button type="button" class="btn btn-primary" id="take-tour-btn">Take the Tour</button>
                </div>
            </div>
        </div>
    </div>
    `;
    
    // Append modal to body
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Show the modal
    const tourPromptModal = new bootstrap.Modal(document.getElementById('tourPromptModal'));
    tourPromptModal.show();
    
    // Add event listeners for buttons
    document.getElementById('skip-tour-btn').addEventListener('click', () => {
        localStorage.setItem('hasSeenTour', 'true');
    });
    
    document.getElementById('take-tour-btn').addEventListener('click', () => {
        tourPromptModal.hide();
        startGuidedTour();
        localStorage.setItem('hasSeenTour', 'true');
    });
}

function startGuidedTour() {
    // Define tour steps based on the current page
    let steps = [];
    
    // Check which page we're on and load appropriate tour steps
    if (document.querySelector('.dashboard-container')) {
        steps = getDashboardTourSteps();
    } else if (window.location.pathname.includes('/add_expense')) {
        steps = getAddExpenseTourSteps();
    } else if (window.location.pathname.includes('/reports_dashboard')) {
        steps = getReportsTourSteps();
    } else if (window.location.pathname.includes('/budget_overview')) {
        steps = getBudgetTourSteps();
    }
    
    // If no steps are defined for this page, show a message
    if (steps.length === 0) {
        showNotification('Tour is not available for this page.', 'info');
        return;
    }
    
    // Initialize the tour
    initTour(steps);
}

function initTour(steps) {
    // Create tour container if it doesn't exist
    if (!document.getElementById('guided-tour-container')) {
        const tourContainer = document.createElement('div');
        tourContainer.id = 'guided-tour-container';
        document.body.appendChild(tourContainer);
    }
    
    // Start with the first step
    showTourStep(steps, 0);
}

function showTourStep(steps, currentIndex) {
    const step = steps[currentIndex];
    const targetElement = document.querySelector(step.element);
    
    // If target element doesn't exist, skip to next step
    if (!targetElement && currentIndex < steps.length - 1) {
        showTourStep(steps, currentIndex + 1);
        return;
    } else if (!targetElement) {
        endTour();
        return;
    }
    
    // Position the tooltip relative to the target element
    positionTooltip(targetElement, step.position, step.title, step.content, () => {
        // Next button handler
        if (currentIndex < steps.length - 1) {
            showTourStep(steps, currentIndex + 1);
        } else {
            endTour();
            showNotification('Tour completed! You can restart it anytime from the help menu.', 'success');
        }
    });
    
    // Highlight the target element
    highlightElement(targetElement);
}

function positionTooltip(targetElement, position, title, content, onNextClick) {
    // Get element position
    const rect = targetElement.getBoundingClientRect();
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;
    
    // Create tooltip element
    const tooltip = document.createElement('div');
    tooltip.className = 'tour-tooltip';
    tooltip.innerHTML = `
        <div class="tour-tooltip-arrow"></div>
        <div class="tour-tooltip-header">
            <h5>${title}</h5>
        </div>
        <div class="tour-tooltip-body">
            <p>${content}</p>
        </div>
        <div class="tour-tooltip-footer">
            <button class="btn btn-sm btn-primary tour-next-btn">Next</button>
            <button class="btn btn-sm btn-outline-secondary tour-skip-btn">Skip Tour</button>
        </div>
    `;
    
    // Add tooltip to container
    const container = document.getElementById('guided-tour-container');
    container.innerHTML = '';
    container.appendChild(tooltip);
    
    // Position tooltip based on specified position
    let top, left;
    switch (position) {
        case 'top':
            top = rect.top + scrollTop - tooltip.offsetHeight - 10;
            left = rect.left + scrollLeft + (rect.width / 2) - (tooltip.offsetWidth / 2);
            tooltip.classList.add('position-top');
            break;
        case 'bottom':
            top = rect.bottom + scrollTop + 10;
            left = rect.left + scrollLeft + (rect.width / 2) - (tooltip.offsetWidth / 2);
            tooltip.classList.add('position-bottom');
            break;
        case 'left':
            top = rect.top + scrollTop + (rect.height / 2) - (tooltip.offsetHeight / 2);
            left = rect.left + scrollLeft - tooltip.offsetWidth - 10;
            tooltip.classList.add('position-left');
            break;
        case 'right':
            top = rect.top + scrollTop + (rect.height / 2) - (tooltip.offsetHeight / 2);
            left = rect.right + scrollLeft + 10;
            tooltip.classList.add('position-right');
            break;
        default:
            top = rect.bottom + scrollTop + 10;
            left = rect.left + scrollLeft;
            tooltip.classList.add('position-bottom');
    }
    
    // Apply position
    tooltip.style.top = `${top}px`;
    tooltip.style.left = `${left}px`;
    
    // Ensure the tooltip is visible in the viewport
    ensureInViewport(tooltip);
    
    // Add event listeners
    tooltip.querySelector('.tour-next-btn').addEventListener('click', onNextClick);
    tooltip.querySelector('.tour-skip-btn').addEventListener('click', endTour);
    
    // Scroll element into view if needed
    if (rect.top < 0 || rect.bottom > window.innerHeight) {
        targetElement.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
        });
    }
}

function ensureInViewport(tooltip) {
    const rect = tooltip.getBoundingClientRect();
    
    // Check if tooltip is outside viewport
    if (rect.left < 0) {
        tooltip.style.left = '10px';
    } else if (rect.right > window.innerWidth) {
        tooltip.style.left = `${window.innerWidth - rect.width - 10}px`;
    }
    
    if (rect.top < 0) {
        tooltip.style.top = '10px';
    } else if (rect.bottom > window.innerHeight) {
        tooltip.style.top = `${window.innerHeight - rect.height - 10}px`;
    }
}

function highlightElement(element) {
    // Remove any existing highlights
    const existingOverlay = document.querySelector('.tour-highlight-overlay');
    if (existingOverlay) {
        existingOverlay.remove();
    }
    
    // Create overlay
    const overlay = document.createElement('div');
    overlay.className = 'tour-highlight-overlay';
    document.body.appendChild(overlay);
    
    // Create highlight
    const rect = element.getBoundingClientRect();
    const highlight = document.createElement('div');
    highlight.className = 'tour-highlight';
    highlight.style.top = `${rect.top + window.pageYOffset}px`;
    highlight.style.left = `${rect.left + window.pageXOffset}px`;
    highlight.style.width = `${rect.width}px`;
    highlight.style.height = `${rect.height}px`;
    document.body.appendChild(highlight);
}

function endTour() {
    // Remove all tour elements
    const container = document.getElementById('guided-tour-container');
    if (container) {
        container.innerHTML = '';
    }
    
    // Remove highlight overlay
    const overlay = document.querySelector('.tour-highlight-overlay');
    if (overlay) {
        overlay.remove();
    }
    
    // Remove highlight
    const highlight = document.querySelector('.tour-highlight');
    if (highlight) {
        highlight.remove();
    }
}

// Define tour steps for different pages
function getDashboardTourSteps() {
    return [
        {
            element: '.navbar-brand',
            position: 'bottom',
            title: 'Welcome to Money Tracker',
            content: 'This is your personal finance management app. Let\'s explore the main features!'
        },
        {
            element: '.card:contains("Financial Summary")',
            position: 'bottom',
            title: 'Financial Summary',
            content: 'Here you can see your overall financial status, including total income and expenses.'
        },
        {
            element: '.card:contains("Budget Overview")',
            position: 'top',
            title: 'Budget Overview',
            content: 'Track your budget progress here. Green means you\'re on track, yellow is a warning, and red means you\'ve exceeded your budget.'
        },
        {
            element: '.card:contains("Spending by Category")',
            position: 'right',
            title: 'Spending Analysis',
            content: 'This chart shows your spending breakdown by category, helping you identify where your money goes.'
        },
        {
            element: '.card:contains("Recent Transactions")',
            position: 'left',
            title: 'Recent Transactions',
            content: 'View your most recent transactions here. You can quickly edit or delete them if needed.'
        },
        {
            element: '.navbar-toggler',
            position: 'bottom',
            title: 'Navigation Menu',
            content: 'Click here to access all features including adding transactions, viewing reports, and managing your account.'
        },
        {
            element: '#darkModeToggle',
            position: 'bottom',
            title: 'Dark Mode',
            content: 'Toggle between light and dark mode based on your preference.'
        }
    ];
}

function getAddExpenseTourSteps() {
    return [
        {
            element: 'form',
            position: 'top',
            title: 'Add Transaction',
            content: 'Use this form to add your expenses or income.'
        },
        {
            element: '#amount',
            position: 'right',
            title: 'Transaction Amount',
            content: 'Enter the amount of your transaction here.'
        },
        {
            element: '#category',
            position: 'right',
            title: 'Transaction Category',
            content: 'Select a category to organize your transactions. This helps with budget tracking and reports.'
        },
        {
            element: '#date',
            position: 'right',
            title: 'Transaction Date',
            content: 'Select the date when the transaction occurred.'
        },
        {
            element: '#is_recurring',
            position: 'right',
            title: 'Recurring Transactions',
            content: 'Enable this for regular expenses like rent or subscriptions that happen on a schedule.'
        }
    ];
}

function getReportsTourSteps() {
    return [
        {
            element: '.nav-tabs',
            position: 'bottom',
            title: 'Reports & Analytics',
            content: 'Switch between different reports to analyze your finances from various angles.'
        },
        {
            element: '.chart-container:first-child',
            position: 'right',
            title: 'Visual Analytics',
            content: 'These charts help you visualize your financial data for better understanding.'
        },
        {
            element: '.date-range-picker',
            position: 'bottom',
            title: 'Date Range Selection',
            content: 'Adjust the time period to analyze specific timeframes.'
        }
    ];
}

function getBudgetTourSteps() {
    return [
        {
            element: '.budget-card:first-child',
            position: 'right',
            title: 'Budget Cards',
            content: 'Each card represents a budget you\'ve set. The progress bar shows how much of your budget you\'ve used.'
        },
        {
            element: '.btn-primary:contains("Add Budget")',
            position: 'left',
            title: 'Create New Budgets',
            content: 'Click here to create a new budget for any category or time period.'
        }
    ];
}