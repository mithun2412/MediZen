import { motion } from "framer-motion";

import {

  ShieldCheck

} from "lucide-react";


export default function AdherenceCard({

  adherence = 84,
}) {

  return (

    <motion.div

      whileHover={{

        y: -5,
      }}

      className="bg-white/5 border border-white/10 rounded-[32px] p-8 backdrop-blur-2xl"
    >

      <div className="flex items-center gap-5">

        <div className="w-16 h-16 rounded-3xl bg-emerald-400 flex items-center justify-center">

          <ShieldCheck className="text-black w-8 h-8" />

        </div>

        <div>

          <h3 className="text-slate-400">

            Adherence Score

          </h3>

          <h2 className="text-5xl font-black mt-2">

            {adherence}%

          </h2>

        </div>

      </div>

    </motion.div>
  );
}