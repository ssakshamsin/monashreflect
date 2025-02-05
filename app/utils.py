import os
from PIL import Image
from flask import current_app
import secrets
from flask_login import current_user

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_profile_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static', 'pictures', picture_fn)  # Use os.path.join() here

    # Ensure the directory exists
    os.makedirs(os.path.dirname(picture_path), exist_ok=True)

    # Remove the old profile picture if it's not the default one
    if current_user.profile_pic != "default.png":
        old_picture_path = os.path.join(current_app.root_path, 'static', 'pictures', current_user.profile_pic)
        if os.path.exists(old_picture_path):
            os.remove(old_picture_path)

    # Resize the image to fit within 150x150 dimensions
    output_size = (150, 150)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    
    # Save the new profile picture
    i.save(picture_path)
    
    return picture_fn
