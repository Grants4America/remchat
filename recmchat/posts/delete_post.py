from flask import flash, session, url_for, redirect
from functions.get_db_connection import get_db_connection

def delete_post(post_id):
    """
    Deletes a post from the database.

    Args:
        post_id (int): The ID of the post to be deleted.

    Returns:
        Response: Redirects to the posts view with a flash message indicating success or error.
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Execute the delete query
                cursor.execute("DELETE FROM posts WHERE id = %s", (post_id,))
                conn.commit()  # Commit the transaction

                # Flash a success message
                flash("Post deleted successfully", "info")
    except Exception as e:
        # Flash an error message if the operation fails
        flash(f'An error occurred while deleting the post: {str(e)}', 'danger')
    
    # Redirect to the posts view
    return redirect(url_for('posts_view', username=session['username']))
