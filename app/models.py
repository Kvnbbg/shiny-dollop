from datetime import timedelta
from app import db
from flask_login import UserMixin, login_user
from flask import app, session
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=True)
    password_hash = db.Column(db.String(128), nullable=False)
    def __init__(self, username, email=None, password=None):
        self.username = username
        self.email = email
        if password:
            self.password = password

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Function to create the user table directly with SQL
def create_user_table():
    sql = """
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(64) NOT NULL UNIQUE,
        email VARCHAR(120) UNIQUE,
        password_hash VARCHAR(128) NOT NULL
    );
    """
    # Assuming you have a connection and a cursor to your SQLite database
    connection = db.get_engine().raw_connection()
    cursor = connection.cursor()
    cursor.execute(sql)
    connection.commit()
    cursor.close()
    connection.close()

# Handling Expiration Logic (Considered in Session Management)

def login_user_with_expiration(user, remember=True):
    # Log in the user as usual
    login_user(user, remember=remember)
    # Set session expiration date to 1 year from now
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=365)