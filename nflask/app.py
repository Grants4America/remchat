#!/usr/bin/python3
from flask import Flask, render_template, request, url_for, redirect, session, flash
from functions.login_user import login_user
from functions.user_dashboard import user_dashboard
from functions.follow_user import follow_user
from functions.unfollow_user import unfollow_user
from functions.search_users_logic import search_users_logic
from functions.signup_user import signup_user
from functions.log_out import log_out
from functions.validate_user import validate_user

from chats.messages import messages as messages_view  # Avoid function name conflict
from chats.chat_room import chat_room

from posts.posts import posts, like_post, load_paginated_posts
from posts.post_content import post_content
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    if 'username' in session:
        flash('You are already logged in!', 'warning')
        validate_user()
        return redirect(url_for('dashboard', username=session['username']))

    if request.method == 'POST':
         return login_user()
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        validate_user()
        return signup_user()
    validate_user()
    return render_template('signup.html')

@app.route("/dashboard/<username>", methods=['GET', 'POST'])
def dashboard(username):
    validate_user()
    return user_dashboard()

@app.route('/search/<username>', methods=['GET', 'POST'])
def search_users_view(username):
    if request.method == 'POST':
        validate_user()
        return search_users_logic()  # Call the logic directly

    # Handle GET requests or render the search form
    validate_user()
    return render_template('search.html')

@app.route('/follow_user/<username>/<int:user_id>', methods=['POST'])
def follow_user_route(username, user_id):
    validate_user()
    return follow_user(user_id)

@app.route('/unfollow_user/<username>/<int:user_id>', methods=['POST'])
def unfollow_user_route(username, user_id):
    validate_user()
    return unfollow_user(user_id)

@app.route('/messages/<username>', methods=['GET', 'POST'])
def messages_route(username):
    validate_user()
    return messages_view()

@app.route('/chat_room/<username>/<int:user_id>', methods=['GET', 'POST'])
def chat_room_route(username, user_id):
    current_user_id = session.get('user_id')
    validate_user()
    return chat_room(user_id, current_user_id)

@app.route('/posts/<username>/', methods=['GET'])
def posts_view(username):
    page = request.args.get('page', 1, type=int)
    validate_user()
    return load_paginated_posts(page)

@app.route('/post_content/<username>', methods=['GET', 'POST'])
def post_content_view(username):
    validate_user()
    return post_content()

@app.route('/like_post/<int:post_id>', methods=['POST'])
def like_post_view(post_id):
    validate_user()
    return like_post(post_id)



@app.route('/logout')
def logout():
    return log_out()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
