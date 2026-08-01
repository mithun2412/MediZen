import { Navigate } from "react-router-dom";

import { useAuth } from "../../context/AuthContext";


export default function ProtectedRoute({

  children

}) {

  const {

    isAuthenticated,

    loading

  } = useAuth();


  // LOADING
  if (loading) {

    return (

      <div className="medivoice-light-theme min-h-screen bg-[#F6F8F7] text-[#12231F] flex items-center justify-center">

        <div className="animate-pulse text-cyan-400 text-xl font-bold">

          Loading MediZen AI...

        </div>

      </div>
    );
  }


  // NOT LOGGED IN
  if (!isAuthenticated) {

    return <Navigate to="/login" replace />;
  }


  // ALLOW ACCESS
  return children;
}
