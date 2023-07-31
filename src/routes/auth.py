from src import app
from src.models import User
from src.forms import LoginForm
from flask import render_template, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from functools import wraps


@app.context_processor
def context_processor():
    user = None
    is_admin = False

    if "user_id" in session:
        user = User.query.get(session["user_id"])
        if user:
            is_admin = user.is_admin

    return {"user": user, "check_if_admin": lambda: is_admin}


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            session["user_id"] = user.id
            flash("Logged in successfully.", "success")
            return redirect(url_for('blog'))
        else:
            flash("Invalid username or password.", "error")
    return render_template("login.html", form=form)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("You need to login first.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("You need to login first.", "error")
            return redirect(url_for("login"))
        user = User.query.get(session["user_id"])
        if not user.is_admin:
            flash("You do not have access to this page.", "error")
            return redirect(url_for("blog"))
        return f(*args, **kwargs)

    return decorated_function


def check_if_admin():
    if 'user' in session:
        user = User.query.get(session['user_id'])
        return user.is_admin
    return False


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))
