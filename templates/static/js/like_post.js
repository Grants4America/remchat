console.log("I am in the script");

var socket = io();

/**
 * Listens for 'like_response' events from the server.
 * @param {Object} data - Contains a message and status from the server.
 */
socket.on("like_response", function (data) {
  console.log(data.message);
  // Optionally, display the message to the user (alert, UI message, etc.)
});

/**
 * Handles the click event when a user likes or unlikes a post.
 * It updates the like button text and the displayed like count on the page.
 *
 * @param {number} post_id - The ID of the post to like/unlike.
 */
function like_post(post_id) {
  var button_value = document.getElementById("button_value_" + post_id);
  var like_count = document.getElementById("like-count-" + post_id);

  // Extract the current like count by removing " Likes" from the inner text
  var count_value = parseInt(like_count.innerText.replace(" Likes", ""));

  // Clean up the button value by converting to lowercase and trimming spaces
  var button_text = button_value.value.toLowerCase().trim();

  // Toggle the like/unlike UI feedback based on cleaned button value
  if (button_text === "like") {
    button_value.value = "Liked";
    like_count.innerText = count_value + 1 + " Likes"; // Increment the like count
    button_value.style.backgroundColor = "#355839";
    button_value.style.color = "#fff";
  } else if (button_text === "liked") {
    if (count_value > 0) {
      button_value.value = "Like";
      like_count.innerText = count_value - 1 + " Likes"; // Decrement the like count
      button_value.style.backgroundColor = "#dcf8c6";
      button_value.style.color = "rgb(51, 204, 102)";
    }
  }

  // Emit the like event to the server via WebSocket
  socket.emit("like_post", { post_id: post_id });
}
