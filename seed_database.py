from app import create_app, db
from app.models import User, Unit, Review
from datetime import datetime
from werkzeug.security import generate_password_hash

def seed_database():
    app = create_app()
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
    
        # Create sample units
        units = [
            Unit(
                code='COMP1000',
                name='Introduction to Computer Science',
                description='Learn the fundamentals of programming and computer science concepts.',
                faculty='Science and Engineering'
            ),
            Unit(
                code='COMP2000',
                name='Data Structures and Algorithms',
                description='Advanced programming concepts including data structures and algorithms.',
                faculty='Science and Engineering'
            ),
            Unit(
                code='MATH1001',
                name='Calculus I',
                description='Introduction to differential and integral calculus.',
                faculty='Mathematics'
            ),
            Unit(
                code='PHYS1001',
                name='Physics I',
                description='Fundamental concepts in classical mechanics and thermodynamics.',
                faculty='Science'
            )
        ]
        db.session.add_all(units)
        
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