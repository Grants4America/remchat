from flask import session, request, flash, redirect, url_for, render_template
from functions.get_db_connection import get_db_connection

from chats.search_users import search_users
from chats.load_previous_users import load_previous_users

def messages():
    """
    Handles displaying messages and searching for users.

    Processes both GET and POST requests. On POST, it searches for users based on 
    the provided query and returns results. On GET, it fetches and displays previous chat users.

    Returns:
        Rendered HTML template for messages with user search results or chat history.
    """
    conn = get_db_connection()
    
    if not conn:
        flash('Database connection error!', 'danger')
        return redirect(url_for('dashboard', username=session.get('username')))
    
    user_id = session.get('user_id')
    if not user_id:
        flash('You need to be logged in to view messages.', 'danger')
        return redirect(url_for('login'))

    cursor = conn.cursor()
    current_user_id = user_id
    search_query = request.form.get('search_query', '').strip() if request.method == 'POST' else request.args.get('query', '').strip()
    
    try:
        users, page, total_pages = search_users(cursor, search_query, current_user_id)
        previous_users = load_previous_users(cursor, user_id)

        if not users and request.method == 'POST':
            flash('No user found! 😒', 'info')

        return render_template(
            'messages.html', 
            users=users, 
            previous_users=previous_users, 
            page=page, 
            total_pages=total_pages, 
            search_query=search_query
        )

    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('dashboard', username=session.get('username')))

    finally:
        cursor.close()  # Always close the cursor
        conn.close()    # Always close the database connection
