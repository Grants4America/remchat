from flask import request, render_template, flash, session, redirect, url_for
from functions.get_db_connection import get_db_connection
from functions.system_picture import system_picture

from flask import render_template, session, flash, request
from functions.get_db_connection import get_db_connection  # Adjust the import according to your project structure

def load_paginated_posts():
    """
    Loads posts for the specified page with pagination.

    Args:
        page (int): The page number to load.

    Returns:
        Response: Renders the posts page with either the fetched posts or an empty list.
    """
    # Get the page number from the request arguments, defaulting to 1
    page = request.args.get('page', 1, type=int)
    per_page = 10
    start = (page - 1) * per_page  # Calculate the offset for pagination
    end = start + per_page

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            try:
                if 'random_ids' not in session:
                    cursor.execute("SELECT id FROM posts ORDER BY RAND() LIMIT 1000")
                    random_ids = [row[0] for row in cursor.fetchall()]
                    session['random_ids'] = random_ids
                    session['total_posts'] = len(random_ids)
                
                random_ids = session['random_ids'][start:end]
                if not random_ids:
                    return render_template('posts.html', posts=[])  # Render an empty posts page

                format_string = ', '.join(['%s'] * len(random_ids))

                # Fetch posts with pagination
                query = f"SELECT id, user_id, content, picture, created_at, likes FROM posts WHERE id IN ({format_string})"
                cursor.execute(query, tuple(random_ids))
                post_contents = cursor.fetchall()  # Get the fetched posts

                # Retrieve the current user's ID from the session
                total_pages = (session['total_posts'] + per_page -1) // per_page
                current_user_id = session.get('user_id')  # Ensure session['user_id'] exists
                post_ids = [post[0] for post in post_contents]  # Collect post IDs for likes query
                
                # Prepare user IDs for fetching user details
                user_ids = [post[1] for post in post_contents]  # Get user_id from post_contents
                placeholders = ', '.join(['%s'] * len(user_ids))
                cursor.execute(f"SELECT id, name, profile_picture FROM users WHERE id IN ({placeholders})", tuple(user_ids))
                user_details = cursor.fetchall()  # Get user details

                # Extract user details for further processing
                creator_ids = [row[0] for row in user_details]
                creator_names = [row[1] for row in user_details]
                creator_pictures = [row[2] for row in user_details]

                liked_posts = []  # Initialize list to store liked post IDs
                if post_ids:
                    # Fetch liked post IDs in one query
                    placeholders = ','.join(['%s'] * len(post_ids))
                    query = f"SELECT post_id FROM likes WHERE user_id = %s AND post_id IN ({placeholders})"
                    cursor.execute(query, [current_user_id] + post_ids)
                    liked_posts = {row[0] for row in cursor.fetchall()}  # Set of liked post IDs

                processed_posts = []  # Initialize list for processed post data
                for post in post_contents:
                    post_id, user_id, content, picture, created_at, likes = post  # Unpack post data

                    if session['user_id'] == user_id:
                        is_my_post = True
                    else:
                        is_my_post = False

                    # Find creator name and picture based on user_id
                    i = 0
                    for _id in creator_ids:
                        if _id == user_id:
                            creator_name = creator_names[i]
                            creator_picture = creator_pictures[i]
                            break  # Exit the loop once the correct user is found
                        else:
                            i += 1

                    # Create a dictionary for the processed post data
                    processed_post = {
                        'id': post_id,
                        'user_id': user_id,
                        'content': content,
                        'picture': picture.decode('utf-8') if picture else None,
                        'created_at': created_at,
                        'likes': likes or 0,  # Default to 0 if None
                        'is_liked_by_current_user': post_id in liked_posts,
                        'creator_name': creator_name,
                        'creator_picture': creator_picture.decode('utf-8') if creator_picture else system_picture(),  # Assuming `system_picture` returns a default picture
                        'is_my_post': is_my_post
                    }
                    processed_posts.append(processed_post)  # Append processed post data

                # Check if there are no processed posts and flash a message if needed
                if not processed_posts:
                    flash('No posts yet!', 'info')

                return render_template('posts.html', posts=processed_posts, page=page, total_pages=total_pages)  # Render the posts template

            except Exception as e:
                flash(f'An error occurred while loading posts: {e}', 'danger')  # Handle any errors
                return redirect(url_for('dashboard', username=session.get('username')))