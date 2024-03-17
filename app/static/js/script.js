document.addEventListener("DOMContentLoaded", function() {
    const movableDiv = document.getElementById("movableDiv");
    movableDiv.addEventListener("click", function() {
      const maxX = window.innerWidth - this.offsetWidth;
      const maxY = window.innerHeight - this.offsetHeight;
      const randomX = Math.floor(Math.random() * maxX);
      const randomY = Math.floor(Math.random() * maxY);
      this.style.left = randomX + "px";
      this.style.top = randomY + "px";
    });
    document.querySelector('.btn-close[data-bs-dismiss="alert"]').addEventListener('click', function() {
        // Hide the advisory section when close button is clicked
        this.closest('.alert-dismissible').style.display = 'none';
    });
  });