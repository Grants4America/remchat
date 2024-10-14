from flask import request, render_template, flash, session, url_for, redirect, session
from functions.get_db_connection import get_db_connection
import random

def posts():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = "SELECT * FROM posts ORDER BY RAND() LIMIT 10"
        cursor.execute(query)
        post_contents = cursor.fetchall()

        process_posts = []

        for post in post_contents:
            process_posts.append(list(post))

        for i, post in enumerate(process_posts):
            encoded_img = post[3]
            decoded_img = encoded_img.decode('utf-8') if encoded_img else None
            process_posts[i][3] = decoded_img

        return render_template('posts.html', posts=process_posts)

    except Exception as e:
        flash(f'An error occurred while fetching posts: {e}', 'danger')
        return render_template('posts.html', posts=[])

    finally:
        cursor.close()
        conn.close()

def load_paginated_posts(page):
    conn = get_db_connection()
    cursor = conn.cursor()
    offset = (page - 1) * 10
    try:
        # Fetch 10 random posts with an offset
        query = "SELECT * FROM posts ORDER BY RAND() LIMIT 10 OFFSET %s"
        cursor.execute(query, [offset])
        post_contents = cursor.fetchall()
        
        process_posts = []

        current_user_id = session['user_id']

        # Fetch all post_ids to display
        post_ids = [post[0] for post in post_contents]
        
        if post_ids:
            # Prepare the placeholders for the IN clause
            placeholders = ','.join(['%s'] * len(post_ids))
            query = f"SELECT post_id FROM likes WHERE user_id = %s AND post_id IN ({placeholders})"
            cursor.execute(query, [current_user_id] + post_ids)
            liked_posts = [row[0] for row in cursor.fetchall()]  # List of post_ids liked by the current user
        else:
            liked_posts = []

        for post in post_contents:
            process_post = list(post)
            encoded_img = process_post[3]
            decoded_img = encoded_img.decode('utf-8') if encoded_img else None
            process_post[3] = decoded_img
            
            # Add whether the current user liked this post
            process_post.append({
                'is_liked_by_current_user': post[0] in liked_posts  # Check if the post_id is in liked_posts
            })
            process_posts.append(process_post)

        if not post_contents:
            flash('No posts yet!', 'info')
            return render_template('posts.html', posts=process_posts)

        return render_template('posts.html', posts=process_posts)

    except Exception as e:
        flash(f'An error occurred while loading posts: {str(e)}', 'danger')
        return render_template('posts.html', posts=[])

    finally:
        cursor.close()
        conn.close()



def like_post(post_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    user_id = session['user_id']
    try:
        cursor.execute("SELECT * FROM likes WHERE post_id = %s AND user_id = %s", (post_id, user_id))
        like = cursor.fetchone()

        cursor.execute("SELECT likes FROM posts WHERE id = %s", (post_id,))
        likes = cursor.fetchone()[0]

        if like:
            if likes > 0:
                likes -= 1
                cursor.execute("UPDATE posts SET likes = %s WHERE id = %s", (likes, post_id))
                cursor.execute("DELETE FROM likes WHERE post_id = %s AND user_id = %s", (post_id, user_id))
                conn.commit()
                flash('You unliked the post!', 'info')
            else:
                flash('Cannot unlike a post with 0 likes!', 'warning')
        else:
            likes += 1
            cursor.execute("UPDATE posts SET likes = %s WHERE id = %s", (likes, post_id))
            cursor.execute("INSERT INTO likes (post_id, user_id) VALUES (%s, %s)", (post_id, user_id))
            conn.commit()
            flash('You liked the post!', 'success')

        return redirect(url_for('posts_view', username=session['username']))

    except Exception as e:
        flash('An error occurred while liking the post.', 'danger')
        return redirect(url_for('posts_view', username=session['username']))

    finally:
        cursor.close()
        conn.close()
