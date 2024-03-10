import logging
from urllib.parse import urljoin, urlparse
from flask import Blueprint, flash, redirect, render_template, request, url_for, session, get_flashed_messages
from flask_login import current_user, login_required, login_user, logout_user
from app import db  # Import the database instance
from app.models import User
from .forms import LoginForm, RegistrationForm

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

auth = Blueprint('auth', __name__)

@auth.route('/set_language/<language>')
def set_language(language):
    # Check to ensure the language code is supported
    supported_languages = ['en', 'fr']
    if language in supported_languages:
        session['lang'] = language
    else:
        flash("Unsupported language.", "error")
    return redirect(url_for('main.home'))

def is_safe_url(target):
    """
    Simplified function to validate that the target URL is safe for redirection.
    """
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.hostname == request.host_url.rstrip('/')

@auth.route("/login", methods=["GET", "POST"])
def login():
    # Initialize error_present to False at the beginning
    error_present = False

    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("You have been logged in!", "success")
            next_page = request.args.get("next")
            if not next_page or not is_safe_url(next_page):
                next_page = url_for("main.home")
            return redirect(next_page)
        else:
            flash("Login Unsuccessful. Please check username and password.", "error")
            # Set error_present to True when there is a login error
            error_present = True
    else:
        # Check for 'error' flash messages if form validation fails
        error_present = any(category == 'error' for category, message in get_flashed_messages(with_categories=True))

    return render_template("login.html", title="Login", form=form, error_present=error_present)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("main.home"))

@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data if 'email' in form else None)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash("Your account has been created! You are now logged in.", "success")
        return redirect(url_for("main.home"))
    return render_template("register.html", title="Register", form=form)


@auth.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

# Flask application error handlers
@auth.app_errorhandler(404)
def not_found_error(error):
    return render_template("404.html"), 404


@auth.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template("500.html"), 500
