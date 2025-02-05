
from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify, current_app, abort
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.models import User, Unit, Review, Vote
from app.forms import RegistrationForm, LoginForm, ReviewForm, SearchForm, UpdateProfileForm, AdminUserActionForm
from datetime import datetime
from urllib.parse import urlparse
from security import sanitize_input, validate_input
from app.utils import save_profile_picture

main = Blueprint('main', __name__)
auth = Blueprint('auth', __name__)

@main.route('/api/search')
def live_search():
    query = request.args.get('query', '')
    page = request.args.get('page', 1, type=int)
    per_page = 9  # Number of results per page
    
    # Query the database
    units = Unit.query.filter(
        db.or_(
            Unit.code.ilike(f'%{query}%'),
            Unit.name.ilike(f'%{query}%'),
            Unit.faculty.ilike(f'%{query}%')
        )
    ).paginate(page=page, per_page=per_page)
    
    # Format results
    results = {
        'units': [{
            'code': unit.code,
            'name': unit.name,
            'faculty': unit.faculty,
            'url': url_for('main.unit', code=unit.code)
        } for unit in units.items],
        'total_pages': units.pages,
        'current_page': units.page,
        'query': query
    }
    
    return jsonify(results)

@main.route('/units', methods=['GET'])
def home():
    page = request.args.get('page', 1, type=int)
    units = Unit.query.paginate(
        page=page, 
        per_page=9,
        error_out=False
    )
    if request.headers.get('Accept') == 'application/json':
        return jsonify({
            'units': [{
                'code': unit.code,
                'name': unit.name,
                'faculty': unit.faculty,
            } for unit in units.items],
            'page': units.page,
            'pages': units.pages,
            'total': units.total
        })
    return render_template('home.html', units=units)

@main.route('/unit/<string:code>', methods=['GET', 'POST'])
@validate_input
def unit(code):
    code = sanitize_input(code)
    if not code:
        abort(400)
    unit = Unit.query.filter_by(code=code).first_or_404()
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'newest')
    form = ReviewForm()
    
    if form and form.validate_on_submit():
        review = Review(content=form.content.data,
            rating=int(form.rating.data),
            unit_id=unit.id,
            user=current_user,
            is_anonymous=form.anonymous.data,
        )
        
        db.session.add(review)
        db.session.commit()
        flash('Your review has been posted.')
        return redirect(url_for('main.unit', code=code))
    
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
    

    for review in reviews.items:
        review.user_vote = review.get_vote_status(current_user) if current_user.is_authenticated else None
    
    return render_template('unit.html', unit=unit, reviews=reviews, sort=sort, form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        elif user.is_deleted:
            flash('This account has been deactivated.')
            return redirect(url_for('auth.login'))

        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.home')
        return redirect(next_page)
    
    # This return statement should be at this indentation level
    return render_template('auth/login.html', title='Sign In', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!') 
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register', form=form)


@auth.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.home'))

@main.route('/unit/<string:code>/review', methods=['GET', 'POST'])
@login_required
def submit_review(code):
    unit = Unit.query.filter_by(code=code).first_or_404()
    form = ReviewForm()
    
    if form.validate_on_submit():
        review = Review(
            content=form.content.data,
            rating=int(form.rating.data),
            unit_id=unit.id,
            author=current_user,
            is_anonymous=form.anonymous.data,
        )
        db.session.add(review)
        db.session.commit()
        flash('Your review has been submitted.')
        return redirect(url_for('main.unit', code=code))
    
    return render_template('submit_review.html', title='Submit Review', form=form, unit=unit)

from flask import jsonify, request

@main.route('/review/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_review(id):
    review = Review.query.get_or_404(id)
    
    if not review.can_edit(current_user):
        if request.is_json:  # API request
            return jsonify({'error': 'Unauthorized'}), 403
        flash('You cannot edit this review.')
        return redirect(url_for('main.unit', code=review.unit.code))
    
    form = ReviewForm()
    
    if request.method == 'GET':  
        if request.is_json:  # Handle API request
            return jsonify({
                'content': review.content,
                'rating': review.rating,
                'anonymous': review.is_anonymous
            })
        # Normal browser form loading
        form.content.data = review.content
        form.rating.data = str(review.rating)
        form.anonymous.data = review.is_anonymous

    if form.validate_on_submit():
        review.content = form.content.data
        review.rating = int(form.rating.data)
        review.is_anonymous = form.anonymous.data
        db.session.commit()

        if request.is_json:  # JSON response for fetch requests
            return jsonify({
                'updated_content': review.content,
                'updated_rating': review.rating
            })
        
        flash('Your review has been updated.')
        return redirect(url_for('main.unit', code=review.unit.code))

    return render_template('edit_review.html', form=form, review=review)


@main.route('/review/<int:id>/delete', methods=['POST'])
@login_required
def delete_review(id):
    review = Review.query.get_or_404(id)
    if not review.can_edit(current_user):
        flash('You cannot delete this review.')
        return redirect(url_for('main.unit', code=review.unit.code))
    
    unit_code = review.unit.code
    db.session.delete(review)
    db.session.commit()
    flash('Your review has been deleted.')
    return redirect(url_for('main.unit', code=unit_code))


@main.route('/review/<int:id>/<string:vote_type>', methods=['POST'])
@login_required
def vote_review(id, vote_type):
    if vote_type not in ['up', 'down']:
        abort(400)
    if not request.is_json:
        return jsonify({'error': 'Invalid request'}), 400
        
    review = Review.query.get_or_404(id)
    if vote_type not in ['up', 'down']:
        return jsonify({'error': 'Invalid vote type'}), 400

    existing_vote = Vote.query.filter_by(
        user_id=current_user.id,
        review_id=review.id
    ).first()

    if existing_vote:
        if existing_vote.vote_type == vote_type:
            # Remove vote if clicking the same button
            db.session.delete(existing_vote)
            if vote_type == 'up':
                review.upvotes = max(0, review.upvotes - 1)
            else:
                review.downvotes = max(0, review.downvotes - 1)
            user_vote = None
        else:
            # Change vote if clicking different button
            existing_vote.vote_type = vote_type
            if vote_type == 'up':
                review.upvotes += 1
                review.downvotes = max(0, review.downvotes - 1)
            else:
                review.downvotes += 1
                review.upvotes = max(0, review.upvotes - 1)
            user_vote = vote_type
    else:
        # New vote
        new_vote = Vote(user_id=current_user.id, review_id=review.id, vote_type=vote_type)
        db.session.add(new_vote)
        if vote_type == 'up':
            review.upvotes += 1
        else:
            review.downvotes += 1
        user_vote = vote_type

    db.session.commit()

    return jsonify({
        'upvotes': review.upvotes,
        'downvotes': review.downvotes,
        'user_vote': user_vote
    })

@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateProfileForm()
    admin_form = AdminUserActionForm() if current_user.is_admin else None
    if form.validate_on_submit():
        if form.profile_pic.data:
            picture_file = save_profile_picture(form.profile_pic.data)
            current_user.profile_pic = picture_file
        current_user.username = form.username.data
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('main.profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username

    page = request.args.get('page', 1, type=int)
    
    # Get both regular and anonymous reviews
    reviews = Review.query.filter(
        (Review.user_id == current_user.id)
    ).order_by(Review.timestamp.desc())
    
    reviews = reviews.paginate(
        page=page, 
        per_page=current_app.config['REVIEWS_PER_PAGE'],
        error_out=False
    )
    return render_template('profile.html', user=current_user, reviews=reviews, form=form, admin_form=admin_form)


@main.route('/profile/delete', methods=['POST'])
@login_required
def delete_account():
    current_user.soft_delete()
    logout_user()
    flash('Your account has been deactivated.')
    return redirect(url_for('main.home'))


@main.route('/unit/<string:code>/vote', methods=['POST'])
@login_required
def vote_unit(code):
    unit = Unit.query.filter_by(code=code).first_or_404()
    data = request.json
    vote_type = data.get("vote_type")

    if vote_type not in ["up", "down"]:
        return jsonify({"error": "Invalid vote type"}), 400

    unit.vote(current_user, vote_type)
    
    return jsonify({
        "upvotes": unit.upvotes,
        "downvotes": unit.downvotes,
        "total_votes": unit.total_votes
    })


@main.route('/search')
def search():
    form = SearchForm()
    query = request.args.get('query', '').strip()
    page = request.args.get('page', 1, type=int)  # Get the current page number
    per_page = 9
    
    units = Unit.query
    if query:
        units = units.filter(
            (Unit.code.contains(query)) |
            (Unit.name.contains(query)) |
            (Unit.faculty.contains(query))
        )
    
    units = units.paginate(
        page=page,
        per_page=9,
        error_out=False
    )
    return render_template('search.html', units=units, form=form)

@main.route("/contact")
def contact():
    return render_template("contact.html")

@main.route("/about")
def about():
    return render_template("about.html")

@main.route("/faq")
def faq():
    return render_template("faq.html")

@main.route("/privacy_policy")
def privacy_policy():
    return render_template("privacy_policy.html")

@main.route("/terms_conditions")
def terms_conditions():
    return render_template("terms_conditions.html")

@main.route("/rules")  
def rules():
    return render_template("rules.html")

@main.route("/")
def landing():
    return render_template("landing.html")

@main.route('/admin/delete_user', methods=['POST'])
@login_required
def admin_delete_user():
    if not current_user.is_admin:
        abort(403)
        
    form = AdminUserActionForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if user.is_admin:
                flash('Cannot delete admin users.')
                return redirect(url_for('main.profile'))
            if user.is_deleted:
                flash('This account is already deleted.')
                return redirect(url_for('main.profile'))
                
            user.soft_delete()
            flash(f'User {user.username} has been deleted.')
        else:
            flash('User not found.')
            
    return redirect(url_for('main.profile'))

@main.route('/admin/restore_user', methods=['POST'])
@login_required
def admin_restore_user():
    if not current_user.is_admin:
        abort(403)
        
    form = AdminUserActionForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if not user.is_deleted:
                flash('This account is not deleted.')
                return redirect(url_for('main.profile'))
                
            user.restore_account()
            flash(f'User account {user.username} has been restored.')
        else:
            flash('User not found.')
            
    return redirect(url_for('main.profile'))