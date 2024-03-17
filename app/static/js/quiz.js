document.addEventListener("DOMContentLoaded", function () {
    const countdownDuration = 34;
    let timeout;

    function startCountdown() {
        let timeRemaining = countdownDuration;
        updateTimerDisplay(timeRemaining);

        timeout = setInterval(() => {
            timeRemaining--;
            updateTimerDisplay(timeRemaining);

            if (timeRemaining === 1) {
                // Optional: Trigger automatic refresh or any other action at a specific time.
                // This block can be adjusted or removed based on specific requirements.
                window.location.reload(true); // Force reload from the server, avoiding cache.
            }

            if (timeRemaining <= 0) {
                clearInterval(timeout);
                document.getElementById("nextQuestionForm").submit(); // Example action when time is up.
            }
        }, 1000);
    }

    function updateTimerDisplay(time) {
        const countdownTimer = document.getElementById("countdownTimer");
        if (countdownTimer) {
            countdownTimer.textContent = `${time} ${time > 1 ? "seconds" : "second"}`;
            if (time <= 0) {
                countdownTimer.textContent = timeUpMessage();
            }
        }
    }

    function timeUpMessage() {
        const lang = document.documentElement.lang;
        return lang === 'en' ? "Time is up!" : "Temps écoulé !";
    }

    function setupNotification() {
        const selectElement = document.querySelector('select[name="filter"]');
        const notificationElement = document.getElementById('notification');

        if (selectElement && notificationElement) {
            selectElement.addEventListener('change', function () {
                const selectedOptionText = selectElement.options[selectElement.selectedIndex].text;
                notificationElement.innerHTML = `<span class="me-2">✅</span>${selectedOptionText} selected.`;
                notificationElement.classList.remove('d-none');

                setTimeout(() => {
                    notificationElement.classList.add('d-none');
                }, 5000);
            });
        }
    }

    function makeDivsClickable() {
        document.querySelectorAll('.clickable-div').forEach(div => {
            div.addEventListener('click', function () {
                window.location.href = this.getAttribute('data-href');
            });
        });
    }

    function validateForm() {
        const validationAlert = document.getElementById("validationAlert");
        if (!document.querySelector('input[name="choice"]:checked')) {
            validationAlert.classList.remove("d-none");
            validationAlert.textContent = "Please select an option."; // Adjust the message as needed
            return false;
        }
        validationAlert.classList.add("d-none");
        return true;
    }

    // Initialization
    startCountdown();
    setupNotification();
    makeDivsClickable();
});
