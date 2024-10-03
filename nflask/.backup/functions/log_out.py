from flask import session, make_response, flash, redirect, url_for
def log_out():
    session.pop('username', None)
    make_resp = make_response(redirect(url_for('index')))
    make_resp.set_cookie('logged_in', '', expires=0)
    flash('You have been logged out!', 'info')
    return make_resp
