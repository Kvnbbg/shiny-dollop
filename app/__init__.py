import os
from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_wtf import CSRFProtect
from config import DevelopmentConfig, ProductionConfig, TestingConfig

# Initialize Flask extensions (but don't instantiate them yet)
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)

    # Dynamically load the appropriate configuration
    config_class = {
        "development": DevelopmentConfig,
        "testing": TestingConfig,
        "production": ProductionConfig
    }.get(os.getenv('FLASK_ENV', 'development'), DevelopmentConfig)
    app.config.from_object(config_class)

    # Initialize Flask extensions with the app instance
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    
    # Configure CSRF
    csrf.init_app(app)

    # Configure server-side session management (if using Flask-Session)
    app.config['SESSION_TYPE'] = 'filesystem'
    Session(app)

    # Flask-Login configuration
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # User loader callback for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from your_application.models import User  # Adjust import as necessary
        return User.query.get(int(user_id))

    # Blueprint registration
    from your_application.auth.routes import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    from your_application.main.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Optionally, if you have specific routes or blueprints that don't require CSRF protection,
    # you can exempt them as shown below:
    # csrf.exempt(your_blueprint_or_view_function)

    return app
