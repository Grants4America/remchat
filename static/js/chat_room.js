document.addEventListener("DOMContentLoaded", function () {
  var chatHistory = document.getElementById("chat-history");

  if (chatHistory) {
    chatHistory.scrollTop = chatHistory.scrollHeight;
  }

  // Check if the browser supports notifications
  if ("Notification" in window && Notification.permission !== "granted") {
    Notification.requestPermission();
  }
});

var socket = io(); // Initialize Socket.IO

var myDiv = document.getElementById("targetUsername");
var targetUsername = myDiv ? myDiv.getAttribute("data-value") : "";

var myDiv2 = document.getElementById("room_id");
var room_id = myDiv2 ? myDiv2.getAttribute("data-value") : "";

socket.on("connect", function () {
  const room = room_id; // Ensure the room is passed from Flask correctly
  console.log("Joining room: " + room);
  socket.emit("join", {
    room: room,
    target_username: targetUsername,
  });
});

// Function to show notifications
function showNotification(title, message) {
  if (Notification.permission === "granted") {
    var notification = new Notification(title, {
      body: message,
      icon: iconUrl,
    });

    // Set the notification to disappear after 5 seconds
    setTimeout(function () {
      notification.close();
    }, 5000); // 5 seconds
  }
}

// Listen for incoming messages
socket.on("message", function (data) {
  console.log("Message received: ", data);

  var sessionUser = document.getElementById("sessionUsername");
  var sessionUsername = sessionUser
    ? sessionUser.getAttribute("data-username")
    : "";

  var chatHistory = document.getElementById("chat-history");
  var chatBox = document.createElement("div");

  // Add data attributes to store sender and receiver information
  chatBox.setAttribute("data-sender", data.user);

  // Sanitize message content using DOMPurify
  var sanitizedMessage = DOMPurify.sanitize(data.msg);

  // Message structure using correct class names
  // <small class="sender-info"><em>${data.user}</em></small><br />
  chatBox.innerHTML = `
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
    chatHistory.scrollTop = chatHistory.scrollHeight;
  }

  // Show a notification if the window is not in focus
  if (!document.hasFocus()) {
    showNotification("New message from " + data.user, data.msg);
  }
});

function sendMessage() {
  var message = document.querySelector("textarea[name='message']").value;
  var userId = document.getElementById("chat-history").dataset.userId;
  var room = room_id;

  if (message) {
    console.log("Sending message: ", message + " to " + room);
    socket.emit("message", { msg: message, user_id: userId, room: room });

    document.querySelector("textarea[name='message']").value = ""; // Clear input
  } else {
    flash("Message cannot be empty.", "warning"); // Flash message if empty
  }
}
