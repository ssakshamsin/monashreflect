from functools import wraps
from flask import request, abort, current_app
import re
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman


def init_security(app):
    # Initialize Talisman for security headers
    Talisman(
        app,
        content_security_policy=app.config['SECURITY_HEADERS']['Content-Security-Policy'],
        force_https=True
    )
    return 

def sanitize_input(input_string):
    """Remove potentially dangerous characters from input"""
    if input_string is None:
        return None
    # Remove SQL injection characters
    cleaned = re.sub(r'[;\'\"\\]', '', input_string)
    # Remove script tags
    cleaned = re.sub(r'<script.*?>.*?</script>', '', cleaned, flags=re.DOTALL)
    return cleaned

def validate_input(func):
    """Decorator to validate and sanitize input data"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if request.method == 'POST':
            for key, value in request.form.items():
                if isinstance(value, str):
                    request.form = request.form.copy()
                    request.form[key] = sanitize_input(value)
        return func(*args, **kwargs)
    return wrapper