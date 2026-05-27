import { useState } from "react";

import { Link, useNavigate } from "react-router-dom";

import { motion } from "framer-motion";

import {

  User,

  Mail,

  Lock,

  HeartPulse,

  Shield,

  BrainCircuit

} from "lucide-react";

import { signupUser } from "../api/api";

import { useAuth } from "../context/AuthContext";


export default function Signup() {

  const navigate = useNavigate();

  const { login } = useAuth();

  const [form, setForm] = useState({

    name: "",

    email: "",

    password: "",
  });

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");


  // ─────────────────────────
  // HANDLE INPUT
  // ─────────────────────────

  const handleChange = (e) => {

    setForm({

      ...form,

      [e.target.name]: e.target.value,
    });
  };


  // ─────────────────────────
  // HANDLE SIGNUP
  // ─────────────────────────

  const handleSignup = async (e) => {

    e.preventDefault();

    setLoading(true);

    setError("");

    try {

      const res = await signupUser(form);

      const data = res.data;

      // SAVE LOGIN
      login(

        data.access_token,

        {

          name: data.user_name,

          email: data.user_email,
        }
      );

      navigate("/dashboard");

    } catch (err) {

      console.log(err);

      setError(

        err?.response?.data?.detail ||

        "Signup failed. Please try again."
      );

    } finally {

      setLoading(false);
    }
  };


  return (

    <div className="min-h-screen bg-black text-white overflow-hidden relative flex items-center justify-center px-6">

      {/* BACKGROUND */}

      <div className="absolute inset-0">

        <div className="absolute top-[-150px] left-[-100px] w-[400px] h-[400px] bg-cyan-500/20 blur-[120px] rounded-full" />

        <div className="absolute bottom-[-180px] right-[-120px] w-[420px] h-[420px] bg-purple-500/20 blur-[120px] rounded-full" />

      </div>


      {/* GRID */}

      <div className="absolute inset-0 opacity-10 bg-[linear-gradient(to_right,#ffffff10_1px,transparent_1px),linear-gradient(to_bottom,#ffffff10_1px,transparent_1px)] bg-[size:60px_60px]" />


      {/* MAIN CARD */}

      <motion.div

        initial={{ opacity: 0, y: 40 }}

        animate={{ opacity: 1, y: 0 }}

        transition={{ duration: 0.7 }}

        className="relative z-10 w-full max-w-6xl grid lg:grid-cols-2 overflow-hidden rounded-[40px] border border-white/10 bg-white/5 backdrop-blur-2xl shadow-[0_0_80px_rgba(0,255,255,0.08)]"
      >

        {/* LEFT PANEL */}

        <div className="hidden lg:flex flex-col justify-between p-14 border-r border-white/10 bg-gradient-to-br from-cyan-500/10 to-transparent">

          <div>

            <div className="flex items-center gap-4">

              <div className="w-16 h-16 rounded-3xl bg-cyan-400 flex items-center justify-center shadow-2xl">

                <HeartPulse className="text-black w-8 h-8" />

              </div>

              <div>

                <h1 className="text-4xl font-black">

                  MediZen AI

                </h1>

                <p className="text-slate-400 mt-1">

                  Next-Generation Healthcare Intelligence

                </p>

              </div>

            </div>


            <div className="mt-16 space-y-8">

              <div className="flex gap-4">

                <div className="w-14 h-14 rounded-2xl bg-cyan-500/10 border border-cyan-400/20 flex items-center justify-center">

                  <BrainCircuit className="text-cyan-300" />

                </div>

                <div>

                  <h3 className="font-bold text-xl">

                    AI Clinical Conversations

                  </h3>

                  <p className="text-slate-400 mt-2 leading-7">

                    Context-aware healthcare conversations powered by multimodal AI reasoning.

                  </p>

                </div>

              </div>


              <div className="flex gap-4">

                <div className="w-14 h-14 rounded-2xl bg-emerald-500/10 border border-emerald-400/20 flex items-center justify-center">

                  <Shield className="text-emerald-300" />

                </div>

                <div>

                  <h3 className="font-bold text-xl">

                    Secure Health Intelligence

                  </h3>

                  <p className="text-slate-400 mt-2 leading-7">

                    Encrypted healthcare records with personalized analytics and adherence tracking.

                  </p>

                </div>

              </div>

            </div>

          </div>


          <div className="text-sm text-slate-500">

            © 2026 MediZen AI Platform

          </div>

        </div>


        {/* RIGHT PANEL */}

        <div className="p-8 md:p-14 flex flex-col justify-center">

          <motion.div

            initial={{ opacity: 0, x: 30 }}

            animate={{ opacity: 1, x: 0 }}

            transition={{ delay: 0.2 }}
          >

            <div className="mb-10">

              <h2 className="text-4xl font-black">

                Create Account

              </h2>

              <p className="text-slate-400 mt-3 text-lg">

                Start your intelligent healthcare journey.

              </p>

            </div>


            {/* ERROR */}

            {error && (

              <div className="mb-6 bg-red-500/10 border border-red-500/20 text-red-300 p-4 rounded-2xl">

                {error}

              </div>
            )}


            {/* FORM */}

            <form

              onSubmit={handleSignup}

              className="space-y-6"
            >

              {/* NAME */}

              <div>

                <label className="text-sm text-slate-400 mb-2 block">

                  Full Name

                </label>

                <div className="relative">

                  <User className="absolute left-4 top-4 text-slate-500 w-5 h-5" />

                  <input

                    type="text"

                    name="name"

                    value={form.name}

                    onChange={handleChange}

                    required

                    placeholder="Enter your full name"

                    className="w-full bg-white/5 border border-white/10 rounded-2xl pl-12 pr-4 py-4 outline-none focus:border-cyan-400 transition"
                  />

                </div>

              </div>


              {/* EMAIL */}

              <div>

                <label className="text-sm text-slate-400 mb-2 block">

                  Email Address

                </label>

                <div className="relative">

                  <Mail className="absolute left-4 top-4 text-slate-500 w-5 h-5" />

                  <input

                    type="email"

                    name="email"

                    value={form.email}

                    onChange={handleChange}

                    required

                    placeholder="Enter your email"

                    className="w-full bg-white/5 border border-white/10 rounded-2xl pl-12 pr-4 py-4 outline-none focus:border-cyan-400 transition"
                  />

                </div>

              </div>


              {/* PASSWORD */}

              <div>

                <label className="text-sm text-slate-400 mb-2 block">

                  Password

                </label>

                <div className="relative">

                  <Lock className="absolute left-4 top-4 text-slate-500 w-5 h-5" />

                  <input

                    type="password"

                    name="password"

                    value={form.password}

                    onChange={handleChange}

                    required

                    placeholder="Create password"

                    className="w-full bg-white/5 border border-white/10 rounded-2xl pl-12 pr-4 py-4 outline-none focus:border-cyan-400 transition"
                  />

                </div>

              </div>


              {/* BUTTON */}

              <motion.button

                whileHover={{ scale: 1.02 }}

                whileTap={{ scale: 0.98 }}

                disabled={loading}

                className="w-full bg-cyan-400 hover:bg-cyan-300 text-black font-black py-4 rounded-2xl transition shadow-2xl disabled:opacity-50"
              >

                {loading

                  ? "Creating Account..."

                  : "Create MediZen Account"}
              </motion.button>

            </form>


            {/* LOGIN */}

            <div className="mt-8 text-center text-slate-400">

              Already have an account?{" "}

              <Link

                to="/login"

                className="text-cyan-300 font-bold hover:text-cyan-200"
              >

                Login

              </Link>

            </div>

          </motion.div>

        </div>

      </motion.div>

    </div>
  );
}