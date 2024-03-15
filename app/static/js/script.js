document.addEventListener("DOMContentLoaded", function() {
    // Listening for click event on the close button
    document.querySelector('.btn-close[data-bs-dismiss="alert"]').addEventListener('click', function() {
        // Hide the advisory section when close button is clicked
        this.closest('.alert-dismissible').style.display = 'none';
    });
});
