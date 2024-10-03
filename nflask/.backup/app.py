#!/usr/bin/python3
from flask import Flask, render_template, request, url_for, redirect, session, flash
from functions.login_user import login_user
from functions.user_dashboard import user_dashboard, search_users_logic, follow_user, unfollow_user
from functions.signup_user import signup_user
from functions.log_out import log_out

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'username' in session:
        flash('You are already logged in!', 'warning')
        return redirect(url_for('dashboard', username=session['username']))

    if request.method == 'POST':
         return login_user()
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        return signup_user()
    return render_template('signup.html')

@app.route("/dashboard/<username>", methods=['GET', 'POST'])
def dashboard(username):
    return user_dashboard()

@app.route('/search', methods=['GET', 'POST'])
def search_users_view():
    if request.method == 'POST':
        return search_users_logic()  # Call the logic directly

    # Handle GET requests or render the search form
    return render_template('search.html')

@app.route('/follow_user/<int:user_id>', methods=['POST'])
def follow_user_route(user_id):
    return follow_user(user_id)

@app.route('/unfollow_user/<int:user_id>', methods=['POST'])
def unfollow_user_route(user_id):
    return unfollow_user(user_id)

@app.route('/logout')
def logout():
    return log_out()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
