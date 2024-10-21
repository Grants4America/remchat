from flask import session
from flask_socketio import emit
from functions.get_db_connection import get_db_connection

def unfollow_user(data):
    user_id = data.get('user_id')  # User to be followed
    current_user = session.get('username')  # Current user

    

    try:
        conn = get_db_connection()  # Get the database connection
        cursor = conn.cursor()

        # Validate that the current user exists
        cursor.execute("SELECT id FROM users WHERE username = %s", (current_user,))
        current_user_id = cursor.fetchone()[0]

        print("i am here...")
        print("current user username: " + current_user)
        print("current user id: " + str(current_user_id))
        print("user id to be followed: " + str(user_id))

        if not current_user_id:
            emit('follow_response', {'message': 'Current user not found!', 'status': 'warning'})
            return

        # Validate that the user to be followed exists
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        followed_user_id = cursor.fetchone()

        if not followed_user_id:
            emit('follow_response', {'message': 'User to follow not found!', 'status': 'warning'})
            return

        # Proceed with the follow logic if both users are valid
        cursor.execute(
            "SELECT COUNT(*) FROM followers WHERE user_id = %s AND followed_user_id = %s",
            (current_user_id, user_id)
        )

        if cursor.fetchone()[0] == 1:
            # Remove the follow relationship
            cursor.execute("DELETE FROM followers WHERE user_id = %s AND followed_user_id = %s",
                           (current_user_id, user_id))

            # Update the followers count for the unfollowed user
            cursor.execute(
                "UPDATE users SET followers_count = followers_count - 1 WHERE id = %s",
                (user_id,)
            )

            # Update the following count for the current user
            cursor.execute(
                "UPDATE users SET following_count = following_count - 1 WHERE id = %s",
                (current_user_id,)
            )
            conn.commit()
            emit('follow_response', {'message': 'User unfollowed successfully!', 'status': 'success'})
        else:
            emit('follow_response', {'message': 'You are no following this user!', 'status': 'warning'})

    except Exception as e:
        emit('follow_response', {'message': f'An error occurred: {str(e)}', 'status': 'danger'})

