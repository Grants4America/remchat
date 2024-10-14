from flask import Flask, render_template, request, url_for, redirect, session, flash
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_session import Session
import datetime

# Import functions from your modules
from functions.login_user import login_user
from functions.user_dashboard import user_dashboard
from functions.follow_user import follow_user
from functions.unfollow_user import unfollow_user
from functions.search_users_logic import search_users_logic
from functions.signup_user import signup_user
from functions.log_out import log_out
from functions.validate_user import validate_user
from functions.get_db_connection import get_db_connection

from chats.messages import messages as messages_view
from chats.chat_room import chat_room

from posts.posts import load_paginated_posts
from posts.like_post import like_post
from posts.delete_post import delete_post
from posts.post_content import post_content
from posts.post_comment import comment_page

# Initialize Flask app and configure session
app = Flask(__name__)
app.config['SECRET_KEY'] = "i_don't_have_it_yet"
app.config['SESSION_TYPE'] = "filesystem"

# Initialize session and Socket.IO
Session(app)
socketio = SocketIO(app, manage_session=True)

# Index route (login page)
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    """Render login page or redirect to dashboard if user is already logged in."""
    if 'username' in session:
        flash('You are already logged in!', 'warning')
        validate_user()
        return redirect(url_for('dashboard', username=session['username']))

    return login_user() if request.method == 'POST' else render_template('index.html')

# User signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handle user signup process."""
    if request.method == 'POST':
        return signup_user()
    return render_template('signup.html')

# Dashboard route
@app.route("/dashboard/<username>", methods=['GET', 'POST'])
def dashboard(username):
    """Render user dashboard."""
    validate_user()
    session.pop('random_ids', None)
    return user_dashboard()

# Search users route with pagination and efficient GET/POST handling
@app.route('/search/<username>', methods=['GET', 'POST'])
def search_users_view(username):
    """Render search results for users."""
    session.pop('random_ids', None)
    validate_user()  # Ensure user is authenticated

    search_results, page, total_pages, query = search_users_logic()

    # Render the search results page
    return render_template('search.html', search_results=search_results, page=page, total_pages=total_pages, query=query)

# Follow user route
@app.route('/follow_user/<username>/<int:user_id>', methods=['POST'])
def follow_user_route(username, user_id):
    """Handle follow user action."""
    return follow_user(user_id)

# Unfollow user route
@app.route('/unfollow_user/<username>/<int:user_id>', methods=['POST'])
def unfollow_user_route(username, user_id):
    """Handle unfollow user action."""
    return unfollow_user(user_id)

# Messaging routes
@app.route('/messages/<username>', methods=['GET', 'POST'])
def messages_route(username):
    """Render messages view for the user."""
    session.pop('random_ids', None)
    validate_user()
    return messages_view()

@app.route('/chat_room/<username>/<int:user_id>', methods=['GET', 'POST'])
def chat_room_route(username, user_id):
    """Render chat room for messaging."""
    validate_user()
    return chat_room(user_id, session.get('user_id'), session['username'])

# Posts and content routes
@app.route('/posts/<username>/', methods=['GET'])
def posts_view(username):
    """Load paginated posts for the user."""
    validate_user()
    return load_paginated_posts()

@app.route('/post_content/<username>', methods=['GET', 'POST'])
def post_content_view(username):
    """Handle posting content for the user."""
    session.pop('random_ids', None)
    validate_user()
    return post_content()

# Like post route
@app.route('/like_post/<int:post_id>', methods=['POST'])
def like_post_view(post_id):
    """Handle liking a post."""
    return like_post(post_id)

# Delete post route
@app.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post_view(post_id):
    """Handle deleting a post."""
    return delete_post(post_id)

# SocketIO events for chat functionality
@socketio.on('join')
def on_join(data):
    """Handle user joining a chat room."""
    username = session.get('username')
    room = data.get('room')

    if not room or not username:
        return

    session['room'] = room
    join_room(room)

@socketio.on('message')
def handle_message(data):
    """Handle incoming chat messages and store them in the database."""
    msg = data.get('msg')
    user_id = data.get('user_id')
    room = data.get('room')

    if msg and user_id and room:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Emit message to the room
        emit('message', {'msg': msg, 'user': session.get('username')}, room=room)

        # Insert the message into the database
        cursor.execute("""INSERT INTO messages (sender_id, receiver_id, message, timestamp) VALUES (%s, %s, %s, %s)""",
                       (session.get('user_id'), user_id, msg, datetime.datetime.now()))
        conn.commit()

        cursor.close()
        conn.close()

@socketio.on('leave')
def on_leave(data):
    """Handle user leaving a chat room."""
    username = session.get('username')
    room = session.get('room')
    leave_room(room)
    emit('message', {'msg': f'{username} has left the room.'}, room=room)

@app.route('/comment/<int:post_id>', methods=['POST', 'GET'])
def comment_page_view(post_id):
    """Handle loading and posting comments on a post."""
    return comment_page(post_id)

# User logout route
@app.route('/logout')
def logout():
    """Handle user logout."""
    return log_out()

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
