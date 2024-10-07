from flask import flash, redirect, url_for, session
from functions.get_db_connection import get_db_connection

def unfollow_user(user_id):
    current_user = session.get('username')
    conn = get_db_connection()

    if not conn:
        flash('Database connection error!', 'danger')
        return redirect(url_for('dashboard', username=current_user))

    try:
        cursor = conn.cursor()

        # Get the current user ID
        cursor.execute("SELECT id FROM users WHERE username = %s", (current_user,))
        current_user_id = cursor.fetchone()

        if not current_user_id:
            flash('Current user not found!', 'warning')
            return redirect(url_for('index'))

        # Check if the follow relationship exists before attempting to delete
        cursor.execute("SELECT COUNT(*) FROM followers WHERE user_id = %s AND followed_user_id = %s", (current_user_id[0], user_id))
        count = cursor.fetchone()[0]

        if count == 0:
            flash('You are not following this user!', 'warning')
        else:
            # Delete follow relationship
            cursor.execute("DELETE FROM followers WHERE user_id = %s AND followed_user_id = %s", (current_user_id[0], user_id))

            # Update followers count for the unfollowed user
            cursor.execute("UPDATE users SET followers_count = followers_count - 1 WHERE id = %s", (user_id,))
            # Update following count for the current user
            cursor.execute("UPDATE users SET following_count = following_count - 1 WHERE id = %s", (current_user_id[0],))

            conn.commit()
            flash('User unfollowed successfully!', 'success')

        return redirect(url_for('dashboard', username=current_user))

    finally:
        conn.close()

