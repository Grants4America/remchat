document.getElementById("myForm").addEventListener("submit", function (e) {
  const password = document.getElementById("password").value;
  const confirmPassword = document.getElementById("confirmPassword").value;
  const errorMessage = document.getElementById("errorMessage");

  if (password !== confirmPassword) {
    e.preventDefault(); // Prevent form submission
    errorMessage.textContent = "Passwords do not match!";

    // Clear the error message after 3 seconds
    setTimeout(() => {
      errorMessage.textContent = "";
    }, 3000);
  } else {
    errorMessage.textContent = ""; // Clear error message if passwords match
  }
});
