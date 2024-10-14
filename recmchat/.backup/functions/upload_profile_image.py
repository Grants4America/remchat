from flask import request, flash, render_template, redirect, url_for, session
from functions.get_db_connection import get_db_connection
from functions.compress_img import compress_img
import base64

def upload_profile_image():
    image = request.files.get('image')
    
    conn = get_db_connection()
    cursor = conn.cursor() if conn else None
    if image:
        byte_data = compress_img(image)
        
        if byte_data:
            encoded_img = base64.b64encode(byte_data)

            cursor.execute("UPDATE users SET profile_picture = %s WHERE username = %s", (encoded_img, session['username']))
            conn.commit()

            cursor.execute("SELECT profile_picture FROM users WHERE username = %s", (session['username'],))
            photos = cursor.fetchone()
            photo = photos[0] if photos else None
            
            if photo:
                flash('Image uploaded successfully!', 'success')
                return redirect(url_for('dashboard', img=photo, username=session['username']))
            
    flash('Failed to upload image! 😞', 'danger')
    return redirect(url_for('dashboard', username=session['username']))
