from flask import flash, redirect, url_for, session
from functions.get_db_connection import get_db_connection

def unfollow_user(user_id):
    """
    Handles the unfollowing of a user by the current user.

    This function checks if the current user is following the specified user.
    If so, it removes the relationship from the followers table and updates
    the follower and following counts for both users.

    Args:
        user_id (int): The ID of the user to be unfollowed.

    Returns:
        Response: Redirects to the search users view upon successful unfollowing
                  or to the dashboard in case of errors.
    """
    current_user = session.get('username')
    conn = get_db_connection()

    if not conn:
        flash('Database connection error!', 'danger')
        return redirect(url_for('dashboard', username=current_user))

    try:
        cursor = conn.cursor()

        # Fetch the current user's ID
        cursor.execute("SELECT id FROM users WHERE username = %s", (current_user,))
        current_user_id = cursor.fetchone()

        if not current_user_id:
            flash('Current user not found!', 'warning')
            return redirect(url_for('index'))

        # Check if the current user is following the specified user
        cursor.execute("SELECT COUNT(*) FROM followers WHERE user_id = %s AND followed_user_id = %s",
                       (current_user_id[0], user_id))
        if cursor.fetchone()[0] == 0:
            flash('You are not following this user!', 'warning')
        else:
            # Remove the follow relationship
            cursor.execute("DELETE FROM followers WHERE user_id = %s AND followed_user_id = %s",
                           (current_user_id[0], user_id))
            # Update follower and following counts
            cursor.execute(
                "UPDATE users SET followers_count = followers_count - 1 WHERE id = %s; "
                "UPDATE users SET following_count = following_count - 1 WHERE id = %s;",
                (user_id, current_user_id[0])
            )
            conn.commit()
            flash('User unfollowed successfully!', 'success')

        return redirect(url_for('search_users_view', username=current_user))

    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('dashboard', username=current_user))
    finally:
        conn.close()
