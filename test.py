from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Initialize Flask and SQLAlchemy
app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///C:\\Users\\saksh\\Downloads\\unit_review\\instance\\test.db"  # Path to database file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define a simple model
class TestModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

# Test function to create and insert data
def test_database():
    # Ensure the instance folder exists
    os.makedirs(os.path.join(os.getcwd(), 'instance'), exist_ok=True)
    
    # Create database tables
    db.drop_all()  # Clear any existing tables for a clean test
    db.create_all()

    # Add a test record
    test_record = TestModel(name="Test Entry")
    db.session.add(test_record)
    db.session.commit()

    # Query the database
    results = TestModel.query.all()
    for record in results:
        print(f"ID: {record.id}, Name: {record.name}")

if __name__ == "__main__":
    with app.app_context():
        test_database()
