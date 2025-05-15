// Advanced Filtering and Search Capabilities
document.addEventListener('DOMContentLoaded', function() {
    // Initialize advanced filters
    initializeAdvancedFilters();
    
    // Initialize data tables if they exist
    initializeDataTables();
    
    // Initialize date range picker
    initializeDateRangePicker();
    
    // Initialize category filter
    initializeCategoryFilter();
    
    // Initialize amount range filter
    initializeAmountRangeFilter();
    
    // Initialize search functionality
    initializeSearch();
});

function initializeAdvancedFilters() {
    // Toggle advanced filters visibility
    const filterToggle = document.getElementById('toggleAdvancedFilters');
    if (filterToggle) {
        filterToggle.addEventListener('click', function() {
            const advancedFilters = document.getElementById('advancedFilters');
            if (advancedFilters) {
                advancedFilters.classList.toggle('show');
                
                // Update button text
                if (advancedFilters.classList.contains('show')) {
                    this.innerHTML = '<i class="bi bi-funnel-fill me-1"></i>Hide Advanced Filters';
                } else {
                    this.innerHTML = '<i class="bi bi-funnel me-1"></i>Show Advanced Filters';
                }
            }
        });
    }
    
    // Handle filter reset
    const resetFilters = document.getElementById('resetFilters');
    if (resetFilters) {
        resetFilters.addEventListener('click', function() {
            // Reset all filter inputs
            const filterForm = document.getElementById('filterForm');
            if (filterForm) {
                filterForm.reset();
                
                // Reset date range picker if it exists
                if (typeof $('#dateRange').data('daterangepicker') !== 'undefined') {
                    $('#dateRange').data('daterangepicker').setStartDate(moment().startOf('month'));
                    $('#dateRange').data('daterangepicker').setEndDate(moment().endOf('month'));
                }
                
                // Reset amount range slider if it exists
                if (typeof amountRangeSlider !== 'undefined') {
                    amountRangeSlider.noUiSlider.reset();
                }
                
                // Reset category multiselect if it exists
                if ($('.category-select').length) {
                    $('.category-select').val('default').trigger('change');
                }
                
                // Apply the reset filters
                applyFilters();
            }
        });
    }
    
    // Handle filter apply
    const applyFiltersBtn = document.getElementById('applyFilters');
    if (applyFiltersBtn) {
        applyFiltersBtn.addEventListener('click', function() {
            applyFilters();
        });
    }
}

function initializeDataTables() {
    // Check if DataTable is available
    if (typeof $.fn.DataTable !== 'undefined') {
        // Initialize expense table
        const expenseTable = $('#expenseTable');
        if (expenseTable.length) {
            expenseTable.DataTable({
                responsive: true,
                dom: 'Bfrtip',
                buttons: [
                    'copy', 'csv', 'excel', 'pdf', 'print'
                ],
                language: {
                    search: "_INPUT_",
                    searchPlaceholder: "Search expenses...",
                    lengthMenu: "Show _MENU_ entries",
                    info: "Showing _START_ to _END_ of _TOTAL_ entries",
                    infoEmpty: "Showing 0 to 0 of 0 entries",
                    infoFiltered: "(filtered from _MAX_ total entries)"
                },
                order: [[0, 'desc']], // Sort by date descending by default
                columnDefs: [
                    { 
                        targets: 'amount-column',
                        render: function(data, type, row) {
                            if (type === 'display' || type === 'filter') {
                                return new Intl.NumberFormat('en-US', { 
                                    style: 'currency', 
                                    currency: 'USD',
                                    minimumFractionDigits: 0,
                                    maximumFractionDigits: 0
                                }).format(data);
                            }
                            return data;
                        }
                    },
                    {
                        targets: 'date-column',
                        render: function(data, type, row) {
                            if (type === 'display' || type === 'filter') {
                                const date = new Date(data);
                                return date.toLocaleDateString('en-US', {
                                    year: 'numeric',
                                    month: 'short',
                                    day: 'numeric'
                                });
                            }
                            return data;
                        }
                    }
                ]
            });
        }
        
        // Initialize budget table
        const budgetTable = $('#budgetTable');
        if (budgetTable.length) {
            budgetTable.DataTable({
                responsive: true,
                language: {
                    search: "_INPUT_",
                    searchPlaceholder: "Search budgets...",
                },
                order: [[0, 'asc']], // Sort by category ascending by default
                columnDefs: [
                    { 
                        targets: 'amount-column',
                        render: function(data, type, row) {
                            if (type === 'display' || type === 'filter') {
                                return new Intl.NumberFormat('en-US', { 
                                    style: 'currency', 
                                    currency: 'USD',
                                    minimumFractionDigits: 0,
                                    maximumFractionDigits: 0
                                }).format(data);
                            }
                            return data;
                        }
                    }
                ]
            });
        }
    }
}

function initializeDateRangePicker() {
    // Check if daterangepicker is available
    if (typeof $.fn.daterangepicker !== 'undefined') {
        const dateRange = $('#dateRange');
        if (dateRange.length) {
            dateRange.daterangepicker({
                startDate: moment().startOf('month'),
                endDate: moment().endOf('month'),
                ranges: {
                   'Today': [moment(), moment()],
                   'Yesterday': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
                   'Last 7 Days': [moment().subtract(6, 'days'), moment()],
                   'Last 30 Days': [moment().subtract(29, 'days'), moment()],
                   'This Month': [moment().startOf('month'), moment().endOf('month')],
                   'Last Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')],
                   'This Year': [moment().startOf('year'), moment().endOf('year')],
                   'Last Year': [moment().subtract(1, 'year').startOf('year'), moment().subtract(1, 'year').endOf('year')]
                },
                locale: {
                    format: 'YYYY-MM-DD'
                }
            });
        }
    }
}

function initializeCategoryFilter() {
    // Check if select2 is available
    if (typeof $.fn.select2 !== 'undefined') {
        const categorySelect = $('.category-select');
        if (categorySelect.length) {
            categorySelect.select2({
                placeholder: "Select categories",
                allowClear: true,
                multiple: true,
                width: '100%'
            });
        }
    }
}

function initializeAmountRangeFilter() {
    // Check if noUiSlider is available
    if (typeof noUiSlider !== 'undefined') {
        const amountRange = document.getElementById('amountRange');
        if (amountRange) {
            // Get min and max values from data attributes
            const min = parseInt(amountRange.dataset.min || 0);
            const max = parseInt(amountRange.dataset.max || 10000);
            
            // Create the slider
            window.amountRangeSlider = noUiSlider.create(amountRange, {
                start: [min, max],
                connect: true,
                step: 100,
                range: {
                    'min': min,
                    'max': max
                },
                format: {
                    to: function(value) {
                        return Math.round(value);
                    },
                    from: function(value) {
                        return Number(value);
                    }
                }
            });
            
            // Update the display values
            const minAmount = document.getElementById('minAmount');
            const maxAmount = document.getElementById('maxAmount');
            
            amountRangeSlider.on('update', function(values, handle) {
                if (handle === 0) {
                    minAmount.value = values[0];
                } else {
                    maxAmount.value = values[1];
                }
            });
            
            // Update slider when input values change
            minAmount.addEventListener('change', function() {
                amountRangeSlider.noUiSlider.set([this.value, null]);
            });
            
            maxAmount.addEventListener('change', function() {
                amountRangeSlider.noUiSlider.set([null, this.value]);
            });
        }
    }
}

function initializeSearch() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            
            // If we're using DataTables, use its search functionality
            if (typeof $.fn.DataTable !== 'undefined') {
                const table = $('#expenseTable').DataTable();
                if (table) {
                    table.search(searchTerm).draw();
                    return;
                }
            }
            
            // Otherwise, implement custom search
            const rows = document.querySelectorAll('#expenseTable tbody tr');
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }
}

function applyFilters() {
    // If we're using DataTables, use its API for filtering
    if (typeof $.fn.DataTable !== 'undefined') {
        const table = $('#expenseTable').DataTable();
        if (table) {
            // Custom filtering function
            $.fn.dataTable.ext.search.push(
                function(settings, data, dataIndex) {
                    // Get filter values
                    const dateRange = $('#dateRange').val().split(' - ');
                    const startDate = dateRange[0] ? new Date(dateRange[0]) : null;
                    const endDate = dateRange[1] ? new Date(dateRange[1]) : null;
                    
                    const categories = $('.category-select').val();
                    
                    const minAmount = parseInt($('#minAmount').val());
                    const maxAmount = parseInt($('#maxAmount').val());
                    
                    const transactionType = $('input[name="transactionType"]:checked').val();
                    
                    // Get row data
                    const rowDate = new Date(data[0]); // Assuming date is in the first column
                    const rowCategory = data[2]; // Assuming category is in the third column
                    const rowAmount = parseFloat(data[3].replace(/[^0-9.-]+/g, '')); // Assuming amount is in the fourth column
                    const rowType = data[4]; // Assuming transaction type is in the fifth column
                    
                    // Apply date filter
                    if (startDate && endDate) {
                        if (rowDate < startDate || rowDate > endDate) {
                            return false;
                        }
                    }
                    
                    // Apply category filter
                    if (categories && categories.length > 0 && categories[0] !== 'default') {
                        if (!categories.includes(rowCategory)) {
                            return false;
                        }
                    }
                    
                    // Apply amount filter
                    if (!isNaN(minAmount) && !isNaN(maxAmount)) {
                        if (rowAmount < minAmount || rowAmount > maxAmount) {
                            return false;
                        }
                    }
                    
                    // Apply transaction type filter
                    if (transactionType && transactionType !== 'all') {
                        if (rowType !== transactionType) {
                            return false;
                        }
                    }
                    
                    return true;
                }
            );
            
            // Redraw the table with the filters applied
            table.draw();
            
            // Remove the custom filter function after drawing
            $.fn.dataTable.ext.search.pop();
        }
    } else {
        // Implement custom filtering for non-DataTable tables
        const rows = document.querySelectorAll('#expenseTable tbody tr');
        
        // Get filter values
        const dateRange = document.getElementById('dateRange').value.split(' - ');
        const startDate = dateRange[0] ? new Date(dateRange[0]) : null;
        const endDate = dateRange[1] ? new Date(dateRange[1]) : null;
        
        const categorySelect = document.querySelector('.category-select');
        const categories = categorySelect ? Array.from(categorySelect.selectedOptions).map(option => option.value) : [];
        
        const minAmount = parseInt(document.getElementById('minAmount').value);
        const maxAmount = parseInt(document.getElementById('maxAmount').value);
        
        const transactionTypeInputs = document.querySelectorAll('input[name="transactionType"]');
        let transactionType = 'all';
        transactionTypeInputs.forEach(input => {
            if (input.checked) {
                transactionType = input.value;
            }
        });
        
        rows.forEach(row => {
            const cells = row.querySelectorAll('td');
            
            // Get row data
            const rowDate = new Date(cells[0].textContent); // Assuming date is in the first column
            const rowCategory = cells[2].textContent; // Assuming category is in the third column
            const rowAmount = parseFloat(cells[3].textContent.replace(/[^0-9.-]+/g, '')); // Assuming amount is in the fourth column
            const rowType = cells[4].textContent; // Assuming transaction type is in the fifth column
            
            let showRow = true;
            
            // Apply date filter
            if (startDate && endDate) {
                if (rowDate < startDate || rowDate > endDate) {
                    showRow = false;
                }
            }
            
            // Apply category filter
            if (categories && categories.length > 0 && categories[0] !== 'default') {
                if (!categories.includes(rowCategory)) {
                    showRow = false;
                }
            }
            
            // Apply amount filter
            if (!isNaN(minAmount) && !isNaN(maxAmount)) {
                if (rowAmount < minAmount || rowAmount > maxAmount) {
                    showRow = false;
                }
            }
            
            // Apply transaction type filter
            if (transactionType && transactionType !== 'all') {
                if (rowType !== transactionType) {
                    showRow = false;
                }
            }
            
            row.style.display = showRow ? '' : 'none';
        });
    }
    
    // Update charts based on filtered data
    updateChartsWithFilteredData();
}