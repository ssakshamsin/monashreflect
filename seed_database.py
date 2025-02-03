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
    
    if not assessment_summary or "No assessment data available" in assessment_summary:
        return assessments

    # Try extracting detailed assessments first
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
    
    # If no structured assessments were found, check for a single summary
    if not assessments:
        match = re.search(r"(\d+)%\s*(.*)", assessment_summary)
        if match:
            weight, name = match.groups()
            assessments.append({
                "number": 1,  # Default to 1 since no explicit numbering
                "name": name.strip(),
                "weight": 100  # Default to 100% if no weight specified
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
            password_hash=generate_password_hash('password123'),
            is_verified=True,
            is_admin=False
        )
        db.session.add(user)
        user2 = User(
            username='pikabro',
            password_hash=generate_password_hash('RedGreenBlue(22)'),
            is_verified=True,
            is_admin=True
        )
        db.session.add(user2)
        
        user3 = User(
            username='comingthruu',
            password_hash=generate_password_hash('RedGreenBlue(22)'),
            is_verified=True,
            is_admin=True
        )
        db.session.add(user3)
        db.session.commit()

if __name__ == '__main__':
    seed_database()
    print("Database seeded successfully!")