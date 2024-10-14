from flask import request, flash, redirect, url_for, session
from functions.get_db_connection import get_db_connection
from functions.compress_img import compress_img
import base64

def upload_profile_image():
    """
    Handles the uploading of a user's profile image.

    This function checks for an uploaded image, compresses it, encodes it in
    Base64, and updates the user's profile picture in the database. If the
    image is successfully uploaded, it redirects the user back to the dashboard.

    Returns:
        Response: Redirects to the dashboard with a success or error flash message.
    """
    image = request.files.get('image')
    conn = get_db_connection()

    if not conn:
        flash('Database connection error!', 'danger')
        return redirect(url_for('dashboard', username=session['username']))

    if image:
        byte_data = compress_img(image)

        if byte_data:
            encoded_img = base64.b64encode(byte_data).decode('utf-8')
            cursor = conn.cursor()

            try:
                # Update the user's profile picture in the database
                cursor.execute("UPDATE users SET profile_picture = %s WHERE username = %s",
                               (encoded_img, session['username']))
                conn.commit()

                # Fetch the updated profile picture
                cursor.execute("SELECT profile_picture FROM users WHERE username = %s", (session['username'],))
                result = cursor.fetchone()  # Fetch only once

                photo = result[0] if result else None  # Check if result is not None

                if photo:
                    flash('Image uploaded successfully!', 'success')
                    return redirect(url_for('dashboard', img=photo, username=session['username']))

            except Exception as e:
                flash(f'An error occurred while updating the image: {str(e)}', 'danger')
                return redirect(url_for('dashboard', username=session['username']))
            finally:
                cursor.close()
                conn.close()

    flash('Failed to upload image! 😞', 'danger')
    return redirect(url_for('dashboard', username=session['username']))

