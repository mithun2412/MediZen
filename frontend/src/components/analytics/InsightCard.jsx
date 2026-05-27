import { motion } from "framer-motion";

import {

  BrainCircuit

} from "lucide-react";


export default function InsightCard({

  insight,
}) {

  return (

    <motion.div

      whileHover={{

        y: -4,
      }}

      className="bg-white/5 border border-white/10 rounded-[28px] p-6 backdrop-blur-2xl"
    >

      <div className="flex items-start gap-4">

        <div className="w-14 h-14 rounded-2xl bg-purple-400 flex items-center justify-center shrink-0">

          <BrainCircuit className="text-black w-7 h-7" />

        </div>

        <div>

          <h3 className="font-black text-xl">

            AI Insight

          </h3>

          <p className="text-slate-300 leading-8 mt-3">

            {insight}

          </p>

        </div>

      </div>

    </motion.div>
  );
}