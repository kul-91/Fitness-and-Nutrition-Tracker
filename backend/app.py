from flask import Flask
from config import Config
from extensions import db
from models import User, Exercise, Meal, Workout, UserProfile, WorkoutExercise, FoodItem, MealFood, Goal, ProgressLog
from sqlalchemy import text, func
from flask import request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash  # optional if you store hashed passwords
from flask_cors import CORS
from datetime import date
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

# Helper: serialize Decimal/Numeric to python native types
def numeric_to_native(value):
    if value is None:
        return None
    try:
        return float(value)
    except Exception:
        return value

def serialize_user(u: User):
    return {
        "id": u.user_id,
        "username": u.username,
        "email": u.email,
        "age": u.age,
        "gender": u.gender,
        "height_cm": numeric_to_native(u.height_cm),
        "weight_kg": numeric_to_native(u.weight_kg),
        "join_date": u.join_date.isoformat() if u.join_date else None
    }

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
    hashed_pw = generate_password_hash(password)

    if not email or not password:
        return jsonify({"message": "Missing email or password"}), 400

    # Find user in database
    user = User.query.filter_by(email=email).first()
    user.password = hashed_pw
    if user and check_password_hash(user.password, password): 
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
    
# Get current user by id (front sends id in query or path)
@app.route('/api/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    return jsonify({"user": serialize_user(user)}), 200

# Get summary for dashboard (calories in/out today, recent meals/workouts)
@app.route('/api/user/<int:user_id>/summary', methods=['GET'])
def user_summary(user_id):
    # Today's date filtering can be added; here we return aggregate numbers
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    # Total calories_in/out from progress_log latest entry
    today = date.today()
    calories_out = (db.session.query(
        func.sum(Workout.total_calories_burned)
    ).filter(Workout.user_id == user_id)
     .filter(Workout.workout_date == today)
     .scalar() ) or 0
    # Total calories in: we keep progress log or calculate from meals
    calories_in = db.session.query(
        func.sum(MealFood.calories_total)
    ).join(Meal, MealFood.meal_id == Meal.meal_id)\
    .filter(Meal.user_id == user_id)\
    .scalar() or 0

    
    # Recent meals (last 5)
    recent_meals = (
        db.session.query(Meal, MealFood, FoodItem)
        .join(MealFood, Meal.meal_id == MealFood.meal_id)
        .join(FoodItem, MealFood.food_id == FoodItem.food_id)
        .filter(Meal.user_id == user_id)
        .order_by(Meal.meal_date.desc())
        .limit(10)
        .all()
    )
    meals_list = []
    for meal, mealfood, food in recent_meals:
        meals_list.append({
            "meal_id": meal.meal_id,
            "meal_date": meal.meal_date.isoformat() if meal.meal_date else None,
            "meal_type": meal.meal_type,
            "food_name": food.food_name,
            "quantity": float(mealfood.quantity) if mealfood.quantity is not None else None,
            "calories_total": float(mealfood.calories_total) if mealfood.calories_total is not None else None
        })

    # Recent workouts (last 10)
    recent_workouts = Workout.query.filter_by(user_id=user_id).order_by(Workout.workout_date.desc()).limit(10).all()
    workouts_list = []
    for w in recent_workouts:
        workouts_list.append({
            "workout_id": w.workout_id,
            "workout_date": w.workout_date.isoformat() if w.workout_date else None,
            "workout_type": w.workout_type,
            "duration_min": w.duration_min,
            "total_calories_burned": numeric_to_native(w.total_calories_burned)
        })

    # Basic BMI calculation if height and weight present
    bmi = None
    if user.height_cm and user.weight_kg:
        try:
            height_m = float(user.height_cm) / 100.0
            bmi = round(float(user.weight_kg) / (height_m * height_m), 2)
        except Exception:
            bmi = None

    return jsonify({
        "user": serialize_user(user),
        "calories_in": calories_in,
        "calories_out": calories_out,
        "bmi": bmi,
        "recent_meals": meals_list,
        "recent_workouts": workouts_list
    }), 200

# Endpoint to add a meal (simple)
@app.route('/api/user/<int:user_id>/meals', methods=['POST'])
def add_meal(user_id):
    payload = request.get_json() or {}
    meal_type = payload.get('meal_type')
    meal_date = payload.get('meal_date')  # expect 'YYYY-MM-DD'
    foods = payload.get('foods', [])  # list of {food_id, quantity, calories_total}
    if not meal_date or not foods:
        return jsonify({"message": "Provide meal_date and foods"}), 400

    m = Meal(user_id=user_id, meal_date=meal_date, meal_type=meal_type, total_calories=sum([f.get('calories_total',0) for f in foods]))
    db.session.add(m)
    db.session.commit()

    for f in foods:
        mf = MealFood(meal_id=m.meal_id, food_id=f['food_id'], quantity=f.get('quantity', 1), calories_total=f.get('calories_total', 0))
        db.session.add(mf)
    db.session.commit()
    return jsonify({"message": "Meal created", "meal_id": m.meal_id}), 201

# Endpoint to add a workout
@app.route('/api/user/<int:user_id>/workouts', methods=['POST'])
def add_workout(user_id):
    payload = request.get_json() or {}
    workout_date = payload.get('workout_date')
    workout_type = payload.get('workout_type')
    duration_min = payload.get('duration_min')
    calories = payload.get('total_calories_burned', 0)

    w = Workout(user_id=user_id, workout_date=workout_date, workout_type=workout_type, duration_min=duration_min, total_calories_burned=calories)
    db.session.add(w)
    db.session.commit()
    return jsonify({"message": "Workout created", "workout_id": w.workout_id}), 201

# Endpoint to get progress logs
@app.route('/api/user/<int:user_id>/progress', methods=['GET'])
def get_progress(user_id):
    logs = ProgressLog.query.filter_by(user_id=user_id).order_by(ProgressLog.log_date.asc()).all()
    out = []
    for l in logs:
        out.append({
            "log_id": l.log_id,
            "log_date": l.log_date.isoformat() if l.log_date else None,
            "weight_kg": numeric_to_native(l.weight_kg),
            "bmi": numeric_to_native(l.bmi),
            "body_fat_percent": numeric_to_native(l.body_fat_percent),
            "calories_in": l.calories_in,
            "calories_out": l.calories_out
        })
    return jsonify({"progress": out}), 200

if __name__ == "__main__":
    app.run(debug=True)