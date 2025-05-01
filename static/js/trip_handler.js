// Handle form submission, loading states, and date validation
document.addEventListener('DOMContentLoaded', function() {
    const tripForm = document.getElementById('trip-planner-form');
    const startDate = document.getElementById('start-date');
    const endDate = document.getElementById('end-date');

    // Set minimum date to today
    const today = new Date().toISOString().split('T')[0];
    startDate.min = today;
    endDate.min = today;

    // Update end date minimum when start date changes
    startDate.addEventListener('change', function() {
        endDate.min = this.value;
        if (endDate.value && endDate.value < this.value) {
            endDate.value = this.value;
        }
    });

    if (tripForm) {
        tripForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Validate dates
            if (!startDate.value || !endDate.value) {
                alert('Please select both start and end dates');
                return;
            }

            // Show loading state
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
            submitBtn.disabled = true;

            // Get form data
            const formData = new FormData(this);
            const data = {};
            formData.forEach((value, key) => {
                // Handle checkboxes arrays
                if (key.endsWith('[]')) {
                    const cleanKey = key.slice(0, -2);
                    if (!data[cleanKey]) {
                        data[cleanKey] = [];
                    }
                    data[cleanKey].push(value);
                } else {
                    data[key] = value;
                }
            });

            try {
                // Submit form data
                const response = await fetch('/generate-trip', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });

                const result = await response.json();

                if (result.success) {
                    window.location.href = '/packages';
                } else {
                    alert(result.error || 'Error generating trip. Please try again.');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error generating trip. Please try again.');
            } finally {
                // Restore button state
                submitBtn.innerHTML = originalBtnText;
                submitBtn.disabled = false;
            }
        });
    }

    // Add budget range value update function if it doesn't exist
    if (typeof updateRangeValue !== 'function') {
        window.updateRangeValue = function(input) {
            const output = document.getElementById(input.dataset.output);
            if (output) {
                output.textContent = '₹' + input.value;
            }
        }
    }
});