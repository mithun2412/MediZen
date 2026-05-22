import { Link } from "react-router-dom";

function CTASection() {

  return (

    <section className="relative z-10 max-w-7xl mx-auto px-8 pb-24">

      <div className="bg-gradient-to-r from-cyan-500/10 to-indigo-500/10 border border-cyan-500/20 rounded-[40px] p-14 text-center">

        <h2 className="text-5xl font-black mb-5">
          Experience AI Healthcare
        </h2>

        <p className="text-slate-400 text-xl mb-10 max-w-3xl mx-auto">

          Intelligent healthcare assistance powered by conversational AI,
          predictive analytics, medical image analysis, and personalized
          health insights.

        </p>

        <Link
          to="/signup"
          className="inline-block bg-cyan-500 hover:bg-cyan-400 text-black font-black px-10 py-4 rounded-2xl text-lg transition"
        >
          Start Using MediZen →
        </Link>

      </div>

    </section>
  );
}

export default CTASection;