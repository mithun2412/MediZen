import {

  BrowserRouter,

  Routes,

  Route,

  Navigate,

} from "react-router-dom";

import Login from "./pages/Login";

import Signup from "./pages/Signup";

import Dashboard from "./pages/Dashboard";

import ChatPage from "./pages/ChatPage";

import History from "./pages/History";

import Analytics from "./pages/Analytics";

import MedicineReminder from "./pages/MedicineReminder";

import ProtectedRoute from "./components/layout/ProtectedRoute";

import {

  AuthProvider

} from "./context/AuthContext";


export default function App() {

  return (

    <BrowserRouter>

      <AuthProvider>

        <Routes>

          {/* LOGIN */}

          <Route

            path="/login"

            element={<Login />}
          />


          {/* SIGNUP */}

          <Route

            path="/signup"

            element={<Signup />}
          />


          {/* DASHBOARD */}

          <Route

            path="/dashboard"

            element={

              <ProtectedRoute>

                <Dashboard />

              </ProtectedRoute>
            }
          />


          {/* CHAT */}

          <Route

            path="/chat"

            element={

              <ProtectedRoute>

                <ChatPage />

              </ProtectedRoute>
            }
          />


          {/* HISTORY */}

          <Route

            path="/history"

            element={

              <ProtectedRoute>

                <History />

              </ProtectedRoute>
            }
          />


          {/* ANALYTICS */}

          <Route

            path="/analytics"

            element={

              <ProtectedRoute>

                <Analytics />

              </ProtectedRoute>
            }
          />


          {/* REMINDERS */}

          <Route

            path="/reminders"

            element={

              <ProtectedRoute>

                <MedicineReminder />

              </ProtectedRoute>
            }
          />


          {/* DEFAULT */}

          <Route

            path="*"

            element={

              <Navigate

                to="/login"
              />
            }
          />

        </Routes>

      </AuthProvider>

    </BrowserRouter>
  );
}