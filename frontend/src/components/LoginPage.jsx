import React, { useState } from "react";

function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  // Handle Login Submission
  const handleLogin = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch("http://localhost:5000/login", {
        method: "POST", // ✅ POST is best for sensitive info
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (response.ok) {
        setMessage("✅ Login successful!");
        localStorage.setItem("user", JSON.stringify(data.user));
        window.location.href = "/dashboard"; // redirect after login
      } else {
        setMessage(`❌ ${data.message}`);
      }
    } catch (error) {
      setMessage("⚠ Error connecting to the server.");
    }
  };

  return (
    <div className="container vh-100 d-flex align-items-center justify-content-center bg-light">
      <div className="card shadow-lg p-4" style={{ maxWidth: "400px", width: "100%" }}>
        <h2 className="text-center mb-3 text-primary fw-bold">
          Fitness & Nutrition Tracker
        </h2>
        <p className="text-center text-muted mb-4">
          Welcome back! Please login to continue.
        </p>

        {/* ✅ FORM SECTION */}
        <form onSubmit={handleLogin}>
          {/* Email Field */}
          <div className="mb-3">
            <label className="form-label fw-semibold">Email address</label>
            <input
              type="email"
              className="form-control"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
            />
          </div>

          {/* Password Field */}
          <div className="mb-3">
            <label className="form-label fw-semibold">Password</label>
            <input
              type="password"
              className="form-control"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
            />
          </div>

          {/* ✅ LOGIN BUTTON — stays inside <form> */}
          <button
            type="submit"
            className="btn btn-primary w-100 fw-semibold"
          >
            Login
          </button>
        </form>

        {/* ✅ Message (feedback for user) */}
        {message && (
          <div className="alert alert-info text-center mt-3 py-2">
            {message}
          </div>
        )}

        {/* Signup Redirect */}
        <p className="text-center mt-3 text-muted">
          Don’t have an account?{" "}
          <a href="/register" className="text-decoration-none text-primary">
            Sign up
          </a>
        </p>
      </div>
    </div>
  );
}

export default LoginPage;