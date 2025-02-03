from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from time import time
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlite3 import Connection as SQLite3Connection
import jwt
from flask import current_app, url_for
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable foreign key enforcement for SQLite"""
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_verified = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False)
    reviews = db.relationship("Review", back_populates="user", foreign_keys="Review.user_id")
    profile_pic = db.Column(db.String(120), default='default.jpg')

    login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime)
    
    def validate_password(self, password):
        return len(password)>=7

    def increment_login_attempts(self):
        self.login_attempts += 1
        if self.login_attempts >= 15:  # Lock after 5 failed attempts
            self.locked_until = datetime.utcnow() + timedelta(minutes=15)
        db.session.commit()
    
    def reset_login_attempts(self):
        self.login_attempts = 0
        self.locked_until = None
        db.session.commit()

    def soft_delete(self):
        self.is_deleted = True
        db.session.commit()
        
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_total_votes(self):
        total_upvotes = 0
        total_downvotes = 0
        for review in self.reviews:
            total_upvotes += review.upvotes
            total_downvotes += review.downvotes
        return {
            'upvotes': total_upvotes,
            'downvotes': total_downvotes,
            'total': total_upvotes + total_downvotes
        }

    def get_profile_pic_url(self):
        return url_for('static', filename=f'pictures/{self.profile_pic}')
    
class Unit(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    faculty = db.Column(db.String(255), nullable=False)
    credit_points = db.Column(db.Integer, nullable=False)
    url = db.Column(db.String(500), nullable=False)
    upvotes = db.Column(db.Integer, default=0, nullable=False)
    downvotes = db.Column(db.Integer, default=0, nullable=False)
    assessment_details = db.Column(db.Text)

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
        return user.id == self.user_id or user.is_admin
    
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
    name = db.Column(db.Text, nullable=False)
    weight = db.Column(db.Integer, nullable=False)

    unit = db.relationship("Unit", backref=db.backref("assessments", lazy=True))
