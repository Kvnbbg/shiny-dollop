import os
from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_wtf import CSRFProtect
from config import DevelopmentConfig, ProductionConfig, TestingConfig

# Create extension instances but don't initialize them yet
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)

    # Load the appropriate configuration based on FLASK_ENV environment variable
    config_map = {
        "development": DevelopmentConfig,
        "testing": TestingConfig,
        "production": ProductionConfig
    }
    config_name = os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config_map.get(config_name, DevelopmentConfig))

    # Initialize extensions with the Flask app instance
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)

    # Configure server-side session management
    app.config['SESSION_TYPE'] = 'filesystem'
    Session(app)

    # Configure Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        from .models import User  # Import here to avoid circular import issues
        return User.query.get(int(user_id))

    # Optionally, if you want to create database tables automatically
    # with app.app_context():
    #     db.create_all()

    # Register application blueprints
    from .auth.routes import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    from .main.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
