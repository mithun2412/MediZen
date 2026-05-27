import { motion } from "framer-motion";

import {

  Brain

} from "lucide-react";


export default function StressCard({

  stressLevel = "Moderate",
}) {

  const colors = {

    Low: "bg-emerald-400",

    Moderate: "bg-yellow-400",

    High: "bg-red-400",
  };


  return (

    <motion.div

      whileHover={{

        y: -5,
      }}

      className="bg-white/5 border border-white/10 rounded-[32px] p-8 backdrop-blur-2xl"
    >

      <div className="flex items-center gap-5">

        <div

          className={`

            w-16

            h-16

            rounded-3xl

            flex

            items-center

            justify-center

            ${

              colors[
                stressLevel
              ]
            }
          `}
        >

          <Brain className="text-black w-8 h-8" />

        </div>

        <div>

          <h3 className="text-slate-400">

            Stress Level

          </h3>

          <h2 className="text-4xl font-black mt-2">

            {stressLevel}

          </h2>

        </div>

      </div>

    </motion.div>
  );
}