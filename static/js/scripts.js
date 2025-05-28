/**
 * General JavaScript for Automatic Answer Checker
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // Auto-close alert messages after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-persistent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Handle multiple choice option selection in question creation
    const questionType = document.getElementById('questionType');
    const multipleChoiceOptions = document.getElementById('multipleChoiceOptions');
    
    if (questionType && multipleChoiceOptions) {
        // Update visibility based on selected question type
        const updateVisibility = () => {
            if (questionType.value === 'multiple_choice') {
                multipleChoiceOptions.style.display = 'block';
            } else {
                multipleChoiceOptions.style.display = 'none';
            }
        };
        
        // Set initial visibility
        updateVisibility();
        
        // Listen for changes
        questionType.addEventListener('change', updateVisibility);
    }
    
    // Add confirmation for delete actions
    const deleteButtons = document.querySelectorAll('.btn-delete, button[type="submit"].btn-danger');
    deleteButtons.forEach(button => {
        if (!button.hasAttribute('data-confirm-attached')) {
            button.addEventListener('click', (e) => {
                const confirmMessage = button.getAttribute('data-confirm') || 'Are you sure you want to delete this item? This action cannot be undone.';
                
                if (!confirm(confirmMessage)) {
                    e.preventDefault();
                }
            });
            
            // Mark this button as having a confirmation attached
            button.setAttribute('data-confirm-attached', 'true');
        }
    });
    
    // Enhance multi-select inputs for exam question selection
    const questionSelect = document.querySelector('select[multiple]');
    if (questionSelect) {
        // Add helper text
        const helpText = document.createElement('small');
        helpText.classList.add('form-text', 'mt-2');
        helpText.textContent = 'Selected questions: ' + questionSelect.selectedOptions.length;
        questionSelect.parentNode.appendChild(helpText);
        
        // Update helper text when selection changes
        questionSelect.addEventListener('change', () => {
            helpText.textContent = 'Selected questions: ' + questionSelect.selectedOptions.length;
        });
    }
    
    // Prevent accidental navigation away from exam page
    const examForm = document.getElementById('examForm');
    if (examForm) {
        const warningHandler = (e) => {
            e.preventDefault();
            e.returnValue = '';
            return '';
        };
        
        // Add beforeunload event
        window.addEventListener('beforeunload', warningHandler);
        
        // Remove event on form submission
        examForm.addEventListener('submit', () => {
            window.removeEventListener('beforeunload', warningHandler);
        });
    }
});

/**
 * Format a timestamp in a human-friendly way
 * @param {Date} date - The date to format
 * @returns {string} Formatted date string
 */
function formatDateTime(date) {
    if (!(date instanceof Date)) {
        date = new Date(date);
    }
    
    const options = { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    
    return date.toLocaleDateString('en-US', options);
}

/**
 * Format a duration in minutes to hours and minutes
 * @param {number} minutes - The duration in minutes
 * @returns {string} Formatted duration string
 */
function formatDuration(minutes) {
    if (minutes < 60) {
        return `${minutes} min`;
    }
    
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    
    if (mins === 0) {
        return `${hours} hr`;
    }
    
    return `${hours} hr ${mins} min`;
}
