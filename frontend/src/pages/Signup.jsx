import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import api from "../api/api";

function Signup() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
  });

  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const handleSignup = async (e) => {
    e.preventDefault();

    try {
      setLoading(true);

      await api.post(
        "/auth/signup",
        form
      );

      alert("Account created successfully ✅");

      navigate("/login");

    } catch (err) {
      console.error(err);

      alert(
        err.response?.data?.detail ||
        "Signup failed"
      );

    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 flex items-center justify-center px-4 overflow-hidden">

      {/* Background Glow */}
      <div className="absolute w-[500px] h-[500px] bg-cyan-500/20 blur-3xl rounded-full top-[-100px] right-[-100px]"></div>

      <div className="absolute w-[400px] h-[400px] bg-indigo-500/20 blur-3xl rounded-full bottom-[-100px] left-[-100px]"></div>

      {/* Signup Card */}
      <div className="relative z-10 w-full max-w-md">

        <div className="bg-white/5 backdrop-blur-2xl border border-white/10 shadow-2xl rounded-[40px] p-10">

          {/* Logo */}
          <div className="text-center mb-10">

            <div className="w-20 h-20 mx-auto rounded-3xl bg-cyan-500 flex items-center justify-center text-black text-4xl font-black shadow-2xl shadow-cyan-500/40 mb-5">
              M
            </div>

            <h1 className="text-4xl font-black text-white">
              MediZen AI
            </h1>

            <p className="text-slate-400 mt-3 text-lg">
              Create your healthcare account
            </p>

          </div>

          {/* Form */}
          <form onSubmit={handleSignup}>

            {/* Name */}
            <div className="mb-5">

              <label className="text-slate-300 text-sm font-semibold block mb-2">
                Full Name
              </label>

              <input
                type="text"
                name="name"
                placeholder="Enter your full name"
                value={form.name}
                onChange={handleChange}
                required
                className="w-full bg-white/5 border border-white/10 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-500/30 outline-none rounded-2xl px-5 py-4 text-white placeholder-slate-500 transition"
              />

            </div>

            {/* Email */}
            <div className="mb-5">

              <label className="text-slate-300 text-sm font-semibold block mb-2">
                Email Address
              </label>

              <input
                type="email"
                name="email"
                placeholder="Enter your email"
                value={form.email}
                onChange={handleChange}
                required
                className="w-full bg-white/5 border border-white/10 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-500/30 outline-none rounded-2xl px-5 py-4 text-white placeholder-slate-500 transition"
              />

            </div>

            {/* Password */}
            <div className="mb-8">

              <label className="text-slate-300 text-sm font-semibold block mb-2">
                Password
              </label>

              <input
                type="password"
                name="password"
                placeholder="Create a secure password"
                value={form.password}
                onChange={handleChange}
                required
                className="w-full bg-white/5 border border-white/10 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-500/30 outline-none rounded-2xl px-5 py-4 text-white placeholder-slate-500 transition"
              />

            </div>

            {/* Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-cyan-500 hover:bg-cyan-400 text-black font-black py-4 rounded-2xl text-lg transition shadow-2xl shadow-cyan-500/30"
            >
              {loading ? "Creating Account..." : "Create Account"}
            </button>

          </form>

          {/* Bottom */}
          <div className="mt-8 text-center text-slate-400">

            Already have an account?

            <Link
              to="/login"
              className="text-cyan-400 hover:text-cyan-300 font-bold ml-2"
            >
              Sign In
            </Link>

          </div>

          {/* Feature Cards */}
          <div className="mt-10 grid grid-cols-3 gap-4">

            <div className="bg-white/5 border border-white/10 rounded-2xl p-4 text-center">
              <div className="text-2xl mb-2">
                🧠
              </div>

              <p className="text-xs text-slate-400">
                AI Analysis
              </p>
            </div>

            <div className="bg-white/5 border border-white/10 rounded-2xl p-4 text-center">
              <div className="text-2xl mb-2">
                💊
              </div>

              <p className="text-xs text-slate-400">
                Smart Tracking
              </p>
            </div>

            <div className="bg-white/5 border border-white/10 rounded-2xl p-4 text-center">
              <div className="text-2xl mb-2">
                🏥
              </div>

              <p className="text-xs text-slate-400">
                Hospital Finder
              </p>
            </div>

          </div>

        </div>

      </div>

    </div>
  );
}

export default Signup;