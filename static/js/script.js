// Simple JavaScript for additional interactivity
document.addEventListener('DOMContentLoaded', function() {
    // Add any client-side functionality here
    console.log('Land Registry System loaded');
    
    // Example: Confirm before important actions
    const deleteButtons = document.querySelectorAll('.btn-danger');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to perform this action?')) {
                e.preventDefault();
            }
        });
    });
});