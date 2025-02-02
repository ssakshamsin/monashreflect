from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from config import Config
from flask_wtf.csrf import CSRFProtect
from security import init_security

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config['SECRET_KEY'] = 'dev-secret-key'
    csrf = CSRFProtect(app)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    limiter = init_security(app)
    login_manager.login_view = 'auth.login'
    
    @app.errorhandler(429)  # Too Many Requests
    def ratelimit_handler(e):
        return "Too many requests. Please try again later.", 429

    @app.after_request
    def add_security_headers(response):
        for header, value in app.config['SECURITY_HEADERS'].items():
            response.headers[header] = value
        return response

    with app.app_context():
        # Import routes inside app context
        from app.routes import main, auth
        app.register_blueprint(main)
        app.register_blueprint(auth)
        
        # Create database tables
        db.create_all()

    return app