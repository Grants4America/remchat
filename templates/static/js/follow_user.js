var socket = io();

// Set up Socket.IO listener outside the function to avoid duplicate listeners
socket.on("follow_response", function (data) {
  console.log(data.message);
});

function follow_user(user_id) {
  var button_value = document.getElementById("button_value_" + user_id); // Get button for this user

  if (button_value.value === "Follow") {
    socket.emit("follow", { user_id: user_id }); // Send follow request
    button_value.value = "Following";
  } else {
    socket.emit("unfollow", { user_id: user_id }); // Send unfollow request
    button_value.value = "Follow";
  }
}
