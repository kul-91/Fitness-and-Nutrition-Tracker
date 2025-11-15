import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import LoginPage from "./components/LoginPage";
import Dashboard from "./pages/Dashboard";

import "bootstrap/dist/css/bootstrap.min.css";

function App() {
  return (
    <Router>
      <Routes>

        {/* Default route → Login */}
        <Route path="/" element={<LoginPage />} />

        {/* Login Route */}
        <Route path="/login" element={<LoginPage />} />

        {/* Dashboard Route */}
        <Route path="/dashboard" element={<Dashboard />} />

      </Routes>
    </Router>
  );
}

export default App;
