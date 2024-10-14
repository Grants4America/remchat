from flask import request, redirect, url_for, session, render_template
from functions.get_db_connection import get_db_connection
from functions.compress_img import compress_img
import base64

def post_content():
    if request.method == 'POST':
        content = request.form['content']
        image = request.files.get('image')
        user_id = session['user_id']

        if image:
            byte_data = compress_img(image)
            encoded_img = base64.b64encode(byte_data) if byte_data else None
        else:
            encoded_img = None

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            query = "INSERT INTO posts (user_id, content, picture) VALUES (%s, %s, %s)"
            cursor.execute(query, (user_id, content, encoded_img))
            conn.commit()
        except Exception as e:
            flash('An error occurred while creating the post.', 'danger')
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('posts_view', username=session['username']))

    return render_template('post_content.html')
