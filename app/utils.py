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
    picture_path = os.path.join(current_app.root_path, 'static\\pictures', picture_fn)

    if current_user.profile_pic != "default.jpg":
        old_picture_path = os.path.join(current_app.root_path, 'static\\pictures', current_user.profile_pic)
        if os.path.exists(old_picture_path):
            os.remove(old_picture_path)


    output_size = (150, 150)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn