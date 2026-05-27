import { motion } from "framer-motion";

import {

  BrainCircuit

} from "lucide-react";


export default function TypingLoader() {

  return (

    <div className="flex justify-start">

      <motion.div

        initial={{

          opacity: 0,

          y: 20,
        }}

        animate={{

          opacity: 1,

          y: 0,
        }}

        className="max-w-xl bg-white/5 border border-white/10 backdrop-blur-xl rounded-[28px] px-6 py-5 shadow-2xl"
      >

        {/* HEADER */}

        <div className="flex items-center gap-4 mb-5">

          {/* ICON */}

          <div className="w-12 h-12 rounded-2xl bg-cyan-400 flex items-center justify-center shadow-xl">

            <BrainCircuit className="text-black w-6 h-6" />

          </div>


          {/* TEXT */}

          <div>

            <h3 className="font-black text-lg">

              MediZen AI

            </h3>

            <p className="text-slate-400 text-sm">

              Analyzing healthcare context...

            </p>

          </div>

        </div>


        {/* TYPING DOTS */}

        <div className="flex items-center gap-3">

          {[0, 1, 2].map((dot) => (

            <motion.div

              key={dot}

              animate={{

                y: [0, -10, 0],

                opacity: [0.3, 1, 0.3],
              }}

              transition={{

                duration: 0.8,

                repeat: Infinity,

                delay: dot * 0.2,
              }}

              className="w-4 h-4 rounded-full bg-cyan-400 shadow-[0_0_15px_rgba(0,255,255,0.6)]"
            />
          ))}

        </div>


        {/* LOADING BAR */}

        <div className="mt-6 h-2 bg-white/5 rounded-full overflow-hidden">

          <motion.div

            animate={{

              x: ["-100%", "100%"],
            }}

            transition={{

              duration: 1.8,

              repeat: Infinity,

              ease: "linear",
            }}

            className="w-1/3 h-full bg-cyan-400 rounded-full"
          />

        </div>

      </motion.div>

    </div>
  );
}