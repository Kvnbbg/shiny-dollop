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

    # Dynamically load the appropriate configuration
    env_config = os.getenv('FLASK_ENV', 'development')
    config_class = {
        "development": DevelopmentConfig,
        "testing": TestingConfig,
        "production": ProductionConfig
    }.get(env_config, DevelopmentConfig)
    app.config.from_object(config_class)

    # Initialize Flask extensions with the app instance
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    
    # CSRF protection
    csrf.init_app(app)

    # Flask-Session configuration for server-side session management
    app.config.setdefault('SESSION_TYPE', 'filesystem')
    Session(app)

    # Configure Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        # Delayed import to avoid circular dependencies
        from .models import User
        return User.query.get(int(user_id))

    # Register blueprints
    from .auth.routes import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    from .main.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Exempt specific routes from CSRF protection if necessary
    # Ensure to import the view function directly if you need to exempt it
    # Example:
    # from .main.views import home_view
    # csrf.exempt(home_view)

    return app
