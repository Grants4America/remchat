from flask import session, request, flash, redirect, url_for, render_template
from functions.get_db_connection import get_db_connection
from functions.upload_profile_image import upload_profile_image
from functions.system_picture import system_picture

def user_dashboard():
    """
    Displays the user dashboard, allowing the user to upload a profile image
    and view their details.

    This function checks if the user is logged in, retrieves user details,
    and processes image uploads if provided.

    Returns:
        Response: Renders the dashboard template with user details and profile image.
    """
    username = session.get('username')
    logged_in = request.cookies.get('logged_in')

    # Check if the user is logged in
    if not username or not logged_in:
        flash('You are not logged in!', 'warning')
        return redirect(url_for('index'))

    conn = get_db_connection()
    if not conn:
        flash('Database connection error!', 'danger')
        return redirect(url_for('index'))
    
    try:
        cursor = conn.cursor()

        # Handle profile image upload
        if request.method == 'POST':
            upload_profile_image()

        # Fetch user details from the database
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        details = cursor.fetchone()

        if not details:
            flash('User not found!', 'warning')
            return redirect(url_for('index'))

        # Decode the profile picture if it exists
        photo = details[5].decode('utf-8') if details[5] else system_picture()
        return render_template('dashboard.html', img=photo, details=details)

    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('index'))

    finally:
        cursor.close()
        conn.close()