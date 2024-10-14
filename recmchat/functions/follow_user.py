from flask import flash, redirect, url_for, session
from functions.get_db_connection import get_db_connection

def follow_user(user_id):
    """
    Allows the current user to follow another user.

    This function checks if the current user can follow the specified user.
    If they are not already following the user, it adds a new entry in the 
    followers table and updates the followers and following counts.

    Args:
        user_id (int): The ID of the user to follow.

    Returns:
        Redirect: Redirects to the search users view or dashboard.
    """
    current_user = session.get('username')
    conn = get_db_connection()

    if not conn:
        flash('Database connection error!', 'danger')
        return redirect(url_for('dashboard', username=current_user))

    try:
        cursor = conn.cursor()

        # Get current user ID and validate
        cursor.execute("SELECT id FROM users WHERE username = %s", (current_user,))
        current_user_id = cursor.fetchone()

        if not current_user_id or current_user_id[0] == user_id:
            flash('Invalid action!', 'warning')
            return redirect(url_for('search_users_view', username=current_user))

        # Follow user if not already following
        cursor.execute(
            "SELECT COUNT(*) FROM followers WHERE user_id = %s AND followed_user_id = %s",
            (current_user_id[0], user_id)
        )
        
        if cursor.fetchone()[0] == 0:
            # Insert into followers and update follower/following counts
            cursor.execute(
                "INSERT INTO followers (user_id, followed_user_id) VALUES (%s, %s)",
                (current_user_id[0], user_id)
            )
            cursor.execute(
                "UPDATE users SET followers_count = followers_count + 1 WHERE id = %s",
                (user_id,)
            )
            cursor.execute(
                "UPDATE users SET following_count = following_count + 1 WHERE id = %s",
                (current_user_id[0],)
            )
            conn.commit()
            flash('User followed successfully!', 'success')
        else:
            flash('Already following this user!', 'warning')

        return redirect(url_for('search_users_view', username=current_user))

    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('dashboard', username=current_user))

    finally:
        cursor.close()
        conn.close()
