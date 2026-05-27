import { motion } from "framer-motion";

import {

  Send,

  Mic,

  Sparkles

} from "lucide-react";
import VoiceControls from "./VoiceControls";


export default function ChatInput({

  input,

  setInput,

  onSend

}) {

  // ─────────────────────────
  // ENTER SEND
  // ─────────────────────────

  const handleKeyDown = (e) => {

    if (

      e.key === "Enter" &&

      !e.shiftKey
    ) {

      e.preventDefault();

      onSend();
    }
  };


  return (

    <div className="border-t border-white/10 bg-black/40 backdrop-blur-2xl px-6 py-5">

      <div className="max-w-6xl mx-auto">

        <motion.div

          initial={{

            opacity: 0,

            y: 20,
          }}

          animate={{

            opacity: 1,

            y: 0,
          }}

          className="relative bg-white/5 border border-white/10 rounded-[32px] overflow-hidden shadow-[0_0_40px_rgba(0,255,255,0.05)]"
        >

          {/* GLOW */}

          <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/5 via-transparent to-emerald-500/5 pointer-events-none" />


          {/* INPUT ROW */}

          <div className="flex items-end gap-4 p-4">

            {/* AI ICON */}

            <div className="hidden md:flex w-14 h-14 rounded-2xl bg-cyan-400 items-center justify-center shrink-0 shadow-xl">

              <Sparkles className="text-black w-7 h-7" />

            </div>


            {/* TEXTAREA */}

            <div className="flex-1">

              <textarea

                value={input}

                onChange={(e) =>

                  setInput(
                    e.target.value
                  )
                }

                onKeyDown={handleKeyDown}

                rows={1}

                placeholder="Describe your symptoms, upload reports, or ask healthcare questions..."

                className="w-full resize-none bg-transparent text-white placeholder:text-slate-500 outline-none text-[16px] leading-7 max-h-40 overflow-y-auto py-3"
              />

            </div>


            {/* VOICE CONTROLS */}

<VoiceControls

  setInput={setInput}

  autoSend={false}

  onSend={onSend}
/>

            {/* SEND */}

            <motion.button

              whileHover={{

                scale: 1.05,
              }}

              whileTap={{

                scale: 0.95,
              }}

              onClick={onSend}

              disabled={!input.trim()}

              className="w-14 h-14 rounded-2xl bg-cyan-400 hover:bg-cyan-300 disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center transition shadow-[0_0_30px_rgba(0,255,255,0.3)]"
            >

              <Send className="text-black w-6 h-6" />

            </motion.button>

          </div>


          {/* FOOTER */}

          <div className="px-6 pb-4 flex items-center justify-between text-xs text-slate-500">

            <p>

              MediZen AI may generate inaccurate medical information.
              Always consult healthcare professionals.

            </p>

            <p className="hidden md:block">

              Press Enter ↵ to send

            </p>

          </div>

        </motion.div>

      </div>

    </div>
  );
}