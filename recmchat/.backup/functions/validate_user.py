from flask import flash, redirect, url_for, session
from functions.get_db_connection import get_db_connection
from functions.log_out import log_out
def validate_user():
    conn = get_db_connection()

    if not conn:
        flash('Database connection error!', 'danger')
        return redirect(url_for('dashboard', username=session.get('username')))
    try:
        current_user = session['username']
        cursor = conn.cursor()
        # Get the current user ID
        cursor.execute("SELECT id FROM users WHERE username = %s", (current_user,))
        current_user_id = cursor.fetchone()
        if not current_user_id:
            log_out()
            flash('Current user not found!', 'warning')
            return redirect(url_for('index'))
    finally:
        conn.close()
