from flask import request, redirect, url_for, flash
from functions.get_db_connection import get_db_connection
from bcrypt import hashpw, gensalt


def check_names(name):
    # Split the name by spaces to check if there are multiple names
    names = name.split()
    
    # Check if there is more than one name
    if len(names) < 2:
        return False
    
    # Check if each name starts with a capital letter
    for n in names:
        if not n[0].isupper():
            return False
    
    return True

def check_password(password):
    # Check if the password is longer than 6 characters
    if len(password) <= 6:
        return False
    
    # Check if the password contains at least one number
    if not any(char.isdigit() for char in password):
        return False
    
    return True

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
    
    # Validate the name format
    if not check_names(name):
        flash('Name must be in the format "First Last".', 'danger')
        return redirect(url_for('signup'))
    
    # Validate the password format
    if not check_password(password):
        flash('Password must be at least 7 characters long and contain at least one number.', 'danger')
        return redirect(url_for('signup'))
    try:
        # Check if the username, email, or name already exists in the database
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
