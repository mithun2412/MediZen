import { motion } from "framer-motion";

import {

  Sparkles

} from "lucide-react";


export default function FollowupOptions({

  options = [],

  onSelect

}) {

  if (!options.length) return null;


  return (

    <motion.div

      initial={{

        opacity: 0,

        y: 10,
      }}

      animate={{

        opacity: 1,

        y: 0,
      }}

      className="ml-2 mt-4 flex flex-wrap gap-3"
    >

      {/* AI LABEL */}

      <div className="w-full flex items-center gap-2 mb-1 text-sm text-cyan-300">

        <Sparkles className="w-4 h-4" />

        <span>

          Suggested responses

        </span>

      </div>


      {/* OPTIONS */}

      {options.map((option, index) => (

        <motion.button

          key={index}

          whileHover={{

            scale: 1.04,

            y: -2,
          }}

          whileTap={{

            scale: 0.96,
          }}

          onClick={() =>
            onSelect(option)
          }

          className="
            px-5
            py-3
            rounded-2xl
            bg-white/5
            hover:bg-cyan-400/10
            border
            border-white/10
            hover:border-cyan-400/30
            text-slate-200
            hover:text-cyan-200
            transition-all
            duration-300
            backdrop-blur-xl
            shadow-lg
            text-sm
            font-medium
          "
        >

          {option}

        </motion.button>
      ))}

    </motion.div>
  );
}