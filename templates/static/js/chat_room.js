document.addEventListener("DOMContentLoaded", function () {
  var chatHistory = document.getElementById("chat-history");
  chatHistory.scrollTop = chatHistory.scrollHeight;
});

var socket = io(); // Initialize Socket.IO

var myDiv = document.getElementById("targetUsername");
var targetUsername = myDiv.getAttribute("data-value");

socket.on("connect", function () {
  const room = "{{ room }}"; // Use the room variable passed from Flask
  console.log("Joining room: " + room);
  socket.emit("join", {
    room: room,
    target_username: targetUsername,
  });
});

// Listen for incoming messages
socket.on("message", function (data) {
  console.log("Message received: ", data);

  var currentUser = document.getElementById("myDiv");
  var sessionUser = document.getElementById("sessionUsername");
  var sessionUsername = sessionUser.getAttribute("data-username");

  var chatHistory = document.getElementById("chat-history");
  var chatBox = document.createElement("div");

  // Add data attributes to store sender and receiver information
  chatBox.setAttribute("data-sender", data.user);

  // Sanitize message content
  var sanitizedMessage = DOMPurify.sanitize(data.msg);

  // Message structure using correct class names
  chatBox.innerHTML = `
    <small class="sender-info"><em>${data.user}</em></small><br />
    <span class="message-content">${sanitizedMessage}</span><br />
    <small class="timestamp-info"><em>${new Date().toLocaleString()}</em></small>
  `;

  // Check if the sender is the current user and align accordingly
  if (data.user === sessionUsername) {
    chatBox.classList.add("chat-box", "sent");
  } else {
    chatBox.classList.add("chat-box", "received");
  }

  // Append the new message to the chat history
  if (chatHistory) {
    chatHistory.appendChild(chatBox);
    // Auto-scroll to the latest message
    chatHistory.scrollTop = chatHistory.scrollHeight;
  }
});

function sendMessage() {
  var message = document.querySelector("textarea[name='message']").value;
  var userId = document.getElementById("chat-history").dataset.userId;
  var room = "{{ room }}";

  if (message) {
    console.log("Sending message: ", message + " to " + room);
    socket.emit("message", { msg: message, user_id: userId, room: room });

    // Optional: Display a loading indicator here while sending
    document.querySelector("textarea[name='message']").value = ""; // Clear input
  } else {
    flash("Message cannot be empty.", "warning"); // Flash message if empty
  }
}
