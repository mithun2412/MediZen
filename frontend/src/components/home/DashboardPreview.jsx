import { motion } from "framer-motion";

function DashboardPreview() {

  return (

    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 1 }}
      className="relative"
    >

      <div className="absolute inset-0 bg-cyan-500/20 blur-3xl rounded-full"></div>

      <div className="relative bg-white/5 backdrop-blur-2xl border border-white/10 rounded-[40px] p-6 shadow-2xl">

        <div className="flex justify-between items-center mb-8">

          <div>

            <h2 className="text-3xl font-black">
              AI Health Intelligence
            </h2>

            <p className="text-slate-400 mt-1">
              Personalized healthcare monitoring
            </p>

          </div>

          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-cyan-400 to-blue-500 flex items-center justify-center text-black font-black text-xl">
            AI
          </div>

        </div>

        <div className="space-y-4">

          <div className="bg-gradient-to-r from-cyan-500/10 to-indigo-500/10 border border-cyan-500/20 rounded-3xl p-5">

            <div className="flex justify-between mb-3 text-sm">

              <span>Health Score</span>

              <span className="text-cyan-400 font-bold">
                92%
              </span>

            </div>

            <div className="w-full bg-slate-700/40 rounded-full h-3">

              <div className="bg-gradient-to-r from-cyan-500 to-blue-400 h-3 rounded-full w-[92%]"></div>

            </div>

          </div>

          <div className="grid grid-cols-2 gap-3">

            <div className="bg-gradient-to-br from-cyan-500/10 to-cyan-500/5 border border-cyan-500/20 rounded-3xl p-5">

              <p className="text-slate-400 text-xs uppercase mb-2">
                AI Symptom Analysis
              </p>

              <p className="text-2xl font-black text-cyan-400">
                Active
              </p>

              <p className="text-xs text-slate-500 mt-1">
                Conversational assessment
              </p>

            </div>

            <div className="bg-gradient-to-br from-indigo-500/10 to-indigo-500/5 border border-indigo-500/20 rounded-3xl p-5">

              <p className="text-slate-400 text-xs uppercase mb-2">
                Vision AI
              </p>

              <p className="text-2xl font-black text-indigo-400">
                Active
              </p>

              <p className="text-xs text-slate-500 mt-1">
                Medical image analysis
              </p>

            </div>

          </div>

          <div className="bg-white/5 border border-white/10 rounded-3xl p-5">

            <p className="text-xs text-slate-400 uppercase tracking-wider mb-4">
              Core AI Modules
            </p>

            <div className="space-y-3">

              {[
                "Conversational Healthcare AI",
                "Disease Prediction Engine",
                "CNN Medical Vision AI",
                "Medicine Reminder System",
                "Health Analytics",
              ].map((item, i) => (

                <div
                  key={i}
                  className="flex items-center gap-3 text-sm"
                >

                  <span className="w-2 h-2 rounded-full bg-cyan-400"></span>

                  <span className="text-slate-300">
                    {item}
                  </span>

                </div>
              ))}
            </div>

          </div>

        </div>

      </div>

    </motion.div>
  );
}

export default DashboardPreview;