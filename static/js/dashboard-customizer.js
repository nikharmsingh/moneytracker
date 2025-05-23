// Dashboard Customizer for Money Tracker
document.addEventListener('DOMContentLoaded', function() {
    initDashboardCustomizer();
});

function initDashboardCustomizer() {
    // Check if we're on the dashboard page
    if (!document.querySelector('.dashboard-container')) return;
    
    // Add customization button to the page
    addCustomizationButton();
    
    // Load user's saved layout if available
    loadUserLayout();
    
    // Initialize drag and drop functionality
    initDragAndDrop();
}

function addCustomizationButton() {
    const dashboardHeader = document.querySelector('.card-header h3');
    if (!dashboardHeader) return;
    
    const customizeBtn = document.createElement('button');
    customizeBtn.className = 'btn btn-sm btn-outline-primary ms-2';
    customizeBtn.innerHTML = '<i class="bi bi-grid me-1"></i>Customize';
    customizeBtn.id = 'customize-dashboard-btn';
    customizeBtn.setAttribute('data-bs-toggle', 'modal');
    customizeBtn.setAttribute('data-bs-target', '#dashboardCustomizeModal');
    
    dashboardHeader.appendChild(customizeBtn);
    
    // Create the customization modal
    createCustomizationModal();
}

function createCustomizationModal() {
    // Create modal HTML
    const modalHTML = `
    <div class="modal fade" id="dashboardCustomizeModal" tabindex="-1" aria-labelledby="dashboardCustomizeModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="dashboardCustomizeModalLabel">Customize Your Dashboard</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <div class="row mb-3">
                        <div class="col-12">
                            <div class="form-check form-switch">
                                <input class="form-check-input" type="checkbox" id="showFinancialSummary" checked>
                                <label class="form-check-label" for="showFinancialSummary">Financial Summary</label>
                            </div>
                            <div class="form-check form-switch">
                                <input class="form-check-input" type="checkbox" id="showBudgetOverview" checked>
                                <label class="form-check-label" for="showBudgetOverview">Budget Overview</label>
                            </div>
                            <div class="form-check form-switch">
                                <input class="form-check-input" type="checkbox" id="showSpendingByCategory" checked>
                                <label class="form-check-label" for="showSpendingByCategory">Spending by Category</label>
                            </div>
                            <div class="form-check form-switch">
                                <input class="form-check-input" type="checkbox" id="showRecentTransactions" checked>
                                <label class="form-check-label" for="showRecentTransactions">Recent Transactions</label>
                            </div>
                        </div>
                    </div>
                    
                    <h6 class="mb-3">Widget Order (Drag to reorder)</h6>
                    <div class="list-group" id="widgetOrderList">
                        <div class="list-group-item d-flex justify-content-between align-items-center" data-widget="financial-summary">
                            <div>
                                <i class="bi bi-grip-vertical me-2"></i>
                                Financial Summary
                            </div>
                            <span class="badge bg-primary">1</span>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center" data-widget="budget-overview">
                            <div>
                                <i class="bi bi-grip-vertical me-2"></i>
                                Budget Overview
                            </div>
                            <span class="badge bg-primary">2</span>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center" data-widget="spending-category">
                            <div>
                                <i class="bi bi-grip-vertical me-2"></i>
                                Spending by Category
                            </div>
                            <span class="badge bg-primary">3</span>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center" data-widget="recent-transactions">
                            <div>
                                <i class="bi bi-grip-vertical me-2"></i>
                                Recent Transactions
                            </div>
                            <span class="badge bg-primary">4</span>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" id="saveDashboardSettings">Save Changes</button>
                </div>
            </div>
        </div>
    </div>
    `;
    
    // Append modal to body
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Add event listener for save button
    document.getElementById('saveDashboardSettings').addEventListener('click', saveUserLayout);
}

function initDragAndDrop() {
    // Initialize Sortable.js on the widget order list
    if (typeof Sortable !== 'undefined') {
        const widgetOrderList = document.getElementById('widgetOrderList');
        if (widgetOrderList) {
            new Sortable(widgetOrderList, {
                animation: 150,
                ghostClass: 'sortable-ghost',
                onEnd: function() {
                    // Update the order numbers
                    updateOrderNumbers();
                }
            });
        }
        
        // Also make the dashboard widgets themselves draggable
        const dashboardContainer = document.querySelector('.dashboard-container');
        if (dashboardContainer) {
            new Sortable(dashboardContainer, {
                animation: 150,
                handle: '.widget-drag-handle',
                ghostClass: 'sortable-ghost',
                onEnd: function() {
                    // Save the new order automatically
                    const newOrder = [];
                    dashboardContainer.querySelectorAll('.dashboard-widget').forEach(widget => {
                        newOrder.push(widget.dataset.widget);
                    });
                    localStorage.setItem('dashboardWidgetOrder', JSON.stringify(newOrder));
                }
            });
        }
    }
}

function updateOrderNumbers() {
    const items = document.querySelectorAll('#widgetOrderList .list-group-item');
    items.forEach((item, index) => {
        const badge = item.querySelector('.badge');
        if (badge) {
            badge.textContent = index + 1;
        }
    });
}

function saveUserLayout() {
    // Get visibility settings
    const settings = {
        showFinancialSummary: document.getElementById('showFinancialSummary').checked,
        showBudgetOverview: document.getElementById('showBudgetOverview').checked,
        showSpendingByCategory: document.getElementById('showSpendingByCategory').checked,
        showRecentTransactions: document.getElementById('showRecentTransactions').checked
    };
    
    // Get widget order
    const widgetOrder = [];
    document.querySelectorAll('#widgetOrderList .list-group-item').forEach(item => {
        widgetOrder.push(item.dataset.widget);
    });
    
    // Save settings to localStorage
    localStorage.setItem('dashboardSettings', JSON.stringify(settings));
    localStorage.setItem('dashboardWidgetOrder', JSON.stringify(widgetOrder));
    
    // Apply settings immediately
    applyDashboardSettings(settings, widgetOrder);
    
    // Close the modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('dashboardCustomizeModal'));
    modal.hide();
    
    // Show success notification
    showNotification('Dashboard layout saved successfully!', 'success');
}

function loadUserLayout() {
    // Load settings from localStorage
    const settings = JSON.parse(localStorage.getItem('dashboardSettings') || '{}');
    const widgetOrder = JSON.parse(localStorage.getItem('dashboardWidgetOrder') || '[]');
    
    // Apply settings to checkboxes in modal
    if (settings.showFinancialSummary !== undefined) {
        document.getElementById('showFinancialSummary').checked = settings.showFinancialSummary;
    }
    if (settings.showBudgetOverview !== undefined) {
        document.getElementById('showBudgetOverview').checked = settings.showBudgetOverview;
    }
    if (settings.showSpendingByCategory !== undefined) {
        document.getElementById('showSpendingByCategory').checked = settings.showSpendingByCategory;
    }
    if (settings.showRecentTransactions !== undefined) {
        document.getElementById('showRecentTransactions').checked = settings.showRecentTransactions;
    }
    
    // Apply settings to the dashboard
    applyDashboardSettings(settings, widgetOrder);
}

function applyDashboardSettings(settings, widgetOrder) {
    // Apply visibility settings
    toggleWidgetVisibility('financial-summary', settings.showFinancialSummary);
    toggleWidgetVisibility('budget-overview', settings.showBudgetOverview);
    toggleWidgetVisibility('spending-category', settings.showSpendingByCategory);
    toggleWidgetVisibility('recent-transactions', settings.showRecentTransactions);
    
    // Apply widget order if we have a valid order
    if (widgetOrder && widgetOrder.length === 4) {
        reorderWidgets(widgetOrder);
    }
}

function toggleWidgetVisibility(widgetId, isVisible) {
    const widget = document.querySelector(`.dashboard-widget[data-widget="${widgetId}"]`);
    if (widget) {
        widget.style.display = isVisible ? 'block' : 'none';
    }
}

function reorderWidgets(widgetOrder) {
    const dashboardContainer = document.querySelector('.dashboard-container');
    if (!dashboardContainer) return;
    
    // Reorder widgets based on the saved order
    widgetOrder.forEach(widgetId => {
        const widget = document.querySelector(`.dashboard-widget[data-widget="${widgetId}"]`);
        if (widget) {
            dashboardContainer.appendChild(widget);
        }
    });
}