from src import app, db
from src.models import User
from werkzeug.security import check_password_hash
from functools import wraps
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from flask import render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash
from sqlalchemy import func
from validate_email import validate_email
import click


login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("You need to login as an admin first.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        submit_type = request.form.get("submit")

        if submit_type == "Login":
            username = request.form.get("username")
            email = request.form.get("email")
            password = request.form.get("password")
            user = None
            if email:
                # Attempt to log in by email
                email = email.lower()
                user = User.query.filter(func.lower(User.email) == email).first()
            elif username:
                # Attempt to log in by username
                username = username.lower()
                user = User.query.filter(func.lower(User.username) == username).first()

            if user and check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for("blog"))
            else:
                flash("Invalid login credentials.", "error")
        elif submit_type == "Register":
            username = request.form.get("username")
            password = request.form.get("password")
            email = request.form.get("email")

            if not username.isalnum():
                flash("Username should be alphanumeric.", "error")
                return render_template("login.html")

            existing_user = User.query.filter(
                func.lower(User.username) == func.lower(username)
            ).first()
            if existing_user is not None:
                flash("Username is already taken.", "error")
                return render_template("login.html")

            if not password or len(password) <= 3:
                flash("Password should be longer than 3 characters.", "error")
                return render_template("login.html")

            if not username or len(username) <= 3:
                flash("Username should be longer than 3 characters.", "error")
                return render_template("login.html")

            if email:
                email = email.lower()
                if not validate_email(email):
                    flash("Invalid email address.", "error")
                    return render_template("login.html")

                existing_email = User.query.filter_by(email=email).first()
                if existing_email:
                    flash("Email is already in use.", "error")
                    return render_template("login.html")

            hashed_password = generate_password_hash(password)
            new_user = User(username=username, password=hashed_password, email=email)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for("blog"))

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Successfully logged out.", "success")
    return redirect(url_for("login"))


@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    if request.method == "POST":
        new_username = request.form.get("username")
        new_email = request.form.get("email")
        new_password = request.form.get("password")

        if new_username:
            current_user.username = new_username

        if new_email:
            current_user.email = new_email

        if new_password:
            current_user.password = generate_password_hash(new_password)

        new_picture_url = request.form.get("profile_picture")

        if new_picture_url:
            current_user.profile_picture = new_picture_url

        db.session.commit()
        flash("Changes saved.", "success")

    return render_template("dashboard.html")


@app.cli.command("createadmin")
def create_admin_user():
    admin = User(username=app.config["ADMIN_USERNAME"])
    admin.set_password(app.config["ADMIN_PASSWORD"])
    admin.is_admin = True
    db.session.add(admin)
    db.session.commit()
    print(f"Admin user created with username: {admin.username}")


@app.cli.command("reset-password")
@click.argument("username")
def reset_password(username):
    # Reset a user's password.
    user = User.query.filter_by(username=username).first()
    if user:
        # Prompt for a new password
        new_password = click.prompt("Please enter a new password", hide_input=True,
                                    confirmation_prompt=True)
        # Use the set_password method of the User model
        user.set_password(new_password)
        # Update the user's password in the database
        db.session.commit()
        click.echo(f"Password for user {username} has been updated.")
    else:
        click.echo(f"User {username} not found.")
