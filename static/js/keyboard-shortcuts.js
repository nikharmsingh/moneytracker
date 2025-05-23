// Keyboard Shortcuts for Money Tracker
document.addEventListener('DOMContentLoaded', function() {
    initKeyboardShortcuts();
    createKeyboardShortcutsModal();
});

function initKeyboardShortcuts() {
    // Global keyboard event listener
    document.addEventListener('keydown', function(event) {
        // Don't trigger shortcuts when typing in input fields
        if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA' || event.target.isContentEditable) {
            return;
        }
        
        // Shift + ? to show keyboard shortcuts help
        if (event.shiftKey && event.key === '?') {
            event.preventDefault();
            showKeyboardShortcutsModal();
            return;
        }
        
        // Navigation shortcuts
        if (event.altKey) {
            switch (event.key) {
                case 'd': // Dashboard
                    event.preventDefault();
                    navigateTo('/');
                    break;
                case 'e': // Add Expense
                    event.preventDefault();
                    navigateTo('/add_expense');
                    break;
                case 'i': // Add Income
                    event.preventDefault();
                    navigateTo('/add_salary');
                    break;
                case 'b': // Budgets
                    event.preventDefault();
                    navigateTo('/manage_budgets');
                    break;
                case 'r': // Reports
                    event.preventDefault();
                    navigateTo('/reports_dashboard');
                    break;
                case 't': // Transactions
                    event.preventDefault();
                    navigateTo('/view_transactions');
                    break;
                case 'c': // Categories
                    event.preventDefault();
                    navigateTo('/manage_categories');
                    break;
                case 'p': // Profile
                    event.preventDefault();
                    navigateTo('/profile');
                    break;
                case 's': // Security Settings
                    event.preventDefault();
                    navigateTo('/security_settings');
                    break;
            }
        }
        
        // Function shortcuts (without modifiers)
        switch (event.key) {
            case 'n': // New transaction
                if (!event.ctrlKey && !event.metaKey && !event.altKey) {
                    event.preventDefault();
                    navigateTo('/add_expense');
                }
                break;
            case 'f': // Search/Filter
                if (!event.ctrlKey && !event.metaKey && !event.altKey) {
                    event.preventDefault();
                    focusSearchField();
                }
                break;
            case 'Escape': // Close modals
                closeActiveModal();
                break;
        }
        
        // Dark mode toggle with Shift+D
        if (event.shiftKey && event.key === 'D') {
            event.preventDefault();
            toggleDarkMode();
        }
    });
}

function navigateTo(path) {
    window.location.href = path;
}

function focusSearchField() {
    // Find the first search input on the page
    const searchInput = document.querySelector('input[type="search"], input[placeholder*="search"], input[placeholder*="Search"]');
    if (searchInput) {
        searchInput.focus();
    }
}

function closeActiveModal() {
    // Find any open Bootstrap modal and close it
    const openModal = document.querySelector('.modal.show');
    if (openModal) {
        const modalInstance = bootstrap.Modal.getInstance(openModal);
        if (modalInstance) {
            modalInstance.hide();
        }
    }
}

function toggleDarkMode() {
    // Find the dark mode toggle and click it
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (darkModeToggle) {
        darkModeToggle.checked = !darkModeToggle.checked;
        // Trigger the change event to apply the dark mode
        darkModeToggle.dispatchEvent(new Event('change'));
    }
}

function createKeyboardShortcutsModal() {
    // Detect if user is on Mac
    const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
    
    // Create the modal HTML
    const modalHTML = `
    <div class="modal fade keyboard-shortcuts-modal" id="keyboardShortcutsModal" tabindex="-1" aria-labelledby="keyboardShortcutsModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="keyboardShortcutsModalLabel">
                        <i class="bi bi-keyboard me-2"></i>Keyboard Shortcuts
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <div class="platform-toggle mb-3">
                        <div class="btn-group" role="group" aria-label="Platform toggle">
                            <button type="button" class="btn btn-sm btn-outline-primary platform-btn active" data-platform="windows">Windows/Linux</button>
                            <button type="button" class="btn btn-sm btn-outline-primary platform-btn" data-platform="mac">macOS</button>
                        </div>
                    </div>
                    
                    <h6 class="mb-3">Navigation</h6>
                    <div class="shortcut-row">
                        <div class="shortcut-description">Go to Dashboard</div>
                        <div class="shortcut-keys windows-shortcut">
                            <span class="shortcut-key">Alt</span> + <span class="shortcut-key">D</span>
                        </div>
                        <div class="shortcut-keys mac-shortcut" style="display: none;">
                            <span class="shortcut-key">Option</span> + <span class="shortcut-key">D</span>
                        </div>
                    </div>
                    <div class="shortcut-row">
                        <div class="shortcut-description">Add Expense</div>
                        <div class="shortcut-keys windows-shortcut">
                            <span class="shortcut-key">Alt</span> + <span class="shortcut-key">E</span>
                        </div>
                        <div class="shortcut-keys mac-shortcut" style="display: none;">
                            <span class="shortcut-key">Option</span> + <span class="shortcut-key">E</span>
                        </div>
                    </div>
                    <div class="shortcut-row">
                        <div class="shortcut-description">Add Income</div>
                        <div class="shortcut-keys windows-shortcut">
                            <span class="shortcut-key">Alt</span> + <span class="shortcut-key">I</span>
                        </div>
                        <div class="shortcut-keys mac-shortcut" style="display: none;">
                            <span class="shortcut-key">Option</span> + <span class="shortcut-key">I</span>
                        </div>
                    </div>
                    <div class="shortcut-row">
                        <div class="shortcut-description">Manage Budgets</div>
                        <div class="shortcut-keys windows-shortcut">
                            <span class="shortcut-key">Alt</span> + <span class="shortcut-key">B</span>
                        </div>
                        <div class="shortcut-keys mac-shortcut" style="display: none;">
                            <span class="shortcut-key">Option</span> + <span class="shortcut-key">B</span>
                        </div>
                    </div>
                    <div class="shortcut-row">
                        <div class="shortcut-description">Reports Dashboard</div>
                        <div class="shortcut-keys windows-shortcut">
                            <span class="shortcut-key">Alt</span> + <span class="shortcut-key">R</span>
                        </div>
                        <div class="shortcut-keys mac-shortcut" style="display: none;">
                            <span class="shortcut-key">Option</span> + <span class="shortcut-key">R</span>
                        </div>
                    </div>
                    <div class="shortcut-row">
                        <div class="shortcut-description">View Transactions</div>
                        <div class="shortcut-keys windows-shortcut">
                            <span class="shortcut-key">Alt</span> + <span class="shortcut-key">T</span>
                        </div>
                        <div class="shortcut-keys mac-shortcut" style="display: none;">
                            <span class="shortcut-key">Option</span> + <span class="shortcut-key">T</span>
                        </div>
                    </div>
                    <div class="shortcut-row">
                        <div class="shortcut-description">Manage Categories</div>
                        <div class="shortcut-keys windows-shortcut">
                            <span class="shortcut-key">Alt</span> + <span class="shortcut-key">C</span>
                        </div>
                        <div class="shortcut-keys mac-shortcut" style="display: none;">
                            <span class="shortcut-key">Option</span> + <span class="shortcut-key">C</span>
                        </div>
                    </div>
                    <div class="shortcut-row">
                        <div class="shortcut-description">Profile Settings</div>
                        <div class="shortcut-keys windows-shortcut">
                            <span class="shortcut-key">Alt</span> + <span class="shortcut-key">P</span>
                        </div>
                        <div class="shortcut-keys mac-shortcut" style="display: none;">
                            <span class="shortcut-key">Option</span> + <span class="shortcut-key">P</span>
                        </div>
                    </div>
                    <div class="shortcut-row">
                        <div class="shortcut-description">Security Settings</div>
                        <div class="shortcut-keys windows-shortcut">
                            <span class="shortcut-key">Alt</span> + <span class="shortcut-key">S</span>
                        </div>
                        <div class="shortcut-keys mac-shortcut" style="display: none;">
                            <span class="shortcut-key">Option</span> + <span class="shortcut-key">S</span>
                        </div>
                    </div>
                    
                    <h6 class="mb-3 mt-4">Actions</h6>
                    <div class="shortcut-row">
                        <div class="shortcut-description">New Transaction</div>
                        <div class="shortcut-keys">
                            <span class="shortcut-key">N</span>
                        </div>
                    </div>
                    <div class="shortcut-row">
                        <div class="shortcut-description">Search/Filter</div>
                        <div class="shortcut-keys">
                            <span class="shortcut-key">F</span>
                        </div>
                    </div>
                    <div class="shortcut-row">
                        <div class="shortcut-description">Close Modal</div>
                        <div class="shortcut-keys">
                            <span class="shortcut-key">Esc</span>
                        </div>
                    </div>
                    <div class="shortcut-row">
                        <div class="shortcut-description">Toggle Dark Mode</div>
                        <div class="shortcut-keys windows-shortcut">
                            <span class="shortcut-key">Shift</span> + <span class="shortcut-key">D</span>
                        </div>
                        <div class="shortcut-keys mac-shortcut" style="display: none;">
                            <span class="shortcut-key">Shift</span> + <span class="shortcut-key">D</span>
                        </div>
                    </div>
                    <div class="shortcut-row">
                        <div class="shortcut-description">Show Keyboard Shortcuts</div>
                        <div class="shortcut-keys windows-shortcut">
                            <span class="shortcut-key">Shift</span> + <span class="shortcut-key">?</span>
                        </div>
                        <div class="shortcut-keys mac-shortcut" style="display: none;">
                            <span class="shortcut-key">Shift</span> + <span class="shortcut-key">?</span>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                </div>
            </div>
        </div>
    </div>
    `;
    
    // Append modal to body
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

function showKeyboardShortcutsModal() {
    const modal = new bootstrap.Modal(document.getElementById('keyboardShortcutsModal'));
    modal.show();
    
    // Set up platform toggle buttons
    const platformButtons = document.querySelectorAll('.platform-btn');
    platformButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from all buttons
            platformButtons.forEach(btn => btn.classList.remove('active'));
            
            // Add active class to clicked button
            this.classList.add('active');
            
            // Get the platform from the button's data attribute
            const platform = this.getAttribute('data-platform');
            
            // Show/hide the appropriate shortcut keys
            if (platform === 'mac') {
                document.querySelectorAll('.windows-shortcut').forEach(el => el.style.display = 'none');
                document.querySelectorAll('.mac-shortcut').forEach(el => el.style.display = 'block');
            } else {
                document.querySelectorAll('.mac-shortcut').forEach(el => el.style.display = 'none');
                document.querySelectorAll('.windows-shortcut').forEach(el => el.style.display = 'block');
            }
        });
    });
    
    // Auto-select Mac platform if user is on Mac
    if (navigator.platform.toUpperCase().indexOf('MAC') >= 0) {
        const macButton = document.querySelector('.platform-btn[data-platform="mac"]');
        if (macButton) {
            macButton.click();
        }
    }
}