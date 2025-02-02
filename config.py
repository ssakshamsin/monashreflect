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

    # Pagination configuration
    REVIEWS_PER_PAGE = 10
    UNITS_PER_PAGE = 12

    # Review configuration
    MINIMUM_REVIEW_LENGTH = 10
    MAXIMUM_REVIEW_LENGTH = 1000

    # Admin configuration
    ADMIN_USER = os.environ.get('ADMIN_USER')

    # Vote configuration
    ALLOW_ANONYMOUS_VOTES = False