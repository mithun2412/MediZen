import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import DashboardPreview from "./DashboardPreview";

function HeroSection() {

  return (

    <section className="relative z-10 max-w-7xl mx-auto px-8 py-28 grid lg:grid-cols-2 gap-16 items-center">

      <motion.div
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >

        <div className="inline-flex items-center gap-2 bg-cyan-500/10 border border-cyan-500/30 px-5 py-2 rounded-full text-cyan-300 mb-8 text-sm">

          <span className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse"></span>

          AI-Powered Healthcare Ecosystem

        </div>

        <h1 className="text-7xl lg:text-8xl font-black leading-[0.92] tracking-tight mb-8">

          The Future of

          <span className="block bg-gradient-to-r from-cyan-400 via-blue-400 to-indigo-400 bg-clip-text text-transparent">

            AI Healthcare

          </span>

        </h1>

        <p className="text-slate-300 text-xl leading-relaxed max-w-2xl mb-10">

          Conversational healthcare AI powered by disease prediction,
          medical image analysis, medicine reminders, and personalized
          health insights.

        </p>

        <div className="flex flex-wrap gap-4">

          <Link
            to="/signup"
            className="bg-cyan-500 hover:bg-cyan-400 text-black font-black px-8 py-4 rounded-2xl text-lg transition"
          >
            Launch MediZen
          </Link>

          <Link
            to="/login"
            className="border border-white/15 hover:border-cyan-400 hover:text-cyan-400 px-8 py-4 rounded-2xl text-lg transition"
          >
            Open Dashboard
          </Link>

        </div>

        <div className="flex flex-wrap gap-3 mt-10">

          {[
            "AI Symptom Analysis",
            "Disease Prediction",
            "Medicine Reminders",
            "Health Analytics",
            "Medical Image Analysis",
          ].map((item, i) => (

            <div
              key={i}
              className="bg-white/5 border border-white/10 px-4 py-2 rounded-2xl text-sm text-slate-300"
            >
              {item}
            </div>
          ))}
        </div>

      </motion.div>

      <DashboardPreview />

    </section>
  );
}

export default HeroSection;