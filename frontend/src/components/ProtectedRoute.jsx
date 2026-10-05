import { Navigate } from "react-router-dom";

function ProtectedRoute({ children, adminOnly = false }) {
  const token = localStorage.getItem("token");
  const role = localStorage.getItem("role");

  // User is not logged in
  if (!token) {
    return <Navigate to="/login" replace />;
  }

  // Page is only for admin
  if (adminOnly && role !== "ADMIN") {
    return <Navigate to="/products" replace />;
  }

  return children;
}

export default ProtectedRoute;