import logging
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField
from wtforms.validators import DataRequired, EqualTo, Length, Regexp, ValidationError, Email, Optional

from app.models import User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoginForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[DataRequired(), Length(min=4, max=25)],
        render_kw={"placeholder": "Username", "class": "form-control"}
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=6)],
        render_kw={"placeholder": "Password", "class": "form-control"}
    )
    submit = SubmitField(
        "Login",
        render_kw={"class": "btn btn-primary"}
    )

class RegistrationForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(min=4, max=25),
            Regexp(
                "^[A-Za-z][A-Za-z0-9_.]*$",
                0,
                "Usernames must have only letters, numbers, dots or underscores",
            ),
        ],
        render_kw={"placeholder": "Username", "class": "form-control"}
    )
    email = EmailField(
        "Email (Optional)",
        validators=[
            Optional(),
            Email(message="Please enter a valid email address."),
        ],
        render_kw={"placeholder": "Email (Optional)", "class": "form-control"}
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=6, message="Password must be at least 6 characters long."),
            Regexp(
                "^.*(?=.*[a-zA-Z])(?=.*[0-9])(?=.*[\W_]).*$",
                0,
                "Password must contain a letter, a number, and a special character.",
            ),
        ],
        render_kw={"placeholder": "Password", "class": "form-control"}
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match."),
        ],
        render_kw={"placeholder": "Confirm Password", "class": "form-control"}
    )
    submit = SubmitField(
        "Sign Up",
        render_kw={"class": "btn btn-success"}
    )

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            logger.warning(f"Attempt to register with taken username: {username.data}")
            raise ValidationError("That username is taken. Please choose a different one.")

    def validate_email(self, email):
        if email.data:  # Only validate if email is provided
            user = User.query.filter_by(email=email.data.lower().strip()).first()
            if user:
                logger.warning(f"Attempt to register with taken email: {email.data}")
                raise ValidationError("That email is already in use. Please choose a different one.")
