document.addEventListener("DOMContentLoaded", (event) => {
  // Clear form data on page reload
  const forms = document.querySelectorAll("form");
  forms.forEach((form) => {
    form.reset(); // Clears all input fields on load
  });

  // Prevent form resubmission on refresh
  if (window.history.replaceState) {
    window.history.replaceState(null, null, window.location.href);
  }

  // Flash message animation (fade out after 5 seconds)
  setTimeout(() => {
    const flashes = document.querySelectorAll(".flashes .alert");
    flashes.forEach((flash) => {
      flash.style.transition = "opacity 1s ease-out";
      flash.style.opacity = 0;
      setTimeout(() => {
        flash.remove();
      }, 1000);
    });
  }, 5000);

  // Navbar toggle functionality
  const navToggle = document.querySelector(".nav-toggle");
  const navbar = document.querySelector(".navbar");

  if (navToggle && navbar) {
    // Check for elements before adding event listener
    navToggle.addEventListener("click", function () {
      navbar.classList.toggle("show");
      // Optional: Toggle ARIA attributes for accessibility
      const isExpanded = navbar.classList.contains("show");
      navToggle.setAttribute("aria-expanded", isExpanded);
      navToggle.setAttribute("aria-controls", "navbar");
    });
  }
});

window.addEventListener("beforeunload", function () {
  localStorage.setItem("scrollPosition", window.scrollY);
  localStorage.setItem("pageURL", window.location.href);
});

window.addEventListener("pagehide", function () {
  localStorage.setItem("scrollPosition", window.scrollY);
  localStorage.setItem("pageURL", window.location.href);
});

// Restore scroll position on pageshow
window.addEventListener("pageshow", function () {
  const scrollPosition = localStorage.getItem("scrollPosition");
  const savedPageURL = localStorage.getItem("pageURL");

  if (scrollPosition && savedPageURL === window.location.href) {
    window.scrollTo(0, parseInt(scrollPosition));
  }
});
