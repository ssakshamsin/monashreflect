from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from time import time

import jwt
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_verified = db.Column(db.Boolean, default=False)
    reviews = db.relationship('Review', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_verification_token(self, expires_in=3600):
        return jwt.encode(
            {'verify_email': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )

    @staticmethod
    def verify_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                          algorithms=['HS256'])['verify_email']
        except:
            return None
        return User.query.get(id)

class Unit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    faculty = db.Column(db.String(50))
    reviews = db.relationship('Review', backref='unit', lazy='dynamic')    
    def vote(self, user, vote_type):
        existing_vote = Vote.query.filter_by(
            user_id=user.id, review_id=self.id).first()
        
        if existing_vote:
            if existing_vote.vote_type == vote_type:
                db.session.delete(existing_vote)
                if vote_type == 'up':
                    self.upvotes -= 1
                else:
                    self.downvotes -= 1
            else:
                existing_vote.vote_type = vote_type
                if vote_type == 'up':
                    self.upvotes += 1
                    self.downvotes -= 1
                else:
                    self.downvotes += 1
                    self.upvotes -= 1
        else:
            new_vote = Vote(user_id=user.id, review_id=self.id, vote_type=vote_type)
            db.session.add(new_vote)
            if vote_type == 'up':
                self.upvotes += 1
            else:
                self.downvotes += 1
        
        db.session.commit()

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_anonymous = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=False)
    upvotes = db.Column(db.Integer, default=0)
    downvotes = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'))

    def has_voted(self, user, vote_type):
        vote = Vote.query.filter_by(user_id=user.id, review_id=self.id, vote_type=vote_type).first()
        return vote is not None

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    review_id = db.Column(db.Integer, db.ForeignKey('review.id'))
    vote_type = db.Column(db.String(4))