import { motion } from "framer-motion";

import { useState } from "react";

import {

  saveHealthHistory

} from "../../api/api";

import {

  BrainCircuit,

  User,

  Volume2,

  Download,

  MapPin,

  ShieldAlert,

  HeartPulse,

  Save,

  FileText,

} from "lucide-react";


export default function MessageBubble({

  msg,

  severityConfig,

  speak,

}) {

  const [saving, setSaving] =
    useState(false);


  // ─────────────────────────────
  // SEVERITY STYLE
  // ─────────────────────────────

  const severityStyle =

    severityConfig?.[
      msg.severity
    ] ||

    severityConfig?.Low;


  // ─────────────────────────────
  // SAVE HISTORY
  // ─────────────────────────────

  const handleSave = async () => {

    try {

      setSaving(true);

      await saveHealthHistory({

        user_id: 1,

        symptom:
          msg.content,

        severity:
          msg.severity ||

          "Low",

        report:
          msg.content,

        pdf_url:
          msg.pdfUrl || "",
      });

      alert(
        "Healthcare report saved successfully."
      );

    } catch (err) {

      console.log(err);

      alert(
        "Failed to save healthcare history."
      );

    } finally {

      setSaving(false);
    }
  };


  return (

    <motion.div

      initial={{

        opacity: 0,

        y: 20,
      }}

      animate={{

        opacity: 1,

        y: 0,
      }}

      transition={{

        duration: 0.3,
      }}

      className={`flex ${

        msg.role === "user"

          ? "justify-end"

          : "justify-start"
      }`}
    >

      {/* BUBBLE */}

      <div

        className={`

          max-w-5xl

          rounded-[32px]

          p-6

          border

          shadow-2xl

          backdrop-blur-2xl

          relative

          overflow-hidden

          ${

            msg.role === "user"

              ? "bg-cyan-400 text-black border-cyan-300"

              : "bg-white/5 border-white/10 text-white"
          }
        `}
      >

        {/* GLOW */}

        {msg.role === "assistant" && (

          <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 via-transparent to-emerald-500/5 pointer-events-none" />

        )}


        {/* HEADER */}

        <div className="flex items-start justify-between gap-4 mb-5 relative z-10">

          {/* LEFT */}

          <div className="flex items-center gap-4">

            {/* AVATAR */}

            <div

              className={`

                w-14

                h-14

                rounded-3xl

                flex

                items-center

                justify-center

                shadow-xl

                ${

                  msg.role === "user"

                    ? "bg-black/10"

                    : "bg-cyan-400"
                }
              `}
            >

              {msg.role === "user" ? (

                <User className="w-7 h-7" />

              ) : (

                <BrainCircuit className="text-black w-7 h-7" />

              )}

            </div>


            {/* TITLE */}

            <div>

              <h3 className="font-black text-xl">

                {msg.role === "user"

                  ? "You"

                  : "MediZen AI"}

              </h3>

              <p

                className={`text-sm mt-1 ${

                  msg.role === "user"

                    ? "text-black/70"

                    : "text-slate-400"
                }`}
              >

                {msg.role === "user"

                  ? "Healthcare Query"

                  : "AI-generated healthcare analysis"}

              </p>

            </div>

          </div>


          {/* ACTIONS */}

          {msg.role === "assistant" && (

            <div className="flex items-center gap-3">

              {/* SPEAK */}

              <motion.button

                whileHover={{

                  scale: 1.05,
                }}

                whileTap={{

                  scale: 0.95,
                }}

                onClick={() =>
                  speak(msg.content)
                }

                className="w-12 h-12 rounded-2xl bg-white/5 hover:bg-white/10 border border-white/10 flex items-center justify-center transition"
              >

                <Volume2 className="w-5 h-5 text-cyan-300" />

              </motion.button>


              {/* SAVE */}

              <motion.button

                whileHover={{

                  scale: 1.05,
                }}

                whileTap={{

                  scale: 0.95,
                }}

                onClick={handleSave}

                disabled={saving}

                className="w-12 h-12 rounded-2xl bg-white/5 hover:bg-white/10 border border-white/10 flex items-center justify-center transition disabled:opacity-50"
              >

                <Save className="w-5 h-5 text-emerald-300" />

              </motion.button>

            </div>
          )}

        </div>


        {/* SEVERITY */}

        {msg.severity && (

          <div

            className={`

              inline-flex

              items-center

              gap-3

              px-5

              py-3

              rounded-2xl

              text-sm

              font-bold

              mb-6

              border

              border-white/10

              ${severityStyle.bg}

              ${severityStyle.text}
            `}
          >

            <ShieldAlert className="w-5 h-5" />

            <span>

              {msg.severity} Severity

            </span>

          </div>
        )}


        {/* IMAGE */}

        {msg.image && (

          <div className="mb-6">

            <img

              src={msg.image}

              alt="medical-upload"

              className="rounded-3xl border border-white/10 max-h-[400px] object-cover shadow-2xl"
            />

          </div>
        )}


        {/* OCR */}

        {msg.extracted_text && (

          <div className="mb-6 bg-black/20 border border-white/10 rounded-3xl p-5">

            <div className="flex items-center gap-3 mb-4">

              <FileText className="text-cyan-300 w-5 h-5" />

              <h3 className="font-bold text-lg">

                OCR Extracted Text

              </h3>

            </div>

            <div className="text-slate-300 whitespace-pre-wrap leading-8 text-[15px]">

              {msg.extracted_text}

            </div>

          </div>
        )}


        {/* CONTENT */}

        <div

          className={`

            whitespace-pre-wrap

            leading-9

            text-[15px]

            relative

            z-10

            ${

              msg.role === "user"

                ? "text-black"

                : "text-slate-100"
            }
          `}
        >

          {msg.content}

        </div>


        {/* HOSPITALS */}

        {msg.hospitals?.length > 0 && (

          <div className="mt-8">

            <div className="flex items-center gap-3 mb-5">

              <HeartPulse className="text-red-300 w-6 h-6" />

              <h3 className="font-black text-xl">

                Nearby Hospitals

              </h3>

            </div>


            <div className="grid md:grid-cols-2 gap-4">

              {msg.hospitals.map(

                (hospital, index) => (

                  <motion.div

                    key={index}

                    whileHover={{

                      scale: 1.02,
                    }}

                    className="bg-white/5 border border-white/10 rounded-3xl p-5 backdrop-blur-xl"
                  >

                    <h4 className="font-black text-lg text-cyan-300">

                      {hospital.name}

                    </h4>

                    <div className="flex items-start gap-3 mt-4 text-slate-300">

                      <MapPin className="w-5 h-5 mt-1 shrink-0" />

                      <span>

                        {hospital.address}

                      </span>

                    </div>


                    <a

                      href={hospital.map_link}

                      target="_blank"

                      rel="noreferrer"

                      className="inline-flex items-center gap-3 mt-6 bg-cyan-400 hover:bg-cyan-300 text-black font-black px-5 py-3 rounded-2xl transition"
                    >

                      <MapPin className="w-5 h-5" />

                      Open Maps

                    </a>

                  </motion.div>
                )
              )}

            </div>

          </div>
        )}


        {/* PDF */}

        {msg.pdfUrl && (

          <motion.a

            whileHover={{

              scale: 1.02,
            }}

            whileTap={{

              scale: 0.98,
            }}

            href={`http://127.0.0.1:8000${msg.pdfUrl}`}

            target="_blank"

            rel="noreferrer"

            className="inline-flex items-center gap-4 mt-8 bg-cyan-400 hover:bg-cyan-300 text-black font-black px-6 py-4 rounded-3xl transition shadow-[0_0_30px_rgba(0,255,255,0.25)]"
          >

            <Download className="w-6 h-6" />

            Download AI Healthcare Report

          </motion.a>
        )}

      </div>

    </motion.div>
  );
}