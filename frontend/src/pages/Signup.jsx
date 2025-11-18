import React, { useState } from "react";

function Signup() {
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    age: "",
    gender: "",
    height_cm: "",
    weight_kg: ""
  });

  const [error, setError] = useState("");

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    setError("");

    const res = await fetch("http://localhost:5000/signup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
    });

    const data = await res.json();

    if (!res.ok) {
      setError(data.message || "Signup failed");
      return;
    }

    alert("Signup successful! Please login.");
    window.location.href = "/login";
  };

  return (
    <div className="container mt-5" style={{ maxWidth: "450px" }}>
      <h3 className="text-center text-primary">Create Account</h3>

      <form onSubmit={handleSignup}>
        <div className="form-group mt-3">
          <label>Username</label>
          <input className="form-control" name="username"
            value={form.username} onChange={handleChange} required />
        </div>

        <div className="form-group mt-3">
          <label>Email</label>
          <input className="form-control" type="email" name="email"
            value={form.email} onChange={handleChange} required />
        </div>

        <div className="form-group mt-3">
          <label>Password</label>
          <input className="form-control" type="password" name="password"
            value={form.password} onChange={handleChange} required />
        </div>

        <div className="form-group mt-3">
          <label>Age</label>
          <input className="form-control" type="number" name="age"
            value={form.age} onChange={handleChange} required />
        </div>

        <div className="form-group mt-3">
          <label>Gender</label>
          <select className="form-control" name="gender"
            value={form.gender} onChange={handleChange} required>
            <option value="">Select</option>
            <option value="Male">Male</option>
            <option value="Female">Female</option>
          </select>
        </div>

        <div className="form-group mt-3">
          <label>Height (cm)</label>
          <input className="form-control" type="number" name="height_cm"
            value={form.height_cm} onChange={handleChange} required />
        </div>

        <div className="form-group mt-3">
          <label>Weight (kg)</label>
          <input className="form-control" type="number" name="weight_kg"
            value={form.weight_kg} onChange={handleChange} required />
        </div>

        {error && <div className="alert alert-danger mt-3">{error}</div>}

        <button className="btn btn-primary w-100 mt-4" type="submit">
          Sign Up
        </button>
      </form>

      <p className="text-center mt-3">
        Already have an account?{" "}
        <a href="/login" className="text-decoration-none">Login</a>
      </p>
    </div>
  );
}

export default Signup;
