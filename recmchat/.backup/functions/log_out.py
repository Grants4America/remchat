from flask import session, make_response, flash, redirect, url_for
from functions.get_db_connection import get_db_connection

def log_out():
    conn = get_db_connection()
    session.pop('username', None)
    make_resp = make_response(redirect(url_for('index')))
    make_resp.set_cookie('logged_in', '', expires=0)
    flash('You have been logged out!', 'info')
    conn.close()
    return make_resp
