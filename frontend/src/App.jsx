import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import LoginPage from "./components/LoginPage";
import Dashboard from "./pages/Dashboard";

import "bootstrap/dist/css/bootstrap.min.css";
import Signup from "./pages/Signup";

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

      

       <Route path="/signup" element={<Signup />} />


      </Routes>
    </Router>
  );
}

export default App;
