// Main JavaScript file for Money Tracker PWA

// Register service worker for PWA functionality
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/static/js/service-worker.js')
      .then(registration => {
        console.log('ServiceWorker registration successful with scope: ', registration.scope);
      })
      .catch(error => {
        console.log('ServiceWorker registration failed: ', error);
      });
  });
}

// Add to Home Screen functionality
let deferredPrompt;
const addToHomeBtn = document.getElementById('add-to-home');

window.addEventListener('beforeinstallprompt', (e) => {
  // Prevent Chrome 67 and earlier from automatically showing the prompt
  e.preventDefault();
  // Stash the event so it can be triggered later
  deferredPrompt = e;
  // Show the "Add to Home Screen" button
  if (addToHomeBtn) {
    addToHomeBtn.style.display = 'block';
    
    addToHomeBtn.addEventListener('click', () => {
      // Show the install prompt
      deferredPrompt.prompt();
      // Wait for the user to respond to the prompt
      deferredPrompt.userChoice.then((choiceResult) => {
        if (choiceResult.outcome === 'accepted') {
          console.log('User accepted the A2HS prompt');
        } else {
          console.log('User dismissed the A2HS prompt');
        }
        deferredPrompt = null;
        // Hide the button
        addToHomeBtn.style.display = 'none';
      });
    });
  }
});

// Detect online/offline status and show appropriate notifications
window.addEventListener('online', () => {
  showNotification('You are back online!', 'success');
  syncData();
});

window.addEventListener('offline', () => {
  showNotification('You are offline. Some features may be limited.', 'warning');
});

// Function to show notifications
function showNotification(message, type = 'info') {
  const alertContainer = document.createElement('div');
  alertContainer.className = `alert alert-${type} alert-dismissible fade show position-fixed bottom-0 end-0 m-3`;
  alertContainer.setAttribute('role', 'alert');
  alertContainer.style.zIndex = '1050';
  
  alertContainer.innerHTML = `
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
  `;
  
  document.body.appendChild(alertContainer);
  
  // Auto-dismiss after 5 seconds
  setTimeout(() => {
    const bsAlert = new bootstrap.Alert(alertContainer);
    bsAlert.close();
  }, 5000);
}

// Function to sync data when coming back online
function syncData() {
  // Get any locally stored data that needs to be synced
  const pendingTransactions = JSON.parse(localStorage.getItem('pendingTransactions') || '[]');
  
  if (pendingTransactions.length > 0) {
    showNotification('Syncing your transactions...', 'info');
    
    // Here you would implement the actual sync logic with your backend
    // For now, we'll just clear the pending transactions
    localStorage.removeItem('pendingTransactions');
    
    showNotification('All transactions synced successfully!', 'success');
  }
}

// Initialize tooltips and popovers
document.addEventListener('DOMContentLoaded', () => {
  // Initialize Bootstrap tooltips
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
  
  // Initialize Bootstrap popovers
  const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
  popoverTriggerList.map(function (popoverTriggerEl) {
    return new bootstrap.Popover(popoverTriggerEl);
  });
});