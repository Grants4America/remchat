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
        print(str(details[6]) + "    " + str(details[7]))
        return render_template('dashboard.html', img=photo.decode('utf-8') if photo else None, details=details)

    finally:
        conn.close()

def search_users_logic():
    query = request.form.get('search_query', '').strip()
    conn = get_db_connection()

    if not conn:
        flash('Database connection error!', 'danger')
        return redirect(url_for('dashboard', username=session.get('username')))

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM users WHERE name LIKE %s", ('%' + query + '%',))
        results = cursor.fetchall()

        # Get the current user's following list
        current_user = session.get('username')
        cursor.execute("SELECT followed_user_id FROM followers WHERE user_id = (SELECT id FROM users WHERE username = %s)", (current_user,))
        following_list = [row[0] for row in cursor.fetchall()]

        # Prepare the search results
        search_results = []
        for user in results:
            search_results.append({
                'id': user[0],
                'name': user[1],
                'is_following': user[0] in following_list
            })

    finally:
        conn.close()

    return render_template('search.html', search_results=search_results)


def follow_user(user_id):
    current_user = session.get('username')
    conn = get_db_connection()

    if not conn:
        flash('Database connection error!', 'danger')
        return redirect(url_for('dashboard', username=current_user))

    try:
        cursor = conn.cursor()

        # Get the current user ID
        cursor.execute("SELECT id FROM users WHERE username = %s", (current_user,))
        current_user_id = cursor.fetchone()

        if not current_user_id:
            flash('Current user not found!', 'warning')
            return redirect(url_for('index'))

        # Check if the user is trying to follow themselves
        if current_user_id[0] == user_id:
            flash('You cannot follow yourself!', 'warning')
            return redirect(url_for('dashboard', username=current_user))

        # Check if the follow relationship already exists
        cursor.execute("SELECT COUNT(*) FROM followers WHERE user_id = %s AND followed_user_id = %s", (current_user_id[0], user_id))
        count = cursor.fetchone()[0]

        if count > 0:
            flash('You are already following this user!', 'warning')
        else:
            # Insert follow relationship
            cursor.execute("INSERT INTO followers (user_id, followed_user_id) VALUES (%s, %s)", (current_user_id[0], user_id))
            
            # Update followers count for the followed user
            cursor.execute("UPDATE users SET followers_count = followers_count + 1 WHERE id = %s", (user_id,))
            # Update following count for the current user
            cursor.execute("UPDATE users SET following_count = following_count + 1 WHERE id = %s", (current_user_id[0],))

            conn.commit()
            flash('User followed successfully!', 'success')

        return redirect(url_for('dashboard', username=current_user))

    finally:
        conn.close()


def unfollow_user(user_id):
    current_user = session.get('username')
    conn = get_db_connection()

    if not conn:
        flash('Database connection error!', 'danger')
        return redirect(url_for('dashboard', username=current_user))

    try:
        cursor = conn.cursor()

        # Get the current user ID
        cursor.execute("SELECT id FROM users WHERE username = %s", (current_user,))
        current_user_id = cursor.fetchone()

        if not current_user_id:
            flash('Current user not found!', 'warning')
            return redirect(url_for('index'))

        # Check if the follow relationship exists before attempting to delete
        cursor.execute("SELECT COUNT(*) FROM followers WHERE user_id = %s AND followed_user_id = %s", (current_user_id[0], user_id))
        count = cursor.fetchone()[0]

        if count == 0:
            flash('You are not following this user!', 'warning')
        else:
            # Delete follow relationship
            cursor.execute("DELETE FROM followers WHERE user_id = %s AND followed_user_id = %s", (current_user_id[0], user_id))

            # Update followers count for the unfollowed user
            cursor.execute("UPDATE users SET followers_count = followers_count - 1 WHERE id = %s", (user_id,))
            # Update following count for the current user
            cursor.execute("UPDATE users SET following_count = following_count - 1 WHERE id = %s", (current_user_id[0],))

            conn.commit()
            flash('User unfollowed successfully!', 'success')

        return redirect(url_for('dashboard', username=current_user))

    finally:
        conn.close()

