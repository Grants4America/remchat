from flask import session, request, flash, redirect, url_for, render_template
from functions.get_db_connection import get_db_connection
import datetime

def chat_room(user_id, current_user_id):
    conn = get_db_connection()

    if not conn:
        flash('Database connection error!', 'danger')
        return redirect(url_for('dashboard', username=session.get('username')))

    try:
        cursor = conn.cursor()

        # Handle POST request to send a message
        if request.method == 'POST':
            message = request.form.get('message')
            if message:
                insert_query = """
                    INSERT INTO messages (sender_id, receiver_id, message, timestamp)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(insert_query, (current_user_id, user_id, message, datetime.datetime.now()))
                conn.commit()
                flash('Message sent!', 'success')
            else:
                flash('Message cannot be empty!', 'danger')

        # Fetch chat history between the two users
        query = """
            SELECT sender_id, receiver_id, message, timestamp
            FROM messages
            WHERE (sender_id = %s AND receiver_id = %s)
            OR (sender_id = %s AND receiver_id = %s)
            ORDER BY timestamp ASC
        """
        cursor.execute(query, (current_user_id, user_id, user_id, current_user_id))
        chat_history = cursor.fetchall()

        # Enhance chat_history with usernames or "You" for the current user
        enhanced_chat_history = []
        for chat in chat_history:
            sender_id = chat[0]
            # If the current user sent the message, use "You", otherwise get the sender's username
            if sender_id == current_user_id:
                sender_name = "You"
            else:
                cursor.execute("SELECT username FROM users WHERE id = %s", (sender_id,))
                sender_name = cursor.fetchone()[0]  # Get the sender's username

            enhanced_chat_history.append({
                'sender_name': sender_name,
                'message': chat[2],
                'timestamp': chat[3]
            })

        return render_template('chat_room.html', chat_history=enhanced_chat_history, user_id=user_id)
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('dashboard', username=session.get('username')))
    finally:
        cursor.close()
        conn.close()
