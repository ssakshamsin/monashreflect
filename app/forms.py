from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, SubmitField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, NumberRange
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Please use a different username.')

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