// src/pages/Dashboard.jsx
import React, { useEffect, useState } from "react";

function Dashboard() {
  const stored = localStorage.getItem("user");
  const storedUser = stored ? JSON.parse(stored) : null;
  const [user, setUser] = useState(storedUser);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // quick state for creating demo workout
  const [addingWorkout, setAddingWorkout] = useState(false);

  useEffect(() => {
    if (!user) {
      window.location.href = "/login";
      return;
    }
    const controller = new AbortController();
    fetch(`http://localhost:5000/api/user/${user.id}/summary`, { signal: controller.signal })
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch summary");
        return res.json();
      })
      .then((data) => {
        setSummary(data);
        // update local stored user (in case profile fields updated)
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

  const handleAddDemoWorkout = async () => {
    if (!user) return;
    setAddingWorkout(true);
    try {
      const payload = {
        workout_date: new Date().toISOString().slice(0, 10),
        workout_type: "Quick Cardio",
        duration_min: 20,
        total_calories_burned: 150
      };
      const res = await fetch(`http://localhost:5000/api/user/${user.id}/workouts`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(payload)
      });
      if (!res.ok) throw new Error("Failed to add workout");
      // refresh summary
      const s = await fetch(`http://localhost:5000/api/user/${user.id}/summary`);
      const data = await s.json();
      setSummary(data);
    } catch (err) {
      alert(err.message);
    } finally {
      setAddingWorkout(false);
    }
  }

  if (!user) return null; // redirect handled above

  return (
    <div className="container mt-4">
      <div className="d-flex justify-content-between align-items-center">
        <h2 className="text-primary">Welcome, {user.username}</h2>
        <div>
          <button className="btn btn-outline-secondary me-2" onClick={handleLogout}>Logout</button>
          <button className="btn btn-primary" onClick={handleAddDemoWorkout} disabled={addingWorkout}>
            {addingWorkout ? "Adding..." : "Add Quick Workout"}
          </button>
        </div>
      </div>

      {loading && <div className="mt-4">Loading dashboard...</div>}
      {error && <div className="alert alert-danger mt-4">{error}</div>}

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
                <p className="h6">{user.join_date ? new Date(user.join_date).toLocaleDateString() : "—"}</p>
              </div>
            </div>
          </div>

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
                        <th>Date</th><th>Type</th><th>Food</th><th>Qty</th><th>Calories</th>
                      </tr>
                    </thead>
                    <tbody>
                      {summary.recent_meals.map((m, i) => (
                        <tr key={i}>
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
                      <tr><th>Date</th><th>Type</th><th>Duration</th><th>Calories</th></tr>
                    </thead>
                    <tbody>
                      {summary.recent_workouts.map((w) => (
                        <tr key={w.workout_id}>
                          <td>{w.workout_date}</td>
                          <td>{w.workout_type}</td>
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

            <div className="col-md-6">
              <h5>Progress (Recent)</h5>
              <div className="card p-3">
                {summary && summary.user ? (
                  <p className="text-muted">See detailed progress page for charts (soon).</p>
                ) : <p>No progress data.</p>}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default Dashboard;
