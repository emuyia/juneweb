from src import app, db, config
from src.models import User
from src.forms import LoginForm
from flask import render_template, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from functools import wraps
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

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


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            # flash("Logged in successfully.", "success")
            return redirect(url_for('blog'))
        else:
            flash("Invalid username or password.", "error")
    return render_template("login.html", form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))


@app.cli.command("createadmin")
def create_admin_user():
    admin = User(username=config.ADMIN_USERNAME)
    admin.set_password(config.ADMIN_PASSWORD)
    admin.is_admin = True
    db.session.add(admin)
    db.session.commit()
    print(f"Admin user created with username: {config.ADMIN_USERNAME}")
