window.addEventListener("DOMContentLoaded", () => {
  const chatContainer = document.querySelector(".chat-history");

  chatContainer.addEventListener("scroll", () => {
    if (chatContainer.scrollTop === 0) {
      // Fetch and append older messages when scrolled to the top
      fetchOlderMessages();
    }
  });

  function fetchOlderMessages() {
    // Implement AJAX call to fetch older messages and prepend to the chat history
  }
});
