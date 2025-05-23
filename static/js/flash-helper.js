// Helper function to create flash messages
function createFlashMessage(message, type = 'info') {
    // Find or create flash container
    const flashContainer = document.querySelector('.flash-container') || document.createElement('div');
    if (!document.querySelector('.flash-container')) {
        flashContainer.className = 'flash-container';
        document.body.appendChild(flashContainer);
    }
    
    // Create new flash message
    const flashMessage = document.createElement('div');
    flashMessage.className = `flash-message ${type}`;
    flashMessage.innerHTML = `
        <div class="flash-content">
            <p>${message}</p>
        </div>
        <button class="close-flash"><i class="fas fa-times"></i></button>
    `;
    
    // Add to container
    flashContainer.appendChild(flashMessage);
    
    // Add close button functionality
    flashMessage.querySelector('.close-flash').addEventListener('click', function() {
        flashMessage.style.opacity = '0';
        flashMessage.style.transform = 'translateX(100%)';
        setTimeout(() => {
            flashMessage.remove();
        }, 300);
    });
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
        flashMessage.style.opacity = '0';
        flashMessage.style.transform = 'translateX(100%)';
        setTimeout(() => {
            flashMessage.remove();
        }, 300);
    }, 5000);
    
    return flashMessage;
}
