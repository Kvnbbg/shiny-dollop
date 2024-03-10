import os
from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

from config import DevelopmentConfig, ProductionConfig, TestingConfig

# Create extension instances
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()  # CSRF protection

def create_app():
    app = Flask(__name__)

    # Determine configuration class based on FLASK_ENV environment variable
    config_class = {
        "development": DevelopmentConfig,
        "testing": TestingConfig,
        "production": ProductionConfig
    }.get(os.environ.get("FLASK_ENV"), DevelopmentConfig)

    app.config.from_object(config_class)

    # Initialize extensions with the app object
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)  # Initialize CSRF protection

    # Setup for Flask-Login
    login_manager.login_view = "auth.login"  # Specify the view function that handles logins
    login_manager.login_message_category = "info"

    # User loader function for Flask-Login
    from app.models import User  # Import here to avoid circular imports
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Initialize the user table and other database-related setup
    with app.app_context():
        from .models import create_user_table  # Adjusted import
        create_user_table()  # Create user table if it doesn't exist

    # Register blueprints
    from .auth.routes import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    from .main.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Additional setup or initialization can be done here
    # E.g., setup scheduled jobs, initialize other app components

    return app
