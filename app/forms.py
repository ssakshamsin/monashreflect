from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, SubmitField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Regexp
from app.models import User
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(),
            Regexp(r'^[a-zA-Z0-9_]+$', message="Username can only contain letters, numbers, and underscores.")])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', 
        validators=[
            DataRequired(),
            Length(min=4, max=20, message="Username must be between 4 and 20 characters"),
            Regexp(r'^[a-zA-Z0-9_]+$', message="Username can only contain letters, numbers, and underscores.")
        ]
    )
    password = PasswordField('Password', validators=[DataRequired(), Length(min=7, max=128, message="Password must be at least 7 characters")])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('This username is already taken.')

class ReviewForm(FlaskForm):
    content = TextAreaField('Review', validators=[DataRequired(), Length(min=10, max=1000)])
    rating = SelectField('Rating', choices=[(str(i), str(i)) for i in range(1, 6)], 
                        validators=[DataRequired()])
    anonymous = BooleanField('Post Anonymously')
    submit = SubmitField('Submit Review')

class SearchForm(FlaskForm):
    query = StringField('Search Units')
    faculty = SelectField('Faculty', choices=[('', 'All Faculties')], default='')
    submit = SubmitField('Search')

class UpdateProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    profile_pic = FileField('Profile Picture', 
                          validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

# Update app/routes.py