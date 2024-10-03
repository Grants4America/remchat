from flask import render_template, request, flash, redirect, url_for, session
from functions.get_db_connection import get_db_connection

def search_users_logic():
    query = request.form.get('search_query', '').strip()
    conn = get_db_connection()

    if not conn:
        flash('Database connection error!', 'danger')
        return redirect(url_for('dashboard', username=session.get('username')))

    try:
        cursor = conn.cursor()
        current_user_id = session['user_id']
        cursor.execute("SELECT id, name FROM users WHERE name LIKE %s AND id != %s", ('%' + query + '%', current_user_id))
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
        if not search_results:
            flash('No user found! 😒', 'info')

    finally:
        conn.close()

    return render_template('search.html', search_results=search_results)
