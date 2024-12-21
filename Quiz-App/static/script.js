let score = 0; // Initialize score outside the function to track across questions

function checkAnswer(button) {
  // Get all buttons for the current question
  const options = button.parentNode.querySelectorAll(".option");

  // Disable all buttons after selection to prevent multiple clicks
  options.forEach((option) => {
    option.disabled = true;

    // Highlight correct and incorrect answers
    if (option.dataset.correct === "true") {
      option.style.backgroundColor = "lightgreen"; // Highlight correct answers
      if (option === button) {
        score += 1; // Increment score if the clicked button is correct
      }
    } else if (option === button) {
      option.style.backgroundColor = "lightcoral"; // Highlight the clicked incorrect answer
    }
  });

  // Check if the quiz is finished
  if (isQuizFinished()) {
    displayScore();
  }
}

// Helper function to determine if the quiz is finished
function isQuizFinished() {
  const remainingButtons = document.querySelectorAll(".option:not([disabled])");
  return remainingButtons.length === 0;
}

// Display the final score
function displayScore() {
  const quizContainer = document.querySelector(".quiz");
  const scoreMessage = document.createElement("div");
  scoreMessage.className = "score-message";
  scoreMessage.innerHTML = `<h2>Your Score: ${score}</h2>`;
  quizContainer.appendChild(scoreMessage);
}
