import {

  createContext,

  useContext,

  useEffect,

  useState

} from "react";


// ─────────────────────────────────────────────
// CREATE CONTEXT
// ─────────────────────────────────────────────

const AuthContext = createContext();


// ─────────────────────────────────────────────
// PROVIDER
// ─────────────────────────────────────────────

export function AuthProvider({

  children

}) {

  // ─────────────────────────
  // STATES
  // ─────────────────────────

  const [user, setUser] = useState(null);

  const [token, setToken] = useState(null);

  const [loading, setLoading] = useState(true);


  // ─────────────────────────
  // LOAD USER FROM LOCAL STORAGE
  // ─────────────────────────

  useEffect(() => {

    try {

      const storedToken =
        localStorage.getItem("token");

      const storedUser =
        localStorage.getItem("user");

      // IF TOKEN + USER EXISTS
      if (storedToken && storedUser) {

        setToken(storedToken);

        setUser(
          JSON.parse(storedUser)
        );
      }

    } catch (error) {

      console.error(
        "Auth Load Error:",
        error
      );

      // CLEAR CORRUPTED DATA
      localStorage.removeItem("token");

      localStorage.removeItem("user");
    }

    setLoading(false);

  }, []);


  // ─────────────────────────
  // LOGIN FUNCTION
  // ─────────────────────────

  const login = (

    userData,

    tokenData

  ) => {

    // SAVE TOKEN
    localStorage.setItem(

      "token",

      tokenData
    );

    // SAVE USER
    localStorage.setItem(

      "user",

      JSON.stringify(userData)
    );

    // UPDATE STATE
    setToken(tokenData);

    setUser(userData);
  };


  // ─────────────────────────
  // LOGOUT FUNCTION
  // ─────────────────────────

  const logout = () => {

    // REMOVE STORAGE
    localStorage.removeItem(
      "token"
    );

    localStorage.removeItem(
      "user"
    );

    // CLEAR STATES
    setUser(null);

    setToken(null);
  };


  // ─────────────────────────
  // CONTEXT VALUE
  // ─────────────────────────

  const value = {

    user,

    token,

    loading,

    login,

    logout,

    isAuthenticated:
      !!token
  };


  // ─────────────────────────
  // PROVIDER
  // ─────────────────────────

  return (

    <AuthContext.Provider
      value={value}
    >

      {children}

    </AuthContext.Provider>
  );
}


// ─────────────────────────────────────────────
// CUSTOM HOOK
// ─────────────────────────────────────────────

export function useAuth() {

  return useContext(
    AuthContext
  );
}