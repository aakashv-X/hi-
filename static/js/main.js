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

    // Modal functionality for login/signup
    const loginModal = document.getElementById('login-modal');
    const signupModal = document.getElementById('signup-modal');
    const modalCloseButtons = document.querySelectorAll('.modal-close');
    
    // Login/Signup buttons
    const loginButtons = document.querySelectorAll('a[href="/login"]');
    const signupButtons = document.querySelectorAll('a[href="/register"]');
    
    // Switch between modals
    const switchToSignup = document.getElementById('switch-to-signup');
    const switchToLogin = document.getElementById('switch-to-login');
    
    // Show login modal
    loginButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            loginModal.classList.add('show');
        });
    });
    
    // Show signup modal
    signupButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            signupModal.classList.add('show');
        });
    });
    
    // Close modals
    modalCloseButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            loginModal.classList.remove('show');
            signupModal.classList.remove('show');
        });
    });
    
    // Switch between login and signup
    if (switchToSignup) {
        switchToSignup.addEventListener('click', function(e) {
            e.preventDefault();
            loginModal.classList.remove('show');
            signupModal.classList.add('show');
        });
    }
    
    if (switchToLogin) {
        switchToLogin.addEventListener('click', function(e) {
            e.preventDefault();
            signupModal.classList.remove('show');
            loginModal.classList.add('show');
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
});

// Trip planner range slider
function updateRangeValue(slider) {
    const value = slider.value;
    const output = document.getElementById(slider.dataset.output);
    
    if (output) {
        output.textContent = '$' + value;
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