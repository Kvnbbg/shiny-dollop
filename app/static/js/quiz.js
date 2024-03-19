document.addEventListener("DOMContentLoaded", function () {
    const movableDiv = document.getElementById("movableDiv");
    let isDragging = false;
    let countdownStarted = false; // New variable to track if countdown has started (initially set to false)

    // Enhance movableDiv to indicate it's clickable for starting the countdown
    movableDiv.style.cursor = 'pointer';
    movableDiv.title = "Click to start the countdown!";

    // Center the div on load
    centerDiv();

    function enableDrag() {
        movableDiv.addEventListener("mousedown", function (e) {
            if (countdownStarted) { // Allow dragging only after countdown has started
                isDragging = true;
                let prevX = e.clientX;
                let prevY = e.clientY;

                window.addEventListener("mousemove", move);
                window.addEventListener("mouseup", () => {
                    window.removeEventListener("mousemove", move);
                    isDragging = false;
                });

                function move(e) {
                    if (!isDragging) return;
                    let newX = prevX - e.clientX;
                    let newY = prevY - e.clientY;

                    const rect = movableDiv.getBoundingClientRect();
                    movableDiv.style.left = rect.left - newX + "px";
                    movableDiv.style.top = rect.top - newY + "px";

                    prevX = e.clientX;
                    prevY = e.clientY;
                }
            }
        });
    }

    movableDiv.addEventListener("click", function () {
        if (!countdownStarted) { // Initiate countdown on first click if not started
            startCountdown();
            countdownStarted = true;
            enableDrag(); // Enable dragging after the countdown starts
            this.style.cursor = 'grab'; // Change cursor to indicate movability
        } else {
            // Random movement functionality remains after countdown has started
            moveToRandomPosition();
        }
    });

    function moveToRandomPosition() {
        const maxX = window.innerWidth - movableDiv.offsetWidth;
        const maxY = window.innerHeight - movableDiv.offsetHeight;
        const randomX = Math.floor(Math.random() * maxX);
        const randomY = Math.floor(Math.random() * maxY);
        movableDiv.style.left = randomX + "px";
        movableDiv.style.top = randomY + "px";
    }

    function centerDiv() {
        const x = (window.innerWidth - movableDiv.offsetWidth) / 2;
        const y = (window.innerHeight - movableDiv.offsetHeight) / 2;
        movableDiv.style.left = `${x}px`;
        movableDiv.style.top = `${y}px`;
    }

    window.addEventListener("resize", centerDiv);

    // Countdown timer logic
    const countdownDuration = 34;

    function startCountdown() {
        let timeRemaining = countdownDuration;
        updateTimerDisplay(timeRemaining);

        const timeout = setInterval(() => {
            timeRemaining--;
            updateTimerDisplay(timeRemaining);

            if (timeRemaining <= 1) {
                window.location.reload(true); // Force reload to reset the countdown
                clearInterval(timeout);
               // document.getElementById("nextQuestionForm").submit();  Example action when time is up.
                
            }
        }, 1000);
    }

    function updateTimerDisplay(time) {
        const countdownTimer = document.getElementById("countdownTimer");
        if (countdownTimer) {
            countdownTimer.textContent = `${time} second${time !== 1 ? 's' : ''}`;
        }
    }
});
