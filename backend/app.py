from flask import Flask
from config import Config
from extensions import db
from models import User, Exercise, Meal, Workout, UserProfile, WorkoutExercise, FoodItem, MealFood, Goal, ProgressLog
from sqlalchemy import text
from flask import request, jsonify
from werkzeug.security import check_password_hash  # optional if you store hashed passwords
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)

    # Create tables (if they don’t already exist)
    with app.app_context():
        db.create_all()

    return app

app = create_app()

@app.route('/test_db')
def test_db():
    try:
        result = db.session.execute(text('SELECT 1'))
        return "Database connection successful!"
    except Exception as e:
        return f"Database connection failed: {e}"

@app.route('/')
def home():
    return "Welcome to the HealthCare App API!"

@app.route('/users')
def get_users():
    users = User.query.all()
    user_list = []
    for user in users:
        user_list.append({
            "id": user.user_id,
            "username": user.username,
            "email": user.email,
            "age": user.age,
            "gender": user.gender
        })
    return {"users": user_list}

# Enable CORS for frontend to talk to Flask
CORS(app)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Missing email or password"}), 400

    # Find user in database
    user = User.query.filter_by(email=email).first()

    if user and password == user.password: 
        # Example: check_password_hash(user.password, password)
        return jsonify({
            "message": "Login successful",
            "user": {
                "id": user.user_id,
                "username": user.username,
                "email": user.email,
                "age": user.age
            }
        }), 200
    else:
        return jsonify({"message": "Invalid email or password"}), 401
    
if __name__ == "__main__":
    app.run(debug=True)