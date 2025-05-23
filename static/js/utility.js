// Utility functions for Money Tracker

/**
 * Shows a notification to the user
 * @param {string} message - The message to display
 * @param {string} type - The type of notification (success, info, warning, danger)
 */
function showNotification(message, type = 'info') {
    // Create notification container if it doesn't exist
    let container = document.getElementById('notification-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notification-container';
        container.className = 'notification-container';
        document.body.appendChild(container);
    }
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    
    // Add icon based on type
    let icon = '';
    switch (type) {
        case 'success':
            icon = '<i class="bi bi-check-circle-fill me-2"></i>';
            break;
        case 'warning':
            icon = '<i class="bi bi-exclamation-triangle-fill me-2"></i>';
            break;
        case 'danger':
            icon = '<i class="bi bi-x-circle-fill me-2"></i>';
            break;
        default:
            icon = '<i class="bi bi-info-circle-fill me-2"></i>';
    }
    
    // Set content
    notification.innerHTML = `
        <div class="notification-content">
            ${icon}
            <span>${message}</span>
        </div>
        <button type="button" class="btn-close btn-close-white notification-close" aria-label="Close"></button>
    `;
    
    // Add to container
    container.appendChild(notification);
    
    // Add event listener for close button
    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.addEventListener('click', () => {
        notification.classList.add('notification-hiding');
        setTimeout(() => {
            notification.remove();
        }, 300);
    });
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.classList.add('notification-hiding');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 300);
        }
    }, 5000);
    
    // Animate in
    setTimeout(() => {
        notification.classList.add('notification-visible');
    }, 10);
}

/**
 * Adds CSS styles for notifications if they don't exist
 */
function addNotificationStyles() {
    if (!document.getElementById('notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            .notification-container {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                display: flex;
                flex-direction: column;
                gap: 10px;
                max-width: 350px;
            }
            
            .notification {
                padding: 12px 15px;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                display: flex;
                justify-content: space-between;
                align-items: center;
                transform: translateX(120%);
                transition: transform 0.3s ease, opacity 0.3s ease;
                opacity: 0;
            }
            
            .notification-visible {
                transform: translateX(0);
                opacity: 1;
            }
            
            .notification-hiding {
                transform: translateX(120%);
                opacity: 0;
            }
            
            .notification-content {
                display: flex;
                align-items: center;
                margin-right: 10px;
            }
            
            .notification-success {
                background-color: #28a745;
                color: white;
            }
            
            .notification-info {
                background-color: #17a2b8;
                color: white;
            }
            
            .notification-warning {
                background-color: #ffc107;
                color: #212529;
            }
            
            .notification-danger {
                background-color: #dc3545;
                color: white;
            }
            
            .notification .btn-close {
                font-size: 0.8rem;
                padding: 0.25rem;
            }
            
            body.dark-mode .notification-warning {
                color: #212529;
            }
        `;
        document.head.appendChild(style);
    }
}

// Add notification styles when the document loads
document.addEventListener('DOMContentLoaded', function() {
    addNotificationStyles();
});