from flask import request, redirect, url_for, flash
from functions.get_db_connection import get_db_connection
from bcrypt import hashpw, gensalt


def signup_user():
    name = request.form['name']
    username = request.form['username']
    password = request.form['password']

    conn = get_db_connection()
    cursor = conn.cursor() if conn else None

    hashed_password = hashpw(password.encode('utf-8'), gensalt())

    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user_exists = cursor.fetchone()

    if user_exists:
        flash('Username already exists! 😞', 'danger')
        return redirect(url_for('signup'))

    cursor.execute("INSERT INTO users (name, username, password) VALUES (%s, %s, %s)", (name, username, hashed_password.decode('utf-8')))
    conn.commit()
    flash('Registration successful! 🎉', 'success')
    return redirect(url_for('index'))
