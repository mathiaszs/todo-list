import functools

import jwt
# import datatime # type: ignore

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        db = get_db()

        existing_user = db.execute(
            "SELECT id FROM user WHERE email = ?", (email, )
        ).fetchone()

        error = None

        if not username:
            error = "You must write an username"
        elif not email:
            error = "You must write an email"
        elif not password:
            error = "You must write a password"
        elif len(password) < 6:
            error = "Password must be at least 6 characters long"
        elif existing_user:
            error = "Email already registered"

        if error:
            flash(error)
            return render_template('auth/register.html')

        db.execute(
            "INSERT into user (username, email, password) VALUES (?, ?, ?)", 
            (username, email, generate_password_hash(password))
        )
        db.commit()  # Commit the changes to the database

        flash("User registered successfully!")
        return redirect(url_for("auth.login"))

    return render_template('auth/register.html')


@bp.route('/login', methods=("GET", "POST"))
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            "SELECT * FROM user WHERE email = ?", (email,)
        ).fetchone()

        if user is None:
            error = 'Incorrect email.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        
        flash(error)

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# Funcion that allows the user go to a page just if he is logged
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)

    return wrapped_view

