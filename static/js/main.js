// Main JavaScript file for traveLLex

// Handle scroll effects
document.addEventListener('DOMContentLoaded', function() {
    // Scroll effect for header
    window.addEventListener('scroll', function() {
        const header = document.querySelector('header');
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });

    // Handle flash messages
    const flashMessages = document.querySelectorAll('.flash-message');
    const closeButtons = document.querySelectorAll('.close-flash');
    
    // Auto dismiss flash messages after 5 seconds
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            message.style.transform = 'translateX(100%)';
            setTimeout(() => {
                message.remove();
            }, 300);
        }, 5000);
    });
    
    // Close flash message when clicking the X button
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const message = this.closest('.flash-message');
            message.style.opacity = '0';
            message.style.transform = 'translateX(100%)';
            setTimeout(() => {
                message.remove();
            }, 300);
        });
    });

    // FAQ accordion functionality
    const faqItems = document.querySelectorAll('.faq-item');
    
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        
        question.addEventListener('click', () => {
            // Toggle active class on the clicked item
            item.classList.toggle('active');
            
            // Close other items
            faqItems.forEach(otherItem => {
                if (otherItem !== item && otherItem.classList.contains('active')) {
                    otherItem.classList.remove('active');
                }
            });
        });
    });

    // Modal functionality
    document.querySelectorAll('.modal-close').forEach(closeBtn => {
        closeBtn.addEventListener('click', function() {
            this.closest('.modal').classList.remove('show');
        });
    });

    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                this.classList.remove('show');
            }
        });
    });

    // Switch between login and signup forms
    const switchToSignup = document.getElementById('switch-to-signup');
    if (switchToSignup) {
        switchToSignup.addEventListener('click', function(e) {
            e.preventDefault();
            document.getElementById('login-modal').classList.remove('show');
            document.getElementById('signup-modal').classList.add('show');
        });
    }

    const switchToLogin = document.getElementById('switch-to-login');
    if (switchToLogin) {
        switchToLogin.addEventListener('click', function(e) {
            e.preventDefault();
            document.getElementById('signup-modal').classList.remove('show');
            document.getElementById('login-modal').classList.add('show');
        });
    }

    // Login button click
    const loginBtn = document.getElementById('login-btn');
    if (loginBtn) {
        loginBtn.addEventListener('click', function(e) {
            e.preventDefault();
            document.getElementById('login-modal').classList.add('show');
        });
    }

    // Signup button click
    const signupBtn = document.getElementById('signup-btn');
    if (signupBtn) {
        signupBtn.addEventListener('click', function(e) {
            e.preventDefault();
            document.getElementById('signup-modal').classList.add('show');
        });
    }

    // Password visibility toggle
    const passwordToggles = document.querySelectorAll('.password-toggle');
    
    passwordToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const passwordInput = this.previousElementSibling;
            const type = passwordInput.getAttribute('type');
            
            if (type === 'password') {
                passwordInput.setAttribute('type', 'text');
                this.querySelector('i').classList.remove('fa-eye');
                this.querySelector('i').classList.add('fa-eye-slash');
            } else {
                passwordInput.setAttribute('type', 'password');
                this.querySelector('i').classList.remove('fa-eye-slash');
                this.querySelector('i').classList.add('fa-eye');
            }
        });
    });

    // Handle profile links
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('profile-link') || e.target.closest('.profile-link')) {
            e.preventDefault();
            
            // Check if the profile popup exists
            let profilePopup = document.querySelector('.profile-popup');
            
            // If the popup doesn't exist, create it
            if (!profilePopup) {
                // Create the popup structure
                profilePopup = document.createElement('div');
                profilePopup.className = 'profile-popup';
                
                const popupContent = document.createElement('div');
                popupContent.className = 'profile-popup-content';
                
                const popupHeader = document.createElement('div');
                popupHeader.className = 'profile-popup-header';
                popupHeader.innerHTML = `
                    <h2>My Profile</h2>
                    <div class="profile-popup-close">
                        <i class="fas fa-times"></i>
                    </div>
                `;
                
                const popupBody = document.createElement('div');
                popupBody.className = 'profile-popup-body';
                popupBody.innerHTML = '<div class="loader" style="display:flex; justify-content:center; padding:30px;"><div class="spinner"></div></div>';
                
                popupContent.appendChild(popupHeader);
                popupContent.appendChild(popupBody);
                profilePopup.appendChild(popupContent);
                document.body.appendChild(profilePopup);
                
                // Add event listener to close button
                popupContent.querySelector('.profile-popup-close').addEventListener('click', function() {
                    profilePopup.classList.remove('show');
                });
            }
            
            // Show the popup
            profilePopup.classList.add('show');
            
            // Fetch the profile content
            fetch('/profile', {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                    return null;
                }
                return response.json().catch(() => response.text());
            })
            .then(data => {
                if (!data) return;
                
                const popupBody = profilePopup.querySelector('.profile-popup-body');
                
                if (typeof data === 'object') {
                    // Handle JSON response - build the profile content dynamically
                    popupBody.innerHTML = buildProfileContent(data);
                    // Initialize tabs and other functionality
                    if (typeof initProfileTabs === 'function') {
                        initProfileTabs();
                    }
                } else {
                    // Handle HTML response
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(data, 'text/html');
                    const dashboardContainer = doc.querySelector('.dashboard-container');
                    
                    if (dashboardContainer) {
                        popupBody.innerHTML = '';
                        popupBody.appendChild(dashboardContainer);
                        
                        // Initialize tabs and other functionality
                        if (typeof initProfileTabs === 'function') {
                            initProfileTabs();
                        }
                    } else {
                        // If dashboard container wasn't found in the response
                        popupBody.innerHTML = `
                            <div class="error-message" style="padding: 20px; text-align: center;">
                                <p>Could not load profile content. Please try again.</p>
                                <button class="btn btn-primary" onclick="window.location.href='/profile'">Go to Profile</button>
                            </div>
                        `;
                    }
                }
            })
            .catch(error => {
                console.error('Error loading profile:', error);
                profilePopup.querySelector('.profile-popup-body').innerHTML = `
                    <div class="error-message" style="padding: 20px; text-align: center;">
                        <p>Failed to load profile. Please try again later.</p>
                        <button class="btn btn-primary" onclick="window.location.href='/profile'">Go to Profile</button>
                    </div>
                `;
            });
        }
    });
});

// Trip planner range slider
function updateRangeValue(slider) {
    const value = slider.value;
    const output = document.getElementById(slider.dataset.output);
    
    if (output) {
        output.textContent = '₹' + value;
    }
}

// Form validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    let isValid = true;
    
    // Reset previous error messages
    const errorMessages = form.querySelectorAll('.error-message');
    errorMessages.forEach(msg => msg.remove());
    
    // Validate required fields
    const requiredFields = form.querySelectorAll('[required]');
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            displayError(field, 'This field is required');
        }
    });
    
    // Validate full name (only for signup form)
    if (formId === 'signup-form') {
        const fullName = form.querySelector('input[name="full_name"]');
        if (fullName && fullName.value.trim() && !isValidName(fullName.value)) {
            isValid = false;
            displayError(fullName, 'Please enter your full name (first and last name)');
        }
    }
    
    // Validate email format
    const emailFields = form.querySelectorAll('input[type="email"]');
    emailFields.forEach(field => {
        if (field.value.trim() && !isValidEmail(field.value)) {
            isValid = false;
            displayError(field, 'Please enter a valid email address');
        }
    });
    
    // Validate password strength for signup
    if (formId === 'signup-form') {
        const password = form.querySelector('input[name="password"]');
        if (password.value.trim() && !isStrongPassword(password.value)) {
            isValid = false;
            displayError(password, 'Password must be at least 8 characters with at least one uppercase letter, lowercase letter, and number');
        }
    }
    
    return isValid;
}

function isValidEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

function isValidName(name) {
    // Check if the name contains at least two words (first and last name)
    const words = name.trim().split(/\s+/);
    return words.length >= 2 && words[0].length > 0 && words[1].length > 0;
}

function isStrongPassword(password) {
    // At least 8 characters, 1 uppercase, 1 lowercase, 1 number
    const regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/;
    return regex.test(password);
}

function displayError(field, message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    errorDiv.style.color = 'red';
    errorDiv.style.fontSize = '0.8rem';
    errorDiv.style.marginTop = '5px';
    
    field.parentNode.appendChild(errorDiv);
    field.style.borderColor = 'red';
    
    field.addEventListener('input', function() {
        errorDiv.remove();
        field.style.borderColor = '';
    }, { once: true });
}

// User authentication functions
function loginUser() {
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const errorDiv = document.getElementById('login-error');
    
    fetch('/api/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = data.redirect;
        } else {
            errorDiv.style.display = 'block';
            errorDiv.textContent = data.message || 'Invalid email or password';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        errorDiv.style.display = 'block';
        errorDiv.textContent = 'An error occurred. Please try again.';
    });
}

function registerUser() {
    const fullName = document.getElementById('full-name').value;
    const email = document.getElementById('signup-email').value;
    const password = document.getElementById('signup-password').value;
    const terms = document.getElementById('terms').checked;
    const errorDiv = document.getElementById('signup-error');
    
    if (!terms) {
        errorDiv.style.display = 'block';
        errorDiv.textContent = 'You must accept the Terms & Conditions';
        return;
    }
    
    // Simple password validation
    if (password.length < 8 || !/[A-Z]/.test(password) || !/[a-z]/.test(password) || !/[0-9]/.test(password)) {
        errorDiv.style.display = 'block';
        errorDiv.textContent = 'Password must have at least 8 characters, 1 uppercase letter, 1 lowercase letter, and 1 number';
        return;
    }
    
    fetch('/api/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
            full_name: fullName,
            email,
            password
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = data.redirect;
        } else {
            errorDiv.style.display = 'block';
            errorDiv.textContent = data.message || 'Registration failed. Please try again.';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        errorDiv.style.display = 'block';
        errorDiv.textContent = 'An error occurred. Please try again.';
    });
}

// Function to build profile content from JSON data
function buildProfileContent(userData) {
    return `
    <div class="dashboard-container modern">
        <!-- Main Content -->
        <div class="dashboard-content">
            <div class="user-profile-header">
                <div class="user-avatar">
                    <img src="/static/images/default-avatar.jpg" alt="User Avatar">
                </div>
                <div class="user-info-header">
                    <h3>${userData.name}</h3>
                    <p>${userData.email}</p>
                    <span class="user-since">Member since ${userData.created_at ? new Date(userData.created_at).toLocaleDateString('en-US', {month: 'short', year: 'numeric'}) : 'N/A'}</span>
                </div>
            </div>
            
            <div class="profile-tabs">
                <button class="tab-btn active" data-tab="profile-info">
                    <i class="fas fa-user"></i> Profile
                </button>
                <button class="tab-btn" data-tab="trips-info">
                    <i class="fas fa-suitcase"></i> Trips <span class="count">${userData.trips ? userData.trips.length : '0'}</span>
                </button>
                <button class="tab-btn" data-tab="saved-info">
                    <i class="fas fa-heart"></i> Saved <span class="count">${userData.saved_destinations ? userData.saved_destinations.length : '0'}</span>
                </button>
                <button class="tab-btn" data-tab="settings-info">
                    <i class="fas fa-cog"></i> Settings
                </button>
            </div>
            
            <div class="tab-content active" id="profile-info">
                <div class="profile-details">
                    <div class="profile-info-card">
                        <h3>Personal Information</h3>
                        <div class="info-group">
                            <label>Full Name</label>
                            <p>${userData.name}</p>
                        </div>
                        <div class="info-group">
                            <label>Email Address</label>
                            <p>${userData.email}</p>
                        </div>
                        <div class="info-group">
                            <label>Phone Number</label>
                            <p>${userData.phone ? userData.phone : 'Not provided'}</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="tab-content" id="trips-info">
                ${buildTripsContent(userData.trips)}
            </div>
            
            <div class="tab-content" id="saved-info">
                ${buildSavedContent(userData.saved_destinations)}
            </div>
            
            <div class="tab-content" id="settings-info">
                <div class="settings-container">
                    <div class="profile-info-card">
                        <h3>Update Password</h3>
                        <form action="/update-password" method="POST" class="settings-form">
                            <div class="form-group">
                                <label for="current-password">Current Password</label>
                                <input type="password" id="current-password" name="current_password" required>
                            </div>
                            <div class="form-group">
                                <label for="new-password">New Password</label>
                                <input type="password" id="new-password" name="new_password" required>
                            </div>
                            <div class="form-group">
                                <label for="confirm-password">Confirm New Password</label>
                                <input type="password" id="confirm-password" name="confirm_password" required>
                            </div>
                            <button type="submit" class="btn btn-primary">Update Password</button>
                        </form>
                    </div>
                    
                    <div class="profile-info-card danger-zone">
                        <h3>Delete Account</h3>
                        <p>This action cannot be undone. All your data will be permanently deleted.</p>
                        <button class="btn btn-danger">Delete Account</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    `;
}

// Function to build trips content
function buildTripsContent(trips) {
    if (!trips || trips.length === 0) {
        return `
        <div class="no-data">
            <img src="/static/images/no-trips.svg" alt="No trips">
            <p>You haven't booked any trips yet.</p>
            <a href="/destinations" class="btn btn-primary">Explore Destinations</a>
        </div>
        `;
    }
    
    let tripsHTML = '<div class="trips-container">';
    
    trips.forEach(trip => {
        tripsHTML += `
        <div class="trip-card">
            <div class="trip-image">
                <img src="/static/images/destinations/${trip.destination.toLowerCase().replace(/\s+/g, '-')}.jpg" 
                     onerror="this.src='/static/images/placeholder-destination.jpg'" 
                     alt="${trip.destination}">
                <div class="trip-status ${trip.status.toLowerCase()}">${trip.status}</div>
            </div>
            <div class="trip-details">
                <h3>${trip.destination}</h3>
                <div class="trip-meta">
                    <span><i class="fas fa-calendar"></i> ${trip.start_date} - ${trip.end_date}</span>
                    <span><i class="fas fa-users"></i> ${trip.travelers} Travelers</span>
                </div>
            </div>
        </div>
        `;
    });
    
    tripsHTML += '</div>';
    return tripsHTML;
}

// Function to build saved destinations content
function buildSavedContent(destinations) {
    if (!destinations || destinations.length === 0) {
        return `
        <div class="no-data">
            <img src="/static/images/no-saved.svg" alt="No saved destinations">
            <p>You haven't saved any destinations yet.</p>
            <a href="/destinations" class="btn btn-primary">Explore Destinations</a>
        </div>
        `;
    }
    
    let destinationsHTML = '<div class="saved-destinations"><div class="destinations-grid">';
    
    destinations.forEach(dest => {
        destinationsHTML += `
        <div class="destination-card">
            <button class="remove-saved" data-id="${dest.id}"><i class="fas fa-times"></i></button>
            <div class="destination-image">
                <img src="/static/images/destinations/${dest.name.toLowerCase().replace(/\s+/g, '-')}.jpg" 
                     onerror="this.src='/static/images/placeholder-destination.jpg'" 
                     alt="${dest.name}">
            </div>
            <div class="destination-details">
                <h3>${dest.name}</h3>
                <p class="destination-location"><i class="fas fa-map-marker-alt"></i> ${dest.location}</p>
                <div class="destination-meta">
                    <span class="price">${dest.price ? dest.price : 'Price varies'}</span>
                    <span class="rating">
                        ${dest.rating ? `<i class="fas fa-star"></i> ${dest.rating}` : ''}
                    </span>
                </div>
            </div>
        </div>
        `;
    });
    
    destinationsHTML += '</div></div>';
    return destinationsHTML;
}

// Function to initialize profile tabs
function initProfileTabs() {
    const tabBtns = document.querySelectorAll('.profile-tabs .tab-btn');
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