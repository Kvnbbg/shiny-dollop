document.addEventListener("DOMContentLoaded", function() {
    // Check the user's language setting
    var userLang = '{{ session["lang"] }}'; // Assuming you're passing the session lang variable to your template
  
    // Find the close button by its class
    var closeButton = document.querySelector('.btn-close[data-bs-dismiss="alert"]');
  
    // Set the button's text based on the language
    if (userLang === 'fr') {
      closeButton.innerHTML = 'Fermé le conseil'; // Note: This might be 'Fermer le conseil' for correct French
    } else {
      closeButton.innerHTML = 'Close'; // Default to English
    }
  
    // Optional: Adjust the button appearance or functionality as needed
    closeButton.classList.add('custom-close'); // Apply custom class for styling if necessary
  });
  