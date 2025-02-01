import json
from app import create_app, db
from app.models import User, Unit, Review, Assessment
from datetime import datetime
from werkzeug.security import generate_password_hash
import re

with open("monash_units_updated.json", "r") as f:
    units_data = json.load(f)


def parse_assessments(assessment_summary):
    """Parses assessment_summary into structured data."""
    assessments = []
    if assessment_summary and "No assessment data available" not in assessment_summary:
        parts = assessment_summary.split("; ")
        for part in parts:
            match = re.match(r"(\d+)\s*-\s*(.*?)\((\d+)%\)", part)
            if match:
                number, name, weight = match.groups()
                assessments.append({
                    "number": int(number),
                    "name": name.strip(),
                    "weight": int(weight)
                })
    return assessments

def seed_database():
    app = create_app()
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
    
        for unit in units_data:

            if "unit" not in unit["url"]:
                print(f"Skipping non-unit entry: {unit['code']} ({unit['url']})")
                continue  
            
            new_unit = Unit(
                code=unit["code"],
                name=unit["name"],
                faculty=unit["faculty"],
                credit_points=unit["credit_points"],
                url=unit["url"]
            )
            db.session.add(new_unit)
            db.session.flush()  # Get unit ID before committing
            
            # Process assessments
            assessments = parse_assessments(unit.get("assessment_summary", ""))
            for assessment in assessments:
                new_assessment = Assessment(
                    unit_code=new_unit.code,
                    number=assessment["number"],
                    name=assessment["name"],
                    weight=assessment["weight"]
                )
                db.session.add(new_assessment)
        
        # Create a sample user
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('password123'),
            is_verified=True
        )
        db.session.add(user)
        
        # Create sample reviews
        reviews = [
            Review(
                content='Great introductory unit! The concepts were well explained.',
                rating=5,
                timestamp=datetime.utcnow(),
                user_id=1,
                unit_id=1,
                is_approved=True
            ),
            Review(
                content='Challenging but rewarding. Good foundation for advanced topics.',
                rating=4,
                timestamp=datetime.utcnow(),
                user_id=1,
                unit_id=2,
                is_approved=True
            )
        ]
        db.session.add_all(reviews)
        
        db.session.commit()

if __name__ == '__main__':
    seed_database()
    print("Database seeded successfully!")