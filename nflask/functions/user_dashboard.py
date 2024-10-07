from flask import session, request, flash, redirect, url_for, render_template
from functions.get_db_connection import get_db_connection
from functions.upload_profile_image import upload_profile_image

def user_dashboard():
    username = session.get('username')
    logged_in = request.cookies.get('logged_in')

    if not username or not logged_in:
        flash('You are not logged in!', 'warning')
        return redirect(url_for('index'))

    conn = get_db_connection()
    if not conn:
        flash('Database connection error!', 'danger')
        return redirect(url_for('index'))
    
    try:
        cursor = conn.cursor()

        if request.method == 'POST':
            upload_profile_image()

        # Fetch user details
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        details = cursor.fetchone()

        if not details:
            flash('User not found!', 'warning')
            return redirect(url_for('index'))

        photo = details[5]  # Assuming the photo is at index 5
        if photo:
            photo = photo.decode('utf-8')
        else:
            photo = None
        return render_template('dashboard.html', img=photo if photo else None, details=details)

    finally:
        conn.close()
