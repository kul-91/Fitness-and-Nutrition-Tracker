// src/pages/Dashboard.js
import React, { useEffect, useState } from "react";

function Dashboard() {
  const stored = localStorage.getItem("user");
  const storedUser = stored ? JSON.parse(stored) : null;

  const [user, setUser] = useState(storedUser);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [showWorkoutForm, setShowWorkoutForm] = useState(false);
  const [showMealForm, setShowMealForm] = useState(false);
// Multi-exercise workout
  const [workoutForm, setWorkoutForm] = useState({
  workout_type: "",
  workout_date: new Date().toISOString().slice(0, 10),
  exercises: [{ exercise_name: "", duration_min: "" }]
  });

  const [expandedWorkout, setExpandedWorkout] = useState(null);

  const toggleWorkoutExpand = (id) => {
    setExpandedWorkout(expandedWorkout === id ? null : id);
  };


  const [mealForm, setMealForm] = useState({
    meal_type: "",
    meal_date: new Date().toISOString().slice(0, 10),
    foods: [
      { food_name: "", quantity: 1 }
    ]
  });

  const updateFood = (index, field, value) => {
    const updated = [...mealForm.foods];
    updated[index][field] = value;
    setMealForm({ ...mealForm, foods: updated });
  };

  useEffect(() => {
    if (!user) {
      window.location.href = "/login";
      return;
    }

    const controller = new AbortController();

    fetch(`http://localhost:5000/api/user/${user.id}/summary`, {
      signal: controller.signal,
    })
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch summary");
        return res.json();
      })
      .then((data) => {
        setSummary(data);

        if (data.user) {
          localStorage.setItem("user", JSON.stringify(data.user));
          setUser(data.user);
        }
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));

    return () => controller.abort();
  }, [user]);

  const handleLogout = () => {
    localStorage.removeItem("user");
    window.location.href = "/login";
  };

  // Submit new workout
  const handleAddWorkout = async () => {
    const validExercises = workoutForm.exercises.filter(
      ex => ex.exercise_name.trim() !== "" && ex.duration_min !== ""
    );

    if (validExercises.length === 0) {
      return alert("Please add at least one exercise.");
    }

    const payload = {
      workout_type: workoutForm.workout_type,   // ADD THIS
      workout_date: workoutForm.workout_date,
      exercises: validExercises.map(ex => ({
        exercise_name: ex.exercise_name,
        duration_min: parseInt(ex.duration_min)
      }))
    };


    try {
      const res = await fetch(
        `http://localhost:5000/api/user/${user.id}/workouts`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        }
      );

      if (!res.ok) throw new Error("Failed to add workout");

      const newSummary = await fetch(
        `http://localhost:5000/api/user/${user.id}/summary`
      ).then(r => r.json());

      setSummary(newSummary);
      setShowWorkoutForm(false);

      // Reset form
      setWorkoutForm({
        workout_type: "",
        workout_date: new Date().toISOString().slice(0, 10),
        exercises: [{ exercise_name: "", duration_min: "" }]
      });


    } catch (error) {
      alert(error.message);
    }
  };

  const updateExercise = (index, field, value) => {
  const updated = [...workoutForm.exercises];
  updated[index][field] = value;
  setWorkoutForm({ ...workoutForm, exercises: updated });
};

const addExerciseRow = () => {
  setWorkoutForm({
    ...workoutForm,
    exercises: [...workoutForm.exercises, { exercise_name: "", duration_min: "" }]
  });
};

const removeExerciseRow = (index) => {
  const updated = workoutForm.exercises.filter((_, i) => i !== index);
  setWorkoutForm({ ...workoutForm, exercises: updated });
};

  const addFoodRow = () => {
  setMealForm({
      ...mealForm,
      foods: [...mealForm.foods, { food_name: "", quantity: 1 }]
    });
  };

  const removeFoodRow = (index) => {
    const updated = mealForm.foods.filter((_, i) => i !== index);
    setMealForm({ ...mealForm, foods: updated });
  };

  const handleAddMeal = async () => {
    if (!mealForm.meal_type) {
      return alert("Select meal type");
    }

    const payload = {
      meal_type: mealForm.meal_type,
      meal_date: mealForm.meal_date,
      foods: mealForm.foods
        .filter(f => f.food_name.trim() !== "") // ignore empty rows
        .map(f => ({
            food_name: f.food_name,
            quantity: parseFloat(f.quantity)
        }))
    };

    try {
      const res = await fetch(
        `http://localhost:5000/api/user/${user.id}/meals`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        }
      );

      if (!res.ok) throw new Error("Failed to add meal");

      const updated = await fetch(
        `http://localhost:5000/api/user/${user.id}/summary`
      ).then((r) => r.json());

      setSummary(updated);
      setShowMealForm(false);

      // Reset
      setMealForm({
        meal_type: "",
        meal_date: new Date().toISOString().slice(0, 10),
        foods: [{ food_name: "", quantity: 1 }]
      });

    } catch (error) {
      alert(error.message);
    }
  };


  if (!user) return null;

  return (
    <div className="container mt-4">
      {/* Header */}
      <div className="d-flex justify-content-between align-items-center">
        <h2 className="text-primary">Welcome, {user.username}</h2>
        <div>
          <button
            className="btn btn-outline-secondary me-2"
            onClick={handleLogout}
          >
            Logout
          </button>
          <button
            className="btn btn-primary"
            onClick={() => setShowWorkoutForm(true)}
          >
            Add Workout
          </button>
          <button 
          className="btn btn-success ms-2" 
          onClick={() => setShowMealForm(true)}
        >
          Add Meal
        </button>
        </div>
      </div>

      {loading && <div className="mt-4">Loading dashboard...</div>}
      {error && <div className="alert alert-danger mt-4">{error}</div>}

      {/* Workout Form */}
{showWorkoutForm && (
  <div className="card p-3 mt-4 shadow">
    <h5>Add Workout</h5>

    <div className="mb-3">
      <label>Workout Type</label>
      <input
        type="text"
        className="form-control"
        placeholder="Push Day / Leg Day / Cardio"
        value={workoutForm.workout_type}
        onChange={(e) =>
          setWorkoutForm({ ...workoutForm, workout_type: e.target.value })
        }
      />
    </div>

    <div className="mb-3">
      <label>Date</label>
      <input
        type="date"
        className="form-control"
        value={workoutForm.workout_date}
        onChange={(e) =>
          setWorkoutForm({ ...workoutForm, workout_date: e.target.value })
        }
      />
    </div>

    <h6>Exercises</h6>

    {workoutForm.exercises.map((ex, index) => (
      <div key={index} className="row mb-2">
        <div className="col-md-5">
          <input
            type="text"
            className="form-control"
            placeholder="Exercise name"
            value={ex.exercise_name}
            onChange={(e) => updateExercise(index, "exercise_name", e.target.value)}
          />
        </div>

        <div className="col-md-3">
          <input
            type="number"
            className="form-control"
            placeholder="Duration"
            value={ex.duration_min}
            onChange={(e) => updateExercise(index, "duration_min", e.target.value)}
          />
        </div>

        <div className="col-md-2">
          <button
            className="btn btn-danger"
            onClick={() => removeExerciseRow(index)}
            disabled={workoutForm.exercises.length === 1}
          >
            X
          </button>
        </div>
      </div>
    ))}

    <button className="btn btn-secondary mb-3" onClick={addExerciseRow}>
      + Add Exercise
    </button>

    <button className="btn btn-success me-2" onClick={handleAddWorkout}>
      Save Workout
    </button>

    <button
      className="btn btn-outline-secondary"
      onClick={() => setShowWorkoutForm(false)}
    >
      Cancel
    </button>
  </div>
)}



    {showMealForm && (
      <div className="card p-3 mt-4 shadow">
        <h5>Add Meal</h5>

        <div className="mb-3">
          <label>Meal Type</label>
          <input
            className="form-control"
            value={mealForm.meal_type}
            onChange={(e) =>
              setMealForm({ ...mealForm, meal_type: e.target.value })
            }
            placeholder="Breakfast / Lunch / Dinner"
          />
        </div>

        <h6>Food Items</h6>

        {mealForm.foods.map((item, index) => (
          <div key={index} className="row mb-2">
            <div className="col-md-5">
              <input
                type="text"
                className="form-control"
                placeholder="Food name"
                value={item.food_name}
                onChange={(e) => updateFood(index, "food_name", e.target.value)}
              />
            </div>

            <div className="col-md-3">
              <input
                type="number"
                className="form-control"
                placeholder="Qty"
                value={item.quantity}
                onChange={(e) => updateFood(index, "quantity", e.target.value)}
              />
            </div>

            <div className="col-md-2">
              <button
                className="btn btn-danger"
                onClick={() => removeFoodRow(index)}
                disabled={mealForm.foods.length === 1}
              >
                X
              </button>
            </div>
          </div>
        ))}

        <button className="btn btn-secondary mb-3" onClick={addFoodRow}>
          + Add More Food
        </button>

        <br />

        <button className="btn btn-success me-2" onClick={handleAddMeal}>
          Save Meal
        </button>

        <button
          className="btn btn-outline-secondary"
          onClick={() => setShowMealForm(false)}
        >
          Cancel
        </button>
      </div>
    )}




      {/* Summary Cards */}
      {summary && (
        <>
          <div className="row mt-4">
            <div className="col-md-3">
              <div className="card p-3">
                <h6>Calories In</h6>
                <p className="h4">{summary.calories_in ?? "—"}</p>
              </div>
            </div>

            <div className="col-md-3">
              <div className="card p-3">
                <h6>Calories Out</h6>
                <p className="h4">{summary.calories_out ?? "—"}</p>
              </div>
            </div>

            <div className="col-md-3">
              <div className="card p-3">
                <h6>BMI</h6>
                <p className="h4">{summary.bmi ?? "—"}</p>
              </div>
            </div>

            <div className="col-md-3">
              <div className="card p-3">
                <h6>Joined</h6>
                <p className="h6">
                  {user.join_date
                    ? new Date(user.join_date).toLocaleDateString()
                    : "—"}
                </p>
              </div>
            </div>
          </div>

          {/* Meals & Workouts */}
          <div className="row mt-4">
            <div className="col-md-6">
              <h5>Recent Meals</h5>
              <div className="card p-3">
                {summary.recent_meals.length === 0 ? (
                  <p className="text-muted">No meals logged yet.</p>
                ) : (
                  <table className="table table-sm">
                    <thead>
                      <tr>
                        <th>Date</th>
                        <th>Type</th>
                        <th>Food</th>
                        <th>Qty</th>
                        <th>Calories</th>
                      </tr>
                    </thead>
                    <tbody>
                      {summary.recent_meals.map((m, idx) => (
                        <tr key={idx}>
                          <td>{m.meal_date}</td>
                          <td>{m.meal_type}</td>
                          <td>{m.food_name}</td>
                          <td>{m.quantity}</td>
                          <td>{m.calories_total}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            </div>

            <div className="col-md-6">
              <h5>Recent Workouts</h5>
              <div className="card p-3">
                {summary.recent_workouts.length === 0 ? (
                  <p className="text-muted">No workouts logged yet.</p>
                ) : (
                  <table className="table table-sm">
                    <thead>
                      <tr>
                        <th>Date</th>
                        <th>Type</th>
                        <th>Duration</th>
                        <th>Calories</th>
                      </tr>
                    </thead>
                    <tbody>
                      {summary.recent_workouts.map((w) => (
                        <tr key={w.workout_id}>
                          <td>{w.workout_date}</td>
                          <td>
                            <button
                              className="btn btn-link p-0"
                              onClick={() => toggleWorkoutExpand(w.workout_id)}
                            >
                              {w.workout_type}
                            </button>

                            {expandedWorkout === w.workout_id && (
                              <ul>
                                {w.exercises && w.exercises.length > 0 && w.exercises.map((ex, i) => (
                                  <li key={i}>
                                    {ex.exercise_name} — {ex.duration_min} min
                                  </li>
                                ))}
                              </ul>
                            )}
                          </td>

                          <td>{w.duration_min}</td>
                          <td>{w.total_calories_burned}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            </div>
          </div>

          {/* Profile section */}
          <div className="row mt-4">
            <div className="col-md-6">
              <h5>Profile</h5>
              <div className="card p-3">
                <p><strong>Name:</strong> {user.username}</p>
                <p><strong>Email:</strong> {user.email}</p>
                <p><strong>Age:</strong> {user.age ?? "—"}</p>
                <p><strong>Gender:</strong> {user.gender ?? "—"}</p>
                <p><strong>Height (cm):</strong> {user.height_cm ?? "—"}</p>
                <p><strong>Weight (kg):</strong> {user.weight_kg ?? "—"}</p>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default Dashboard;
