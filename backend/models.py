from extensions import db

class User(db.Model):
    __tablename__ = 'user'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(50))
    height_cm = db.Column(db.Numeric(5, 2))
    weight_kg = db.Column(db.Numeric(5, 2))
    join_date = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    profile = db.relationship('UserProfile', backref='user', uselist=False)
    workouts = db.relationship('Workout', backref='user', lazy=True)
    meals = db.relationship('Meal', backref='user', lazy=True)
    goals = db.relationship('Goal', backref='user', lazy=True)
    progress_logs = db.relationship('ProgressLog', backref='user', lazy=True)


class UserProfile(db.Model):
    __tablename__ = 'user_profile'

    profile_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    activity_level = db.Column(db.String(50))
    goal_type = db.Column(db.String(50))
    target_weight = db.Column(db.Numeric(5, 2))
    dietary_preference = db.Column(db.String(50))

class Workout(db.Model):
    __tablename__ = 'workout'

    workout_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    workout_date = db.Column(db.Date)
    duration_min = db.Column(db.Integer)
    total_calories_burned = db.Column(db.Numeric(6, 2))
    workout_type = db.Column(db.String(50))
    notes = db.Column(db.String(255))

    exercises = db.relationship('WorkoutExercise', backref='workout', lazy=True)


class Exercise(db.Model):
    __tablename__ = 'exercise'

    exercise_id = db.Column(db.Integer, primary_key=True)
    exercise_name = db.Column(db.String(50))
    category = db.Column(db.String(50))
    muscle_group = db.Column(db.String(50))
    calories_per_min = db.Column(db.Numeric(5, 2))
    difficulty = db.Column(db.String(50))

    workouts = db.relationship('WorkoutExercise', backref='exercise', lazy=True)


class WorkoutExercise(db.Model):
    __tablename__ = 'workout_exercise'

    workout_id = db.Column(db.Integer, db.ForeignKey('workout.workout_id'), primary_key=True)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.exercise_id'), primary_key=True)
    duration_min = db.Column(db.Integer)
    calories_burned = db.Column(db.Numeric(6, 2))
    intensity_level = db.Column(db.String(50))


class Meal(db.Model):
    __tablename__ = 'meal'

    meal_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    meal_date = db.Column(db.Date)
    meal_type = db.Column(db.String(50))
    total_calories = db.Column(db.Numeric(6, 2))
    notes = db.Column(db.String(255))

    foods = db.relationship('MealFood', backref='meal', lazy=True)


class FoodItem(db.Model):
    __tablename__ = 'food_item'

    food_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    food_name = db.Column(db.String(50))
    category = db.Column(db.String(50))
    calories_per_unit = db.Column(db.Numeric(6, 2))
    protein_g = db.Column(db.Numeric(5, 2))
    carbs_g = db.Column(db.Numeric(5, 2))
    fat_g = db.Column(db.Numeric(5, 2))
    unit = db.Column(db.String(50))

    meals = db.relationship('MealFood', backref='food', lazy=True)


class MealFood(db.Model):
    __tablename__ = 'meal_food'

    meal_id = db.Column(db.Integer, db.ForeignKey('meal.meal_id'), primary_key=True)
    food_id = db.Column(db.Integer, db.ForeignKey('food_item.food_id'), primary_key=True)
    quantity = db.Column(db.Numeric(5, 2))
    calories_total = db.Column(db.Numeric(6, 2))


class Goal(db.Model):
    __tablename__ = 'goal'

    goal_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    goal_type = db.Column(db.String(50))
    target_value = db.Column(db.Numeric(6, 2))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    is_achieved = db.Column(db.Boolean, default=False)


class ProgressLog(db.Model):
    __tablename__ = 'progress_log'

    log_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    log_date = db.Column(db.Date)
    weight_kg = db.Column(db.Numeric(5, 2))
    bmi = db.Column(db.Numeric(5, 2))
    body_fat_percent = db.Column(db.Numeric(5, 2))
    calories_in = db.Column(db.Integer)
    calories_out = db.Column(db.Integer)

