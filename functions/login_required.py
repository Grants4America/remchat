from functools import wraps
from flask import redirect, url_for, session, flash, request
from functions.log_out import log_out

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logged_in = request.cookies.get('logged_in')
        if 'username' not in session and not logged_in:
            log_out()
            flash('You need to be logged in to access this page.', 'warning')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function