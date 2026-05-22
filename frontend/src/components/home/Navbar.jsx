import { Link } from "react-router-dom";

function Navbar() {

  return (

    <nav className="sticky top-0 z-50 flex items-center justify-between px-8 py-5 border-b border-white/10 backdrop-blur-xl bg-slate-950/40">

      <div className="flex items-center gap-3">

        <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-cyan-400 to-blue-500 flex items-center justify-center text-black font-black text-xl shadow-2xl shadow-cyan-500/40">
          M
        </div>

        <div>

          <h1 className="text-2xl font-black tracking-wide">
            MediZen AI
          </h1>

          <p className="text-xs text-slate-400 uppercase tracking-[0.25em]">
            Intelligent Healthcare
          </p>

        </div>
      </div>

      <div className="hidden md:flex gap-8 text-slate-300 font-medium">

        <a href="#features" className="hover:text-cyan-400 transition">
          Features
        </a>

        <a href="#ai" className="hover:text-cyan-400 transition">
          AI Workflow
        </a>

      </div>

      <div className="flex gap-3">

        <Link
          to="/login"
          className="border border-white/15 hover:border-cyan-400 hover:text-cyan-400 px-5 py-2.5 rounded-2xl transition font-semibold"
        >
          Login
        </Link>

        <Link
          to="/signup"
          className="bg-cyan-500 hover:bg-cyan-400 text-black font-black px-6 py-2.5 rounded-2xl transition"
        >
          Get Started
        </Link>

      </div>

    </nav>
  );
}

export default Navbar;