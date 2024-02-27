from src import app, db
from src.models import User, Role, CustomAnonymousUser
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
from itsdangerous import URLSafeTimedSerializer
from mailersend import emails
from wtforms.validators import Email, ValidationError


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.anonymous_user = CustomAnonymousUser

MAILERSEND_API_URL = "https://api.mailersend.com/v1/email"

ROLE_DISPLAY_NAMES = {
    "Admin": "Admin",
    "Moderator": "Moderator",
    "User": "User",
}


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.has_role("Admin"):
            flash("You need to login as an admin first.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


def get_role_nick(role_identifier):
    # Returns the display name for a given role identifier
    return ROLE_DISPLAY_NAMES.get(role_identifier, role_identifier)


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])
    return serializer.dumps(email, salt=app.config["SECURITY_PASSWORD_SALT"])


def send_confirmation_email(user):
    try:
        mailer = emails.NewEmail(app.config["MAILERSEND_API_KEY"])

        mail_from = {
            "name": "admin",
            "email": "admin@junes.website",
        }

        recipients = [
            {
                "name": user.username,
                "email": user.email,
            }
        ]

        reply_to = {
            "name": "admin",
            "email": "admin@junes.website",
        }

        token = generate_confirmation_token(user.email)
        domain = app.config["DOMAIN"]

        subject = f"[{domain}] - email confirmation"
        html_content = (
            f"<p><a href='https://www.{domain}/confirm/{token}'>Confirm Email</a></p>"
        )
        text_content = f"Confirm Email: https://www.{domain}/confirm/{token}"

        mail_body = {
            "from": mail_from,
            "to": recipients,
            "subject": subject,
            "html": html_content,
            "text": text_content,
            "reply_to": reply_to,
        }

        response = mailer.send(mail_body)
        print(f"Email sent; response: {response}")

    except Exception as e:
        print(f"An error occurred: {e}")


@app.route("/confirm/<token>")
def confirm_email(token):
    try:
        serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])
        email = serializer.loads(
            token,
            salt=app.config["SECURITY_PASSWORD_SALT"],
            max_age=3600,  # Token expires after 1 hour
        )
    except:
        flash("The confirmation link is invalid or has expired.", "error")
        return redirect(url_for("dashboard"))

    user = User.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        flash("Account already confirmed. Please login.", "success")
    else:
        user.confirmed = True
        db.session.commit()  # Commit the confirmed status to the database
        flash("Your account has been confirmed.", "success")

    return redirect(url_for("dashboard"))


@app.route("/confirm/resend")
@login_required
def resend_confirmation_email():
    if not current_user.confirmed:
        send_confirmation_email(current_user)
        flash("A new confirmation email has been sent.", "success")
    else:
        flash("Your account is already confirmed.", "info")
    return redirect(url_for("dashboard"))


def validate_email_address(email):
    try:
        # WTForms validators require form and field objects, so we create dummy ones
        email_validator = Email(message="Invalid email")
        email_validator(None, type("DummyField", (object,), {"data": email}))
        return True
    except ValidationError:
        return False


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        submit_type = request.form.get("submit")

        if submit_type == "Login":
            username = request.form.get("username")
            email = request.form.get("email") or None
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
            nickname = username
            password = request.form.get("password")
            email = request.form.get("email") or None

            existing_email = User.query.filter(User.email == email).first() if email else None
            if existing_email:
                flash("Email is already in use.", "error")
                return render_template("login.html")

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

            new_user = User(
                username=username,
                nickname=nickname,
                password=hashed_password,
                email=email,
                confirmed=False,
            )

            # Conditionally send confirmation email if an email is provided
            if email:
                if validate_email_address(email):
                    send_confirmation_email(new_user)
                    flash("A confirmation email has been sent.", "success")
                else:
                    flash("Invalid email address.", "danger")
                    return render_template("login.html")

            db.session.add(new_user)
            db.session.commit()

            # Log in the user automatically
            login_user(new_user)

            flash("Account created successfully.", "success")

            return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    if request.method == "POST":
        new_nickname = request.form.get("nickname")
        new_email = request.form.get("email").lower()  # Normalize email to lowercase
        new_password = request.form.get("password")
        new_about = request.form.get("about")

        if new_nickname:
            current_user.nickname = new_nickname

        if new_email:
            existing_email = User.query.filter(User.email == new_email).first() if new_email else None
            if validate_email_address(new_email):
                if new_email.lower() != (current_user.email or "").lower():
                    current_user.email = new_email
                    current_user.confirmed = False
                    send_confirmation_email(current_user)
                    flash("A confirmation email has been sent.", "success")
                elif (
                    new_email.lower() == current_user.email.lower()
                    and not current_user.confirmed
                ):
                    send_confirmation_email(current_user)
                    flash("A new confirmation email has been sent.", "success")
                    return render_template("dashboard.html")
                else:
                    flash("You are already using this email address.", "danger")
                    return render_template("dashboard.html")
            elif existing_email:
                flash("Email is already in use.", "error")
                return render_template("dashboard.html")
            else:
                flash("Invalid email address.", "danger")
                return render_template("dashboard.html")

        if new_password:
            current_user.password = generate_password_hash(new_password)

        new_picture_url = request.form.get("profile_picture")

        if new_picture_url:
            current_user.profile_picture = new_picture_url

        if new_about:
            current_user.about = new_about

        db.session.commit()
        flash("Changes saved.", "success")

    return render_template("dashboard.html")


@app.cli.command("createadmin")
def create_admin_user():
    admin_role = Role.query.filter_by(name="Admin").first()
    if admin_role is None:
        print("Admin role does not exist. Please create it first.")
        return

    admin = User(username=app.config["ADMIN_USERNAME"])
    admin.set_password(app.config["ADMIN_PASSWORD"])
    admin.role = admin_role
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
        new_password = click.prompt(
            "Please enter a new password", hide_input=True, confirmation_prompt=True
        )
        # Use the set_password method of the User model
        user.set_password(new_password)
        # Update the user's password in the database
        db.session.commit()
        click.echo(f"Password for user {username} has been updated.")
    else:
        click.echo(f"User {username} not found.")


@app.cli.command("reset-username")
@click.argument("username")
def reset_username(username):
    # Reset a user's username.
    user = User.query.filter_by(username=username).first()
    if user:
        # Prompt for a new username
        new_username = click.prompt(
            "Please enter a new username", hide_input=False, confirmation_prompt=True
        )
        user.username = new_username
        # Update the user's username in the database
        db.session.commit()
        click.echo(f"Username for user {username} has been changed to {user.username}.")
    else:
        click.echo(f"User {username} not found.")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Successfully logged out.", "success")
    return redirect(url_for("login"))
