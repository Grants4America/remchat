from flask import request, url_for, redirect, session, make_response, flash
from functions.get_db_connection import get_db_connection
from bcrypt import checkpw


def login_user():
    username = request.form['username']
    password = request.form['password']

    conn = get_db_connection()
    cursor = conn.cursor() if conn else None

    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    if user and checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
        name = user[1]
        user_id = user[0]
        session['username'] = username
        session['name'] = name
        session['user_id'] = user_id
        make_resp = make_response(redirect(url_for('dashboard', username=session['username'])))
        make_resp.set_cookie('logged_in', 'true', max_age=60*60*24)
        return make_resp
    else:
        flash('Invalid username or password! 😒', 'danger')
        return redirect(url_for('index'))
