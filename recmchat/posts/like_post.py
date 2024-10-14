from flask import flash, session, url_for, redirect
from functions.get_db_connection import get_db_connection

def like_post(post_id):
    """
    Toggles the like status of a post for the current user.

    This function checks if the current user has liked the specified post. If they have,
    it unlikes the post; if they haven't, it likes the post. The like count is updated
    accordingly. Any errors encountered during the process are flashed as messages.

    Args:
        post_id (int): The ID of the post to like or unlike.

    Returns:
        Response: Redirects to the posts view.
    """
    user_id = session.get('user_id')

    if user_id is None:
        flash('You need to be logged in to like posts.', 'danger')
        return redirect(url_for('login'))

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            try:
                # Check if the user has already liked the post
                cursor.execute("SELECT * FROM likes WHERE post_id = %s AND user_id = %s", (post_id, user_id))
                like = cursor.fetchone()

                # Get the current like count for the post
                cursor.execute("SELECT likes FROM posts WHERE id = %s", (post_id,))
                likes = cursor.fetchone()[0]

                if like:  # User already liked the post
                    if likes > 0:
                        likes -= 1  # Decrement like count
                        cursor.execute("UPDATE posts SET likes = %s WHERE id = %s", (likes, post_id))
                        cursor.execute("DELETE FROM likes WHERE post_id = %s AND user_id = %s", (post_id, user_id))
                        flash('You unliked the post!', 'info')
                    else:
                        flash('Cannot unlike a post with 0 likes!', 'warning')
                else:  # User likes the post
                    likes += 1  # Increment like count
                    cursor.execute("UPDATE posts SET likes = %s WHERE id = %s", (likes, post_id))
                    cursor.execute("INSERT INTO likes (post_id, user_id) VALUES (%s, %s)", (post_id, user_id))
                    flash('You liked the post!', 'success')

                conn.commit()  # Commit the transaction
                return redirect(url_for('posts_view', username=session['username']))

            except Exception as e:
                flash(f'An error occurred while liking the post: {str(e)}', 'danger')
                return redirect(url_for('posts_view', username=session['username']))
