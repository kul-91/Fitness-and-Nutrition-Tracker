from flask import Flask
from config import Config
from extensions import db
from models import User, Exercise, Meal, Workout, UserProfile, WorkoutExercise, FoodItem, MealFood, Goal, ProgressLog
from sqlalchemy import text, func
from flask import request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash  # optional if you store hashed passwords
from flask_cors import CORS
from datetime import datetime, date, timedelta
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

    if not email or not password:
        return jsonify({"message": "Missing email or password"}), 400

    user = User.query.filter_by(email=email).first()

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

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json() or {}

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    age = data.get('age')
    gender = data.get('gender')
    height_cm = data.get('height_cm')
    weight_kg = data.get('weight_kg')

    if not username or not email or not password or not age or not gender or not height_cm or not weight_kg:
        return jsonify({"message": "All fields are required"}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"message": "Email already registered"}), 409

    hashed_pw = generate_password_hash(password)

    # BMI calculation
    try:
        h = float(height_cm) / 100
        bmi = round(float(weight_kg) / (h * h), 2)
    except:
        bmi = None

    new_user = User(
        username=username,
        email=email,
        password=hashed_pw,
        age=age,
        gender=gender,
        height_cm=height_cm,
        weight_kg=weight_kg,
        join_date=date.today()
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "Signup successful",
        "user": {
            "id": new_user.user_id,
            "username": new_user.username,
            "email": new_user.email,
            "age": new_user.age,
            "gender": new_user.gender,
            "height_cm": new_user.height_cm,
            "weight_kg": new_user.weight_kg,
            "bmi": bmi
        }
    }), 201


# Get summary for dashboard (calories in/out today, recent meals/workouts)
@app.route('/api/user/<int:user_id>/summary', methods=['GET'])
def user_summary(user_id):
    # Today's date filtering can be added; here we return aggregate numbers
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    # Total calories_in/out from progress_log latest entry
    today = date.today()
    calories_in = (
    db.session.query(func.sum(MealFood.calories_total))
    .join(Meal, MealFood.meal_id == Meal.meal_id)
    .filter(Meal.user_id == user_id)
    .filter(Meal.meal_date == today)
    .scalar()
    ) or 0

    calories_out = (
        db.session.query(func.sum(Workout.total_calories_burned))
        .filter(Workout.user_id == user_id)
        .filter(Workout.workout_date == today)
        .scalar()
    ) or 0

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
        exercises = WorkoutExercise.query.filter_by(workout_id=w.workout_id).all()

        exercise_list = []
        for ex in exercises:
            exercise_list.append({
                "exercise_name": ex.exercise.exercise_name,
                "duration_min": ex.duration_min,
                "calories_burned": ex.calories_burned
            })

        workouts_list.append({
            "workout_id": w.workout_id,
            "workout_date": w.workout_date.isoformat() if w.workout_date else None,
            "workout_type": w.workout_type,
            "duration_min": sum(ex.duration_min for ex in exercises),
            "total_calories_burned": numeric_to_native(w.total_calories_burned),
            "exercises": exercise_list      # ADD THIS
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

    meal_type = payload.get("meal_type")
    meal_date = payload.get("meal_date")
    foods = payload.get("foods", [])

    if not meal_type or not meal_date or not foods:
        return jsonify({"message": "Missing fields"}), 400

    total_meal_calories = 0

    # Create meal entry first
    meal = Meal(
        user_id=user_id,
        meal_date=meal_date,
        meal_type=meal_type,
        total_calories=0
    )
    db.session.add(meal)
    db.session.commit()

    for f in foods:
        food_name = f["food_name"]
        quantity = float(f.get("quantity", 1))

        food = FoodItem.query.filter_by(food_name=food_name).first()

        if not food:
            food = FoodItem(
                food_name=food_name,
                category="General",
                calories_per_unit=120,
                protein_g=0,
                carbs_g=0,
                fat_g=0,
                unit="unit"
            )
            db.session.add(food)
            db.session.commit()

        calories_total = float(food.calories_per_unit) * quantity
        total_meal_calories += calories_total

        meal_food = MealFood(
            meal_id=meal.meal_id,
            food_id=food.food_id,
            quantity=quantity,
            calories_total=calories_total
        )
        db.session.add(meal_food)

    meal.total_calories = total_meal_calories
    db.session.commit()

    return jsonify({"message": "Meal added", "meal_id": meal.meal_id}), 201


# Endpoint to add a workout
@app.route('/api/user/<int:user_id>/workouts', methods=['POST'])
def add_workout(user_id):
    payload = request.get_json() or {}

    workout_type = payload.get("workout_type")
    workout_date = payload.get("workout_date")
    exercises = payload.get("exercises", [])

    if not workout_type or not workout_date or len(exercises) == 0:
        return jsonify({"message": "Missing required fields"}), 400

    # Create main workout entry
    workout = Workout(
        user_id=user_id,
        workout_type=workout_type,
        workout_date=datetime.strptime(workout_date, "%Y-%m-%d").date(),
        total_calories_burned=0
    )
    db.session.add(workout)
    db.session.commit()

    total_calories = 0

    for ex in exercises:
        name = ex["exercise_name"]
        duration = int(ex["duration_min"])

        # Check if exercise exists
        exercise = Exercise.query.filter_by(exercise_name=name).first()
        if not exercise:
            exercise = Exercise(
                exercise_name=name,
                category="General",
                muscle_group="General",
                calories_per_min=7.5,  # default
                difficulty="Medium"
            )
            db.session.add(exercise)
            db.session.commit()

        # Calculate calories
        calories = float(exercise.calories_per_min) * duration
        total_calories += calories

        # Link entry
        link = WorkoutExercise(
            workout_id=workout.workout_id,
            exercise_id=exercise.exercise_id,
            duration_min=duration,
            calories_burned=calories,
            intensity_level="Normal"
        )
        db.session.add(link)

    workout.total_calories_burned = total_calories
    db.session.commit()

    return jsonify({
        "message": "Workout added",
        "workout_id": workout.workout_id
    }), 201


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