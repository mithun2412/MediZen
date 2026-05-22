import { Routes, Route } from "react-router-dom";

import Home from "./pages/Home";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";
import MedicineReminder from "./pages/MedicineReminder";
import History from "./pages/History";
import ChatPage from "./pages/ChatPage";

import ProtectedRoute from "./components/ProtectedRoute";

export default function App() {
  return (
    <Routes>

      {/* Landing Page */}
      <Route
        path="/"
        element={<Home />}
      />

      {/* Auth Pages */}
      <Route
        path="/login"
        element={<Login />}
      />

      <Route
        path="/signup"
        element={<Signup />}
      />

      {/* Protected Dashboard */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />

      {/* Medicine Reminder */}
      <Route
        path="/reminders"
        element={
          <ProtectedRoute>
            <MedicineReminder />
          </ProtectedRoute>
        }
      />

      {/* History */}
      <Route
        path="/history"
        element={
          <ProtectedRoute>
            <History />
          </ProtectedRoute>
        }
      />

      {/* AI Chat */}
      <Route
        path="/chat"
        element={
          <ProtectedRoute>
            <ChatPage />
          </ProtectedRoute>
        }
      />

    </Routes>
  );
}