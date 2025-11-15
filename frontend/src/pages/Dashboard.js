import React from "react";

function Dashboard() {
  const user = JSON.parse(localStorage.getItem("user"));

  return (
    <div className="container mt-5">
      <h2 className="text-primary">Welcome, {user.username}!</h2>
      
      <div className="card mt-3 p-3 shadow">
        <h4>User Details</h4>
        <p><strong>User Name:</strong> {user.username}</p>
        <p><strong>Email:</strong> {user.email}</p>
        <p><strong>Age:</strong> {user.age}</p>
      </div>
    </div>
  );
}

export default Dashboard;
