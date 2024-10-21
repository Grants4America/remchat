from flask import flash, redirect, url_for, session
from functions.get_db_connection import get_db_connection
from functions.log_out import log_out

def validate_user():
    """
    Validates the current logged-in user by checking their existence in the database.

    This function retrieves the current user's ID based on the username stored in the session.
    If the user is not found, it logs them out and redirects to the index page.

    Returns:
        Response: Redirects to the index page if the user is not found; 
                  otherwise, continues without any response.
    """
    conn = get_db_connection()
    if not conn:
        flash('Database connection error!', 'danger')
        return redirect(url_for('dashboard', username=session.get('username')))

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = %s", (session['username'],))
        if not cursor.fetchone():
            log_out()  # Log out the user if not found
            flash('Current user not found!', 'warning')
            return redirect(url_for('index'))

    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')  # Handle any exceptions
        return redirect(url_for('index'))
    
    finally:
        cursor.close()  # Ensure the cursor is closed
        conn.close()    # Ensure the connection is closed
