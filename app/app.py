from flask import Flask, render_template, request
from flask import Blueprint
from flask import jsonify

# Initialize the Flask app
app = Flask(__name__)

# Create a Blueprint named 'main'
main = Blueprint('main', __name__)

# Mock data for units
UNITS = [
    {"code": "FIT1000", "name": "Introduction to Programming", "description": "Learn the basics of programming.", "faculty": "Faculty of IT"},
    {"code": "FIT1001", "name": "Data Structures", "description": "Study fundamental data structures.", "faculty": "Faculty of IT"},
    {"code": "FIT1002", "name": "Algorithms", "description": "Explore algorithm design and analysis.", "faculty": "Faculty of IT"},
    # Add more units as needed
]


@main.route("/", methods=["GET"])
def landing():
    return render_template("landing.html")

# Home route
@main.route("/units", methods=["GET"])
def home():
    query = request.args.get("query", "").strip().lower()
    if query:
        filtered_units = [unit for unit in UNITS if query in unit["code"].lower() or query in unit["name"].lower()]
    else:
        filtered_units = UNITS
    return render_template("home.html", units=filtered_units)

# Unit detail route
@main.route("/unit/<code>")
def unit(code):
    unit = next((u for u in UNITS if u["code"] == code), None)
    if not unit:
        return "Unit not found", 404
    return render_template("unit.html", unit=unit)

# Register the Blueprint
app.register_blueprint(main)


# this currently does nothing just boilerplate 
@app.route('/unit/<code>/vote', methods=['POST'])
def vote_unit(code):
    data = request.get_json()
    option = data.get('option')

    # Update the vote count in the database
    unit = Unit.query.filter_by(code=code).first_or_404()
    if option == 'good':
        unit.good_votes += 1
    elif option == 'bad':
        unit.bad_votes += 1

    db.session.commit()

    return jsonify({
        'good_votes': unit.good_votes,
        'bad_votes': unit.bad_votes,
        'total_votes': unit.good_votes + unit.bad_votes,
    })

from app import db
from app.models import User, Unit

test_user = User(username='testuser', email='test@example.com')
test_user.set_password('password')
db.session.add(test_user)
db.session.commit()

if __name__ == "__main__":
    app.run(debug=True)