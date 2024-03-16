document.addEventListener("DOMContentLoaded", function () {
    const countdownDuration = 35;
    let timeout;
  
    // Starts the countdown timer
    function startCountdown() {
        let timeRemaining = countdownDuration;
        updateTimerDisplay(timeRemaining);
  
        timeout = setInterval(() => {
            timeRemaining--;
            updateTimerDisplay(timeRemaining);
  
            if (timeRemaining <= 0) {
                clearInterval(timeout);
                document.getElementById("nextQuestionForm").submit(); // Consider adding a check if this element exists
            }
        }, 1000);
    }
  
    // Updates the display of the countdown timer
    function updateTimerDisplay(time) {
        const countdownTimer = document.getElementById("countdownTimer");
        if (countdownTimer) { // Check if element exists
            countdownTimer.textContent = `${time} ${time > 1 ? "seconds" : "second"}`;
            if (time <= 0) {
                countdownTimer.textContent = timeUpMessage();
            }
        }
    }
  
    // Dynamic message based on user's language
    function timeUpMessage() {
        const lang = document.documentElement.lang; // Assumes <html lang="en"> or similar
        return lang === 'en' ? "Time is up!" : "Temps écoulé !";
    }

    // Notification and filter change handling
    function setupNotification() {
        const selectElement = document.querySelector('select[name="filter"]');
        const notificationElement = document.getElementById('notification');
      
        if (selectElement && notificationElement) {
            selectElement.addEventListener('change', function() {
                const selectedOptionText = selectElement.options[selectElement.selectedIndex].text;
                notificationElement.innerHTML = `<span class="me-2">✅</span>${selectedOptionText} selected.`;
                notificationElement.classList.remove('d-none');
                
                setTimeout(() => {
                    notificationElement.classList.add('d-none');
                }, 5000);
            });
        }
    }
    
    // Making divs clickable
    function makeDivsClickable() {
        document.querySelectorAll('.clickable-div').forEach(div => {
            div.addEventListener('click', function() {
                window.location.href = this.getAttribute('data-href');
            });
        });
    }

      // Validates the form before submitting
      function validateForm() {
        const validationAlert = document.getElementById("validationAlert");
        if (!document.querySelector('input[name="choice"]:checked')) {
          validationAlert.classList.remove("d-none");
          // Use |tojson filter for safe string handling
          validationAlert.textContent = "Veuillez s\u00e9lectionner une option.";
          return false;
        }
        validationAlert.classList.add("d-none");
        return true;
      }

    // Event Listeners
    startCountdown();
    setupNotification();
    makeDivsClickable();
});
