import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()

class Config:
    # Basic Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') or True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or MAIL_USERNAME

    # Pagination configuration
    REVIEWS_PER_PAGE = 10
    UNITS_PER_PAGE = 12

    # Review configuration
    MINIMUM_REVIEW_LENGTH = 10
    MAXIMUM_REVIEW_LENGTH = 1000

    # Admin configuration
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
    
    # Verification configuration
    VERIFY_EMAIL_TOKEN_EXPIRATION = 3600  # 1 hour

    # Vote configuration
    ALLOW_ANONYMOUS_VOTES = False