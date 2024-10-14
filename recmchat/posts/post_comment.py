from flask import request, flash, redirect, url_for, session, render_template
from functions.get_db_connection import get_db_connection

def comment_page(post_id):
    """
    Handles both loading and posting comments for a specific post.

    Args:
        post_id (int): The ID of the post.

    Returns:
        Response: Renders the post with comments or handles the POST request to add a new comment.
    """
    user_id = session.get('user_id')
    if not user_id:
        flash('You need to be logged in to comment.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Handle posting a comment
        comment_content = request.form.get('comment')

        if not comment_content:
            flash('Comment cannot be empty.', 'warning')
        else:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    try:
                        cursor.execute(
                            "INSERT INTO comments (post_id, user_id, content) VALUES (%s, %s, %s)",
                            (post_id, user_id, comment_content)
                        )
                        conn.commit()
                        flash('Comment posted successfully!', 'success')
                    except Exception as e:
                        flash(f'An error occurred while posting your comment: {e}', 'danger')

        return redirect(url_for('comment_page', post_id=post_id))

    # Handle loading comments (GET request)
    comments = load_comments(post_id)
    return render_template('post_comment.html', post_id=post_id, comments=comments)

def load_comments(post_id):
    """
    Loads comments for a specific post.

    Args:
        post_id (int): The ID of the post.

    Returns:
        list: List of comments for the specified post.
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT user_id, content, created_at FROM comments WHERE post_id = %s ORDER BY created_at ASC",
                (post_id,)
            )
            return cursor.fetchall()  # Returns a list of comments
