// Profile functionality for traveLLex
document.addEventListener('DOMContentLoaded', function() {
    // Initialize profile tabs when the page loads
    initProfileTabs();
    
    // Handle edit profile button
    const editProfileBtn = document.querySelector('.edit-profile-btn');
    if (editProfileBtn) {
        editProfileBtn.addEventListener('click', function() {
            alert('Edit profile functionality will be implemented soon!');
        });
    }
    
    // Close profile popup when ESC key is pressed
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const profilePopup = document.querySelector('.profile-popup');
            if (profilePopup && profilePopup.classList.contains('show')) {
                profilePopup.classList.remove('show');
            }
        }
    });
    
    // Close profile popup when clicking on backdrop
    document.addEventListener('click', function(e) {
        const profilePopup = document.querySelector('.profile-popup');
        if (profilePopup && e.target === profilePopup) {
            profilePopup.classList.remove('show');
        }
    });
    
    // Add event listener for delete account button
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('btn-danger') && e.target.textContent.includes('Delete Account')) {
            if (confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
                // TODO: Add AJAX call to delete account
                alert('Account deletion functionality will be implemented soon.');
            }
        }
    });
    
    // Handle remove saved destination
    const removeSavedBtns = document.querySelectorAll('.remove-saved');
    removeSavedBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Get the destination card
            const card = this.closest('.destination-card');
            
            // Confirm removal
            if (confirm('Are you sure you want to remove this destination from your saved list?')) {
                // Add a fade-out animation
                card.style.opacity = 0;
                card.style.transform = 'scale(0.8)';
                
                // In a real app, you would make an API call here to remove from user's saved list
                
                // Remove card after animation
                setTimeout(() => {
                    card.remove();
                    
                    // Check if there are no more saved destinations
                    const savedDestinations = document.querySelectorAll('.destination-card');
                    if (savedDestinations.length === 0) {
                        // Show the no-data message
                        const savedContainer = document.querySelector('.saved-destinations');
                        savedContainer.innerHTML = `
                            <div class="no-data">
                                <img src="/static/images/no-saved.svg" alt="No saved destinations">
                                <p>You haven't saved any destinations yet.</p>
                                <a href="/destinations" class="btn btn-primary">Explore Destinations</a>
                            </div>
                        `;
                    }
                }, 300);
            }
        });
    });
});

// Function to open profile popup
function openProfilePopup() {
    const profilePopup = document.querySelector('.profile-popup');
    if (profilePopup) {
        profilePopup.classList.add('show');
    }
}

// Function to close profile popup
function closeProfilePopup() {
    const profilePopup = document.querySelector('.profile-popup');
    if (profilePopup) {
        profilePopup.classList.remove('show');
    }
}

// Function to initialize profile tabs
function initProfileTabs() {
    const tabBtns = document.querySelectorAll('.profile-tabs .tab-btn');
    if (!tabBtns.length) return;
    
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Remove active class from all buttons
            tabBtns.forEach(b => b.classList.remove('active'));
            // Add active class to clicked button
            this.classList.add('active');
            
            // Hide all tab contents
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Show the selected tab content
            const tabId = this.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
        });
    });
    
    // Add event listeners for remove saved destination buttons
    const removeSavedBtns = document.querySelectorAll('.remove-saved');
    removeSavedBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const destId = this.getAttribute('data-id');
            // TODO: Add AJAX call to remove saved destination
            
            // For now, just remove the card from the UI
            this.closest('.destination-card').remove();
        });
    });
} 