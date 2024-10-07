from flask import session, request, flash, redirect, url_for, render_template
from functions.get_db_connection import get_db_connection

def messages():
    conn = get_db_connection()

    if not conn:
        flash('Database connection error!', 'danger')
        return redirect(url_for('dashboard', username=session.get('username')))

    try:
        cursor = conn.cursor()

        if request.method == 'POST':
            search_query = request.form.get('search_query')
            current_user_id = session['user_id']  # Assuming current user ID is stored in session
            search_sql = """
            SELECT id, username
            FROM users
            WHERE username LIKE %s
            AND id != %s
            """
            cursor.execute(search_sql, ('%' + search_query + '%', current_user_id))

            users = cursor.fetchall()
            if not users:
                flash('No user found! 😒', 'info')

            return render_template('messages.html', users=users)
        else:
            # Load previous chat users with their usernames
            user_id = session.get('user_id')
            query = """
                SELECT DISTINCT u.id, u.username
                FROM messages m
                JOIN users u ON (u.id = m.sender_id AND m.receiver_id = %s)
                               OR (u.id = m.receiver_id AND m.sender_id = %s)
            """
            cursor.execute(query, (user_id, user_id))
            previous_users = cursor.fetchall()


            return render_template('messages.html', previous_users=previous_users)
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('dashboard', username=session.get('username')))
    finally:
        cursor.close()
        conn.close()
