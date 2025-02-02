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
    password_hash = db.Column(db.String(128))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_verified = db.Column(db.Boolean, default=False)
    reviews = db.relationship("Review", back_populates="user", foreign_keys="Review.user_id")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Unit(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    faculty = db.Column(db.String(255), nullable=False)
    credit_points = db.Column(db.Integer, nullable=False)
    url = db.Column(db.String(500), nullable=False)
    upvotes = db.Column(db.Integer, default=0, nullable=False)
    downvotes = db.Column(db.Integer, default=0, nullable=False)

    @property
    def total_votes(self):
        return self.upvotes + self.downvotes
    
    reviews = db.relationship('Review', back_populates="unit", lazy='dynamic')
    def vote(self, user, vote_type):
        existing_vote = Vote.query.filter_by(
            user_id=user.id, unit_id=self.id).first()
        
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
            new_vote = Vote(user_id=user.id, unit_id=self.id, vote_type=vote_type)
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
    upvotes = db.Column(db.Integer, default=0)
    downvotes = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'), nullable=False)

    user = db.relationship("User", back_populates="reviews", foreign_keys=[user_id])
    unit = db.relationship("Unit", back_populates="reviews")


    def has_voted(self, user, vote_type):
        if not user.is_authenticated:
            return False
        vote = Vote.query.filter_by(
            user_id=user.id,
            review_id=self.id,
            vote_type=vote_type
        ).first()
        return vote is not None

    def get_vote_status(self, user):
        if not user.is_authenticated:
            return None
        vote = Vote.query.filter_by(
            user_id=user.id,
            review_id=self.id
        ).first()
        return vote.vote_type if vote else None

    def can_edit(self, user):
        if not user.is_authenticated:
            return False
        return user.id == self.user_id # or user.is_admin
    
class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'), nullable=True)  # Allow voting for units
    review_id = db.Column(db.Integer, db.ForeignKey('review.id'), nullable=True)
    vote_type = db.Column(db.String(4), nullable=False)  # 'up' or 'down'

    __table_args__ = (db.UniqueConstraint('user_id', 'review_id'),)

class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    unit_code = db.Column(db.String(20), db.ForeignKey('unit.code'), nullable=False)
    number = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    weight = db.Column(db.Integer, nullable=False)

    unit = db.relationship("Unit", backref=db.backref("assessments", lazy=True))