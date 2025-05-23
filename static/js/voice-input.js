// Voice Input for Money Tracker
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on a page with transaction forms
    if (document.querySelector('form#expenseForm') || document.querySelector('form#salaryForm')) {
        initVoiceInput();
    }
});

function initVoiceInput() {
    // Check if browser supports speech recognition
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        console.log('Speech recognition not supported in this browser');
        return;
    }
    
    // Add voice input buttons to relevant form fields
    addVoiceInputToField('amount', 'Enter amount');
    addVoiceInputToField('description', 'Enter description');
    
    // Add a voice input button for the entire form
    addFullFormVoiceInput();
}

function addVoiceInputToField(fieldId, placeholder) {
    const field = document.getElementById(fieldId);
    if (!field) return;
    
    // Create container to wrap the input field
    const parent = field.parentNode;
    const container = document.createElement('div');
    container.className = 'voice-input-container';
    
    // Move the field into the container
    parent.replaceChild(container, field);
    container.appendChild(field);
    
    // Add voice input button
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'voice-input-button';
    button.innerHTML = '<i class="bi bi-mic"></i>';
    button.setAttribute('title', 'Click to use voice input');
    button.setAttribute('data-target-field', fieldId);
    button.setAttribute('data-placeholder', placeholder);
    
    // Add event listener
    button.addEventListener('click', function() {
        startVoiceRecognition(fieldId, placeholder);
    });
    
    container.appendChild(button);
}

function addFullFormVoiceInput() {
    // Create a button for full form voice input
    const form = document.querySelector('form#expenseForm') || document.querySelector('form#salaryForm');
    if (!form) return;
    
    const submitButton = form.querySelector('button[type="submit"]');
    if (!submitButton) return;
    
    const voiceButton = document.createElement('button');
    voiceButton.type = 'button';
    voiceButton.className = 'btn btn-outline-primary ms-2';
    voiceButton.innerHTML = '<i class="bi bi-mic me-1"></i>Voice Input';
    voiceButton.id = 'fullFormVoiceInput';
    
    // Add event listener
    voiceButton.addEventListener('click', startFullFormVoiceInput);
    
    // Add button next to submit button
    submitButton.parentNode.insertBefore(voiceButton, submitButton.nextSibling);
}

function startVoiceRecognition(fieldId, placeholder) {
    const field = document.getElementById(fieldId);
    const button = document.querySelector(`button[data-target-field="${fieldId}"]`);
    
    // Create speech recognition instance
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    
    // Configure recognition
    recognition.lang = 'en-US';
    recognition.continuous = false;
    recognition.interimResults = false;
    
    // Show recording state
    button.classList.add('recording');
    button.innerHTML = '<i class="bi bi-mic-fill"></i>';
    
    // Show feedback to user
    const originalPlaceholder = field.placeholder;
    field.placeholder = placeholder + '...';
    
    // Start listening
    recognition.start();
    
    // Handle results
    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        field.value = transcript;
        field.focus();
        
        // Trigger input event to activate any listeners
        field.dispatchEvent(new Event('input', { bubbles: true }));
        
        // If this is the amount field, try to extract a number
        if (fieldId === 'amount') {
            const numberMatch = transcript.match(/\d+(\.\d+)?/);
            if (numberMatch) {
                field.value = numberMatch[0];
            }
        }
    };
    
    // Handle end of speech recognition
    recognition.onend = function() {
        button.classList.remove('recording');
        button.innerHTML = '<i class="bi bi-mic"></i>';
        field.placeholder = originalPlaceholder;
    };
    
    // Handle errors
    recognition.onerror = function(event) {
        console.error('Speech recognition error', event.error);
        button.classList.remove('recording');
        button.innerHTML = '<i class="bi bi-mic"></i>';
        field.placeholder = originalPlaceholder;
        
        if (event.error === 'not-allowed') {
            showNotification('Microphone access denied. Please enable microphone permissions.', 'warning');
        } else {
            showNotification('Voice recognition error: ' + event.error, 'warning');
        }
    };
}

function startFullFormVoiceInput() {
    // Create speech recognition instance
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    
    // Configure recognition
    recognition.lang = 'en-US';
    recognition.continuous = false;
    recognition.interimResults = false;
    
    // Show recording state
    const button = document.getElementById('fullFormVoiceInput');
    button.classList.add('btn-danger');
    button.classList.remove('btn-outline-primary');
    button.innerHTML = '<i class="bi bi-mic-fill me-1"></i>Listening...';
    
    // Create a modal to show instructions and feedback
    createVoiceInputModal();
    const modal = new bootstrap.Modal(document.getElementById('voiceInputModal'));
    modal.show();
    
    // Update modal status
    document.getElementById('voiceInputStatus').textContent = 'Listening...';
    
    // Start listening
    recognition.start();
    
    // Handle results
    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript.toLowerCase();
        document.getElementById('voiceInputTranscript').textContent = transcript;
        
        // Process the transcript
        processVoiceCommand(transcript);
    };
    
    // Handle end of speech recognition
    recognition.onend = function() {
        button.classList.remove('btn-danger');
        button.classList.add('btn-outline-primary');
        button.innerHTML = '<i class="bi bi-mic me-1"></i>Voice Input';
        
        // Update modal status
        document.getElementById('voiceInputStatus').textContent = 'Processing...';
        
        // Close modal after a delay
        setTimeout(() => {
            const modalElement = document.getElementById('voiceInputModal');
            const modalInstance = bootstrap.Modal.getInstance(modalElement);
            if (modalInstance) {
                modalInstance.hide();
            }
        }, 2000);
    };
    
    // Handle errors
    recognition.onerror = function(event) {
        console.error('Speech recognition error', event.error);
        button.classList.remove('btn-danger');
        button.classList.add('btn-outline-primary');
        button.innerHTML = '<i class="bi bi-mic me-1"></i>Voice Input';
        
        // Update modal status
        document.getElementById('voiceInputStatus').textContent = 'Error: ' + event.error;
        
        if (event.error === 'not-allowed') {
            showNotification('Microphone access denied. Please enable microphone permissions.', 'warning');
        } else {
            showNotification('Voice recognition error: ' + event.error, 'warning');
        }
    };
}

function createVoiceInputModal() {
    // Remove existing modal if it exists
    const existingModal = document.getElementById('voiceInputModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Create modal HTML
    const modalHTML = `
    <div class="modal fade" id="voiceInputModal" tabindex="-1" aria-labelledby="voiceInputModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="voiceInputModalLabel">
                        <i class="bi bi-mic-fill me-2"></i>Voice Input
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <p class="mb-3">Speak naturally to add a transaction. For example:</p>
                    <div class="alert alert-info">
                        <p class="mb-1">"Add expense of 25 dollars for groceries"</p>
                        <p class="mb-1">"Spent 50 dollars on dinner yesterday"</p>
                        <p class="mb-1">"Add income of 1000 dollars for salary"</p>
                    </div>
                    
                    <div class="mt-4">
                        <p class="mb-1"><strong>Status:</strong> <span id="voiceInputStatus">Initializing...</span></p>
                        <p class="mb-1"><strong>Heard:</strong> <span id="voiceInputTranscript">Waiting for speech...</span></p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    `;
    
    // Append modal to body
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

function processVoiceCommand(transcript) {
    // Extract amount
    const amountRegex = /(\d+(\.\d+)?)\s*(dollars|dollar|bucks|rupees|rupee)/i;
    const amountMatch = transcript.match(amountRegex);
    
    if (amountMatch) {
        const amount = amountMatch[1];
        document.getElementById('amount').value = amount;
    }
    
    // Extract date
    let date = new Date();
    if (transcript.includes('yesterday')) {
        date.setDate(date.getDate() - 1);
    } else if (transcript.includes('tomorrow')) {
        date.setDate(date.getDate() + 1);
    } else if (transcript.includes('last week')) {
        date.setDate(date.getDate() - 7);
    }
    
    // Format date as YYYY-MM-DD
    const formattedDate = date.toISOString().split('T')[0];
    const dateField = document.getElementById('date');
    if (dateField) {
        dateField.value = formattedDate;
    }
    
    // Extract description and category
    let description = '';
    let category = '';
    
    // Common expense categories
    const categories = [
        'groceries', 'food', 'restaurant', 'dining', 'dinner', 'lunch', 'breakfast',
        'transportation', 'uber', 'taxi', 'bus', 'train', 'gas', 'fuel',
        'utilities', 'electricity', 'water', 'internet', 'phone', 'bill', 'bills',
        'rent', 'mortgage', 'housing',
        'entertainment', 'movie', 'movies', 'concert', 'subscription',
        'shopping', 'clothes', 'clothing', 'shoes',
        'health', 'medical', 'doctor', 'medicine', 'pharmacy',
        'education', 'tuition', 'books', 'course',
        'travel', 'vacation', 'hotel', 'flight'
    ];
    
    // Check for categories in the transcript
    for (const cat of categories) {
        if (transcript.includes(cat)) {
            category = cat;
            // Use the first found category as part of the description
            description = transcript.replace(amountRegex, '').replace(/(add expense|add income|spent|paid|for|on)/gi, '').trim();
            break;
        }
    }
    
    // If no specific category was found, use the whole transcript as description
    if (!description) {
        description = transcript.replace(amountRegex, '').replace(/(add expense|add income|spent|paid|for|on)/gi, '').trim();
    }
    
    // Set description field
    const descriptionField = document.getElementById('description');
    if (descriptionField && description) {
        descriptionField.value = description.charAt(0).toUpperCase() + description.slice(1);
    }
    
    // Try to set category if we found one
    if (category) {
        const categorySelect = document.getElementById('category');
        if (categorySelect) {
            // Find the closest matching option
            Array.from(categorySelect.options).forEach(option => {
                if (option.text.toLowerCase().includes(category)) {
                    categorySelect.value = option.value;
                }
            });
        }
    }
    
    // Show feedback to user
    showNotification('Voice input processed successfully!', 'success');
}