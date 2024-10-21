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
from functions.get_db_connection import get_db_connection
from functions.login_required import login_required

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
socketio = SocketIO(app, manage_session=False)

conn = get_db_connection()
cursor = conn.cursor()

# Index route (login page)
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    """Render login page or redirect to dashboard if user is already logged in."""
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
@login_required
def dashboard(username):
    """Render user dashboard."""
    session.pop('random_ids', None)
    return user_dashboard()

# Search users route with pagination and efficient GET/POST handling
@app.route('/search/<username>', methods=['GET', 'POST'])
@login_required
def search_users_view(username):
    """Render search results for users."""
    session.pop('random_ids', None)
    search_results, page, total_pages, query = search_users_logic()
    # Render the search results page
    return render_template('search.html', search_results=search_results, page=page, total_pages=total_pages, query=query)

@socketio.on('follow')
def on_follow(data):
   follow_user(data)

@socketio.on('unfollow')
def on_unfollow(data):
    unfollow_user(data)
    


@app.route('/messages/<username>', methods=['GET', 'POST'])
@login_required
def messages_route(username):
    """Render messages view for the user."""
    session.pop('random_ids', None)
    return messages_view()

@app.route('/chat_room/<username>/<int:user_id>', methods=['GET', 'POST'])
@login_required
def chat_room_route(username, user_id):
    """Render chat room for messaging."""
    return chat_room(user_id, session.get('user_id'), session['username'])

@app.route('/posts/<username>/', methods=['GET'])
@login_required
def posts_view(username):
    return load_paginated_posts()

@app.route('/post_content/<username>', methods=['GET', 'POST'])
@login_required
def post_content_view(username):
    """Handle posting content for the user."""
    session.pop('random_ids', None)
    return post_content()


@socketio.on('like_post')
def on_like(data):
    like_post(data)
    

# Delete post route
@app.route('/delete_post/<int:post_id>', methods=['POST'])
@login_required
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
    # emit('message', {'msg': f'{username} has joined the room.'}, room=room)

@socketio.on('message')
def handle_message(data):
    """Handle incoming chat messages and store them in the database."""
    msg = data.get('msg')
    user_id = data.get('user_id')
    room = data.get('room')

    if not (msg and user_id and room):
        return  # Validate data

    try:
        # Emit message to the room
        username = session.get('username')
        emit('message', {'msg': msg, 'user': username}, room=room)

        # Insert the message into the database
        cursor.execute("""INSERT INTO messages (sender_id, receiver_id, message, timestamp) 
                          VALUES (%s, %s, %s, %s)""",
                       (session.get('user_id'), user_id, msg, datetime.datetime.now()))
        conn.commit()

    except Exception as e:
        print(f"Error handling message: {e}")
        conn.rollback()  # Rollback in case of error

    finally:
        cursor.close()
        conn.close()

@socketio.on('leave')
def on_leave(data):
    """Handle user leaving a chat room."""
    username = session.get('username')
    room = data.get('room') or session.get('room')

    if room and username:
        leave_room(room)
        emit('message', {'msg': f'{username} has left the room.'}, room=room)


@app.route('/comment/<int:post_id>', methods=['POST', 'GET'])
@login_required
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
