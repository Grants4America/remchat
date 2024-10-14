from flask import request, redirect, url_for, flash
from functions.get_db_connection import get_db_connection
from bcrypt import hashpw, gensalt

def signup_user():
    """
    Handles user registration by collecting user details from the signup form,
    checking for existing name, username, or email, and storing the new user in the database.

    Returns:
        Response: Redirects to the index page upon successful registration or
                  back to the signup page in case of errors.
    """
    name, username, email, password = (request.form[key] for key in ('name', 'username', 'email', 'password'))
    conn = get_db_connection()

    if not conn:
        flash('Database connection error!', 'danger')
        return redirect(url_for('signup'))

    try:
        cursor = conn.cursor()

        # Check if the name, username, or email already exists
        cursor.execute(
            "SELECT * FROM users WHERE username = %s OR email = %s OR name = %s", 
            (username, email, name)
        )
        existing_user = cursor.fetchone()
        if existing_user:
            if existing_user[2] == username:
                flash('Username already exists! 😞', 'danger')
            elif existing_user[4] == email:
                flash('Email already exists! 😞', 'danger')
            return redirect(url_for('signup'))

        # Hash the password before storing it
        hashed_password = hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')
        
        # Insert the new user into the database
        cursor.execute(
            "INSERT INTO users (name, username, email, password) VALUES (%s, %s, %s, %s)",
            (name, username, email, hashed_password)
        )
        conn.commit()
        flash('Registration successful! 🎉', 'success')

    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')

    finally:
        conn.close()

    return redirect(url_for('index'))
