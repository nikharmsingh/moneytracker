// Touch gestures for mobile users

document.addEventListener('DOMContentLoaded', () => {
  // Initialize touch gesture handlers
  initSwipeToDelete();
  initPullToRefresh();
  initLongPressActions();
});

// Swipe to delete functionality for transaction items
function initSwipeToDelete() {
  const transactionItems = document.querySelectorAll('.transaction-item');
  
  transactionItems.forEach(item => {
    let startX, moveX, startTime;
    const threshold = 100; // Minimum distance to trigger swipe
    const restraint = 100; // Maximum vertical movement allowed
    const allowedTime = 300; // Maximum time allowed for swipe
    
    item.addEventListener('touchstart', function(e) {
      const touchObj = e.changedTouches[0];
      startX = touchObj.pageX;
      startY = touchObj.pageY;
      startTime = new Date().getTime();
      e.preventDefault();
    }, { passive: false });
    
    item.addEventListener('touchmove', function(e) {
      const touchObj = e.changedTouches[0];
      moveX = touchObj.pageX - startX;
      
      // If swiping left, show delete button
      if (moveX < 0) {
        item.style.transform = `translateX(${moveX}px)`;
      }
      
      e.preventDefault();
    }, { passive: false });
    
    item.addEventListener('touchend', function(e) {
      const touchObj = e.changedTouches[0];
      const distX = touchObj.pageX - startX;
      const distY = touchObj.pageY - startY;
      const elapsedTime = new Date().getTime() - startTime;
      
      const isSwipeLeft = (elapsedTime <= allowedTime && 
                          Math.abs(distX) >= threshold && 
                          Math.abs(distY) <= restraint && 
                          distX < 0);
      
      if (isSwipeLeft) {
        // Show delete confirmation
        item.classList.add('show-delete');
        
        // Add delete button if it doesn't exist
        if (!item.querySelector('.delete-btn')) {
          const deleteBtn = document.createElement('button');
          deleteBtn.className = 'btn btn-danger delete-btn';
          deleteBtn.innerHTML = '<i class="bi bi-trash"></i> Delete';
          deleteBtn.style.position = 'absolute';
          deleteBtn.style.right = '0';
          deleteBtn.style.top = '0';
          deleteBtn.style.height = '100%';
          
          deleteBtn.addEventListener('click', function() {
            // Get transaction ID from data attribute
            const transactionId = item.dataset.id;
            
            // Show confirmation dialog
            if (confirm('Are you sure you want to delete this transaction?')) {
              // Send delete request to server
              fetch(`/delete_transaction/${transactionId}`, {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                  'X-Requested-With': 'XMLHttpRequest'
                }
              })
              .then(response => response.json())
              .then(data => {
                if (data.success) {
                  // Remove item from DOM with animation
                  item.style.height = `${item.offsetHeight}px`;
                  item.style.opacity = '0';
                  setTimeout(() => {
                    item.style.height = '0';
                    item.style.padding = '0';
                    item.style.margin = '0';
                    setTimeout(() => {
                      item.remove();
                    }, 300);
                  }, 300);
                } else {
                  alert('Error deleting transaction: ' + data.message);
                  item.style.transform = 'translateX(0)';
                  item.classList.remove('show-delete');
                }
              })
              .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while deleting the transaction.');
                item.style.transform = 'translateX(0)';
                item.classList.remove('show-delete');
              });
            } else {
              // Reset position if cancelled
              item.style.transform = 'translateX(0)';
              item.classList.remove('show-delete');
            }
          });
          
          item.appendChild(deleteBtn);
        }
      } else {
        // Reset position
        item.style.transform = 'translateX(0)';
        item.classList.remove('show-delete');
      }
      
      e.preventDefault();
    }, { passive: false });
  });
}

// Pull to refresh functionality
function initPullToRefresh() {
  const content = document.querySelector('.container');
  if (!content) return;
  
  let touchStartY = 0;
  let touchEndY = 0;
  const minPullDistance = 100;
  let isPulling = false;
  let refreshIndicator;
  
  // Create refresh indicator
  function createRefreshIndicator() {
    refreshIndicator = document.createElement('div');
    refreshIndicator.className = 'refresh-indicator';
    refreshIndicator.innerHTML = '<i class="bi bi-arrow-clockwise"></i>';
    refreshIndicator.style.position = 'fixed';
    refreshIndicator.style.top = '0';
    refreshIndicator.style.left = '50%';
    refreshIndicator.style.transform = 'translateX(-50%) translateY(-100%)';
    refreshIndicator.style.padding = '10px 20px';
    refreshIndicator.style.backgroundColor = 'var(--primary-color)';
    refreshIndicator.style.color = 'white';
    refreshIndicator.style.borderRadius = '0 0 10px 10px';
    refreshIndicator.style.transition = 'transform 0.3s ease';
    refreshIndicator.style.zIndex = '1000';
    document.body.appendChild(refreshIndicator);
    return refreshIndicator;
  }
  
  // Get or create refresh indicator
  function getRefreshIndicator() {
    return document.querySelector('.refresh-indicator') || createRefreshIndicator();
  }
  
  content.addEventListener('touchstart', function(e) {
    // Only enable pull to refresh at the top of the page
    if (window.scrollY === 0) {
      touchStartY = e.touches[0].clientY;
      isPulling = true;
      refreshIndicator = getRefreshIndicator();
    }
  }, { passive: true });
  
  content.addEventListener('touchmove', function(e) {
    if (!isPulling) return;
    
    touchEndY = e.touches[0].clientY;
    const pullDistance = touchEndY - touchStartY;
    
    if (pullDistance > 0 && window.scrollY === 0) {
      // Show pull indicator with dynamic height based on pull distance
      const indicatorHeight = Math.min(pullDistance * 0.5, 60);
      refreshIndicator.style.transform = `translateX(-50%) translateY(${indicatorHeight - 100}%)`;
      
      // Prevent default scrolling when pulling
      if (pullDistance > 30) {
        e.preventDefault();
      }
    }
  }, { passive: false });
  
  content.addEventListener('touchend', function() {
    if (!isPulling) return;
    
    const pullDistance = touchEndY - touchStartY;
    
    if (pullDistance > minPullDistance && window.scrollY === 0) {
      // Show loading state
      refreshIndicator.innerHTML = '<i class="bi bi-arrow-repeat spin"></i> Refreshing...';
      refreshIndicator.style.transform = 'translateX(-50%) translateY(0)';
      
      // Reload the page after a short delay
      setTimeout(() => {
        window.location.reload();
      }, 1000);
    } else {
      // Hide indicator if pull not far enough
      refreshIndicator.style.transform = 'translateX(-50%) translateY(-100%)';
    }
    
    isPulling = false;
  }, { passive: true });
}

// Long press for additional options
function initLongPressActions() {
  const actionableElements = document.querySelectorAll('.card, .transaction-item, .budget-item');
  
  actionableElements.forEach(element => {
    let timer;
    const longPressDuration = 800; // ms
    
    element.addEventListener('touchstart', function(e) {
      timer = setTimeout(() => {
        // Create and show context menu
        showContextMenu(element, e.touches[0].clientX, e.touches[0].clientY);
      }, longPressDuration);
    }, { passive: true });
    
    element.addEventListener('touchend', function() {
      clearTimeout(timer);
    }, { passive: true });
    
    element.addEventListener('touchmove', function() {
      clearTimeout(timer);
    }, { passive: true });
  });
}

// Show context menu for long press
function showContextMenu(element, x, y) {
  // Remove any existing context menus
  const existingMenu = document.querySelector('.context-menu');
  if (existingMenu) {
    existingMenu.remove();
  }
  
  // Create context menu
  const contextMenu = document.createElement('div');
  contextMenu.className = 'context-menu';
  contextMenu.style.position = 'fixed';
  contextMenu.style.zIndex = '1050';
  contextMenu.style.backgroundColor = 'white';
  contextMenu.style.boxShadow = '0 2px 10px rgba(0,0,0,0.2)';
  contextMenu.style.borderRadius = '10px';
  contextMenu.style.padding = '10px 0';
  
  // Determine available actions based on element type
  let actions = [];
  
  if (element.classList.contains('transaction-item')) {
    actions = [
      { icon: 'bi-pencil', text: 'Edit', action: 'edit' },
      { icon: 'bi-trash', text: 'Delete', action: 'delete' },
      { icon: 'bi-files', text: 'Duplicate', action: 'duplicate' }
    ];
  } else if (element.classList.contains('budget-item')) {
    actions = [
      { icon: 'bi-pencil', text: 'Edit', action: 'edit' },
      { icon: 'bi-trash', text: 'Delete', action: 'delete' },
      { icon: 'bi-graph-up', text: 'View Details', action: 'view' }
    ];
  } else {
    actions = [
      { icon: 'bi-arrow-clockwise', text: 'Refresh', action: 'refresh' },
      { icon: 'bi-share', text: 'Share', action: 'share' }
    ];
  }
  
  // Add actions to menu
  actions.forEach(action => {
    const menuItem = document.createElement('div');
    menuItem.className = 'context-menu-item';
    menuItem.style.padding = '10px 20px';
    menuItem.style.cursor = 'pointer';
    menuItem.style.display = 'flex';
    menuItem.style.alignItems = 'center';
    menuItem.style.transition = 'background-color 0.2s';
    
    menuItem.innerHTML = `
      <i class="bi ${action.icon} me-2"></i>
      <span>${action.text}</span>
    `;
    
    menuItem.addEventListener('click', () => {
      handleContextMenuAction(action.action, element);
      contextMenu.remove();
    });
    
    menuItem.addEventListener('mouseover', () => {
      menuItem.style.backgroundColor = '#f0f0f0';
    });
    
    menuItem.addEventListener('mouseout', () => {
      menuItem.style.backgroundColor = 'transparent';
    });
    
    contextMenu.appendChild(menuItem);
  });
  
  // Add to document
  document.body.appendChild(contextMenu);
  
  // Position the menu
  const menuWidth = contextMenu.offsetWidth;
  const menuHeight = contextMenu.offsetHeight;
  const windowWidth = window.innerWidth;
  const windowHeight = window.innerHeight;
  
  // Adjust position to ensure menu is fully visible
  let menuX = x;
  let menuY = y;
  
  if (menuX + menuWidth > windowWidth) {
    menuX = windowWidth - menuWidth - 10;
  }
  
  if (menuY + menuHeight > windowHeight) {
    menuY = windowHeight - menuHeight - 10;
  }
  
  contextMenu.style.left = `${menuX}px`;
  contextMenu.style.top = `${menuY}px`;
  
  // Add click outside listener to close menu
  setTimeout(() => {
    document.addEventListener('click', function closeMenu(e) {
      if (!contextMenu.contains(e.target)) {
        contextMenu.remove();
        document.removeEventListener('click', closeMenu);
      }
    });
  }, 10);
  
  // Add haptic feedback if available
  if ('vibrate' in navigator) {
    navigator.vibrate(50);
  }
}

// Handle context menu actions
function handleContextMenuAction(action, element) {
  const id = element.dataset.id;
  
  switch (action) {
    case 'edit':
      if (element.classList.contains('transaction-item')) {
        window.location.href = `/edit_transaction/${id}`;
      } else if (element.classList.contains('budget-item')) {
        window.location.href = `/edit_budget/${id}`;
      }
      break;
      
    case 'delete':
      if (confirm('Are you sure you want to delete this item?')) {
        let endpoint = '';
        
        if (element.classList.contains('transaction-item')) {
          endpoint = `/delete_transaction/${id}`;
        } else if (element.classList.contains('budget-item')) {
          endpoint = `/delete_budget/${id}`;
        }
        
        if (endpoint) {
          fetch(endpoint, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-Requested-With': 'XMLHttpRequest'
            }
          })
          .then(response => response.json())
          .then(data => {
            if (data.success) {
              // Remove element with animation
              element.style.height = `${element.offsetHeight}px`;
              element.style.opacity = '0';
              setTimeout(() => {
                element.style.height = '0';
                element.style.padding = '0';
                element.style.margin = '0';
                setTimeout(() => {
                  element.remove();
                }, 300);
              }, 300);
            } else {
              alert('Error: ' + data.message);
            }
          })
          .catch(error => {
            console.error('Error:', error);
            alert('An error occurred.');
          });
        }
      }
      break;
      
    case 'duplicate':
      if (element.classList.contains('transaction-item')) {
        window.location.href = `/duplicate_transaction/${id}`;
      }
      break;
      
    case 'view':
      if (element.classList.contains('budget-item')) {
        window.location.href = `/budget_details/${id}`;
      }
      break;
      
    case 'refresh':
      window.location.reload();
      break;
      
    case 'share':
      if (navigator.share) {
        navigator.share({
          title: 'Money Tracker',
          text: 'Check out my financial tracking!',
          url: window.location.href
        })
        .catch(error => console.log('Error sharing:', error));
      } else {
        alert('Web Share API not supported in your browser.');
      }
      break;
  }
}