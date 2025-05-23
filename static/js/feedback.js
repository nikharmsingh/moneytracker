// Feedback functionality for Money Tracker
document.addEventListener('DOMContentLoaded', function() {
    // Initialize feedback form
    initFeedbackForm();
});

function initFeedbackForm() {
    const submitButton = document.getElementById('submitFeedback');
    if (!submitButton) return;
    
    submitButton.addEventListener('click', function() {
        const form = document.getElementById('feedbackForm');
        
        // Basic form validation
        const feedbackType = document.getElementById('feedbackType').value;
        const subject = document.getElementById('feedbackSubject').value;
        const message = document.getElementById('feedbackMessage').value;
        
        if (!feedbackType || !subject || !message) {
            showNotification('Please fill in all required fields.', 'warning');
            return;
        }
        
        // Check if screenshot should be included
        const includeScreenshot = document.getElementById('includeScreenshot').checked;
        let screenshotData = null;
        
        if (includeScreenshot) {
            // In a real implementation, you would use a library like html2canvas
            // For this demo, we'll just simulate it
            screenshotData = 'screenshot_placeholder';
        }
        
        // Collect feedback data
        const feedbackData = {
            type: feedbackType,
            subject: subject,
            message: message,
            screenshot: screenshotData,
            userAgent: navigator.userAgent,
            timestamp: new Date().toISOString(),
            url: window.location.href
        };
        
        // In a real implementation, you would send this data to your server
        // For this demo, we'll just log it and show a success message
        console.log('Feedback data:', feedbackData);
        
        // Store in localStorage for demo purposes
        const storedFeedback = JSON.parse(localStorage.getItem('userFeedback') || '[]');
        storedFeedback.push(feedbackData);
        localStorage.setItem('userFeedback', JSON.stringify(storedFeedback));
        
        // Close the modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('feedbackModal'));
        modal.hide();
        
        // Show success message
        showNotification('Thank you for your feedback! We appreciate your input.', 'success');
        
        // Reset form
        form.reset();
    });
    
    // Add event listener for the tour menu item
    const startTourMenu = document.getElementById('start-tour-menu');
    if (startTourMenu) {
        startTourMenu.addEventListener('click', function(e) {
            e.preventDefault();
            if (typeof startGuidedTour === 'function') {
                startGuidedTour();
            } else {
                showNotification('Tour functionality is not available on this page.', 'info');
            }
        });
    }
}

// Function to take a screenshot using html2canvas
// Note: In a real implementation, you would need to include the html2canvas library
function takeScreenshot() {
    if (typeof html2canvas !== 'undefined') {
        html2canvas(document.body).then(canvas => {
            return canvas.toDataURL('image/png');
        });
    } else {
        console.warn('html2canvas library not loaded');
        return null;
    }
}