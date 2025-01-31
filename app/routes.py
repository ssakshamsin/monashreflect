from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify, current_app
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.models import User, Unit, Review, Vote
from app.forms import RegistrationForm, LoginForm, ReviewForm, SearchForm
from datetime import datetime
from app.email import send_verification_email
from urllib.parse import urlparse

main = Blueprint('main', __name__)
auth = Blueprint('auth', __name__)

@main.route('/')
def home():
    # Add some sample units if none exist
    if Unit.query.count() == 0:
        sample_units = [
            Unit(
                code='COMP1000',
                name='Introduction to Computer Science',
                description='Learn the basics of programming and computer science concepts.',
                faculty='Science and Engineering'
            ),
            Unit(
                code='COMP2000',
                name='Data Structures',
                description='Advanced programming concepts and data structures.',
                faculty='Science and Engineering'
            )
        ]
        db.session.add_all(sample_units)
        db.session.commit()
    
    units = Unit.query.all()
    return render_template('home.html', units=units)

@main.route('/unit/<string:code>', methods=['GET'])
def unit(code):
    unit = Unit.query.filter_by(code=code).first_or_404()
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'newest')
    
    if sort == 'newest':
        reviews = Review.query.filter_by(unit_id=unit.id)\
            .order_by(Review.timestamp.desc())
    elif sort == 'highest_rated':
        reviews = Review.query.filter_by(unit_id=unit.id)\
            .order_by(Review.rating.desc())
    elif sort == 'most_voted':
        reviews = Review.query.filter_by(unit_id=unit.id)\
            .order_by((Review.upvotes - Review.downvotes).desc())
    
    reviews = reviews.paginate(page=page, 
                             per_page=current_app.config['REVIEWS_PER_PAGE'])
    
    return render_template('unit.html', unit=unit, reviews=reviews, sort=sort)

@auth.route('/login', methods=['GET', 'POST'])  # Add both GET and POST methods
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.home')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)

@auth.route('/register')
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        send_verification_email(user)
        flash('Please check your email to verify your account.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register', form=form)

@auth.route('/verify/<token>')
def verify_email(token):
    user = User.verify_token(token)
    if not user:
        flash('The verification link is invalid or has expired.')
        return redirect(url_for('main.home'))
    user.verified = True
    db.session.commit()
    flash('Your email has been verified.')
    return redirect(url_for('auth.login'))


@auth.route('/logout')
def logout():
    return redirect(url_for('main.home'))

@main.route('/unit/<string:code>/review', methods=['GET', 'POST'])
@login_required
def submit_review(code):
    unit = Unit.query.filter_by(code=code).first_or_404()
    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(content=form.content.data,
                       rating=int(form.rating.data),
                       unit_id=unit.id,
                       author=None if form.anonymous.data else current_user,
                       timestamp=datetime.utcnow())
        db.session.add(review)
        db.session.commit()
        flash('Your review has been submitted.')
        return redirect(url_for('main.unit', code=code))
    return render_template('submit_review.html', title='Submit Review', 
                         form=form, unit=unit)

@main.route('/review/<int:id>/<string:vote_type>')
@login_required
def vote_review(id, vote_type):
    review = Review.query.get_or_404(id)
    if vote_type not in ['up', 'down']:
        return jsonify({'error': 'Invalid vote type'}), 400
    review.vote(current_user, vote_type)
    return jsonify({
        'upvotes': review.upvotes,
        'downvotes': review.downvotes
    })

@main.route('/search')
def search():
    form = SearchForm()
    query = request.args.get('query', '')
    faculty = request.args.get('faculty', '')
    
    units = Unit.query
    if query:
        units = units.filter(
            (Unit.code.contains(query)) |
            (Unit.name.contains(query)) |
            (Unit.description.contains(query))
        )
    if faculty:
        units = units.filter_by(faculty=faculty)
    
    units = units.order_by(Unit.code).all()
    return render_template('search.html', units=units, form=form)

@main.route('/profile')
@login_required
def profile():
    page = request.args.get('page', 1, type=int)
    reviews = Review.query.filter_by(author=current_user)\
        .order_by(Review.timestamp.desc())\
        .paginate(page=page, per_page=current_app.config['REVIEWS_PER_PAGE'])
    return render_template('profile.html', user=current_user, reviews=reviews)