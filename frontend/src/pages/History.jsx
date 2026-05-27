import { useEffect, useState } from "react";

import { motion } from "framer-motion";

import {

  History as HistoryIcon,

  Download,

  CalendarDays,

  ShieldAlert,

  FileText,

  Search,

  Trash2,

  BrainCircuit,

  HeartPulse,

} from "lucide-react";

import {

  getHealthHistory

} from "../api/api";

import {

  useAuth

} from "../context/AuthContext";


// ─────────────────────────────────────────────
// SEVERITY COLORS
// ─────────────────────────────────────────────

const severityStyles = {

  Low: {

    bg: "bg-emerald-500/10",

    text: "text-emerald-300",
  },

  Moderate: {

    bg: "bg-yellow-500/10",

    text: "text-yellow-300",
  },

  High: {

    bg: "bg-red-500/10",

    text: "text-red-300",
  },
};


export default function History() {

  const { user } = useAuth();

  const [history, setHistory] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [search, setSearch] =
    useState("");


  // ─────────────────────────────
  // FETCH HISTORY
  // ─────────────────────────────

  useEffect(() => {

    fetchHistory();

  }, []);


  const fetchHistory = async () => {

    try {

      setLoading(true);

      // API CALL
      const response =
        await getHealthHistory(1);

      setHistory(
        response.data || []
      );

    } catch (err) {

      console.log(err);

    } finally {

      setLoading(false);
    }
  };


  // ─────────────────────────────
  // FILTERED DATA
  // ─────────────────────────────

  const filteredHistory =
    history.filter((item) =>

      item.symptom
        ?.toLowerCase()
        .includes(
          search.toLowerCase()
        )
    );


  return (

    <div className="min-h-screen bg-black text-white overflow-hidden relative">

      {/* BACKGROUND */}

      <div className="absolute inset-0">

        <div className="absolute top-[-120px] left-[-100px] w-[420px] h-[420px] bg-cyan-500/20 blur-[120px] rounded-full" />

        <div className="absolute bottom-[-180px] right-[-120px] w-105 h-[420px] bg-emerald-500/20 blur-[120px] rounded-full" />

      </div>


      {/* GRID */}

      <div className="absolute inset-0 opacity-10 bg-[linear-gradient(to_right,#ffffff10_1px,transparent_1px),linear-gradient(to_bottom,#ffffff10_1px,transparent_1px)] bg-[size:60px_60px]" />


      {/* CONTENT */}

      <div className="relative z-10 max-w-7xl mx-auto px-8 py-12">

        {/* HEADER */}

        <motion.div

          initial={{

            opacity: 0,

            y: 20,
          }}

          animate={{

            opacity: 1,

            y: 0,
          }}

          className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-8"
        >

          {/* LEFT */}

          <div>

            <div className="inline-flex items-center gap-3 px-5 py-3 rounded-2xl bg-cyan-400/10 border border-cyan-400/20 text-cyan-300 font-bold">

              <HistoryIcon className="w-5 h-5" />

              Healthcare Conversation History

            </div>


            <h1 className="text-6xl font-black mt-8">

              Medical History

            </h1>


            <p className="text-slate-400 text-xl leading-9 mt-6 max-w-3xl">

              Access previous AI healthcare conversations,
              downloadable reports, OCR analyses,
              and persistent adherence tracking.

            </p>

          </div>


          {/* USER */}

          <div className="bg-white/5 border border-white/10 rounded-4xl p-8 backdrop-blur-2xl min-w-[320px]">

            <div className="flex items-center gap-5">

              <div className="w-16 h-16 rounded-3xl bg-cyan-400 flex items-center justify-center">

                <HeartPulse className="text-black w-8 h-8" />

              </div>

              <div>

                <h3 className="text-2xl font-black">

                  {user?.name}

                </h3>

                <p className="text-slate-400 mt-1">

                  {user?.email}

                </p>

              </div>

            </div>

          </div>

        </motion.div>


        {/* SEARCH */}

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

            delay: 0.1,
          }}

          className="mt-12 relative"
        >

          <Search className="absolute left-5 top-5 text-slate-500 w-5 h-5" />

          <input

            type="text"

            placeholder="Search symptoms, reports, or healthcare conversations..."

            value={search}

            onChange={(e) =>
              setSearch(
                e.target.value
              )
            }

            className="w-full bg-white/5 border border-white/10 rounded-[28px] pl-14 pr-6 py-5 outline-none focus:border-cyan-400 transition text-white placeholder:text-slate-500"
          />

        </motion.div>


        {/* LOADING */}

        {loading && (

          <div className="flex justify-center mt-24">

            <div className="animate-pulse text-cyan-300 text-xl font-bold">

              Loading healthcare history...

            </div>

          </div>
        )}


        {/* EMPTY */}

        {!loading &&

          filteredHistory.length === 0 && (

            <motion.div

              initial={{

                opacity: 0,
              }}

              animate={{

                opacity: 1,
              }}

              className="mt-24 bg-white/5 border border-white/10 rounded-[40px] p-16 text-center backdrop-blur-2xl"
            >

              <div className="w-28 h-28 rounded-[40px] bg-cyan-400 mx-auto flex items-center justify-center shadow-[0_0_50px_rgba(0,255,255,0.2)]">

                <BrainCircuit className="text-black w-14 h-14" />

              </div>

              <h2 className="text-4xl font-black mt-10">

                No Healthcare History

              </h2>

              <p className="text-slate-400 text-xl mt-6 max-w-2xl mx-auto leading-9">

                Your AI healthcare conversations,
                OCR analyses, and medical reports
                will appear here once saved.

              </p>

            </motion.div>
          )}


        {/* HISTORY GRID */}

        <div className="grid xl:grid-cols-2 gap-8 mt-12">

          {filteredHistory.map(

            (item, index) => {

              const style =

                severityStyles[
                  item.severity
                ] ||

                severityStyles.Low;

              return (

                <motion.div

                  key={index}

                  initial={{

                    opacity: 0,

                    y: 20,
                  }}

                  animate={{

                    opacity: 1,

                    y: 0,
                  }}

                  transition={{

                    delay:
                      index * 0.05,
                  }}

                  whileHover={{

                    y: -6,
                  }}

                  className="group bg-white/5 hover:bg-white/[0.07] border border-white/10 hover:border-cyan-400/30 rounded-[36px] p-8 backdrop-blur-2xl transition-all duration-300 overflow-hidden relative"
                >

                  {/* GLOW */}

                  <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition bg-gradient-to-br from-cyan-500/10 via-transparent to-emerald-500/10 pointer-events-none" />


                  {/* TOP */}

                  <div className="relative z-10 flex items-start justify-between gap-5">

                    {/* LEFT */}

                    <div className="flex items-center gap-5">

                      <div className="w-16 h-16 rounded-3xl bg-cyan-400 flex items-center justify-center shadow-xl">

                        <FileText className="text-black w-8 h-8" />

                      </div>

                      <div>

                        <h3 className="text-2xl font-black">

                          {item.symptom}

                        </h3>

                        <div className="flex items-center gap-3 mt-3 text-slate-400">

                          <CalendarDays className="w-4 h-4" />

                          <span>

                            {

                              item.created_at
                            }

                          </span>

                        </div>

                      </div>

                    </div>


                    {/* SEVERITY */}

                    <div

                      className={`

                        inline-flex

                        items-center

                        gap-3

                        px-5

                        py-3

                        rounded-2xl

                        border

                        border-white/10

                        font-bold

                        ${style.bg}

                        ${style.text}
                      `}
                    >

                      <ShieldAlert className="w-5 h-5" />

                      {item.severity}

                    </div>

                  </div>


                  {/* REPORT */}

                  <div className="relative z-10 mt-8 text-slate-300 leading-8 whitespace-pre-wrap">

                    {item.report}

                  </div>


                  {/* ACTIONS */}

                  <div className="relative z-10 flex flex-wrap gap-4 mt-10">

                    {/* DOWNLOAD */}

                    {item.pdf_url && (

                      <motion.a

                        whileHover={{

                          scale: 1.03,
                        }}

                        whileTap={{

                          scale: 0.97,
                        }}

                        href={`http://127.0.0.1:8000${item.pdf_url}`}

                        target="_blank"

                        rel="noreferrer"

                        className="inline-flex items-center gap-3 bg-cyan-400 hover:bg-cyan-300 text-black font-black px-6 py-4 rounded-2xl transition shadow-[0_0_30px_rgba(0,255,255,0.2)]"
                      >

                        <Download className="w-5 h-5" />

                        Download Report

                      </motion.a>
                    )}


                    {/* DELETE */}

                    <motion.button

                      whileHover={{

                        scale: 1.03,
                      }}

                      whileTap={{

                        scale: 0.97,
                      }}

                      className="inline-flex items-center gap-3 bg-red-500/10 hover:bg-red-500/20 border border-red-500/20 text-red-300 font-bold px-6 py-4 rounded-2xl transition"
                    >

                      <Trash2 className="w-5 h-5" />

                      Delete

                    </motion.button>

                  </div>

                </motion.div>
              );
            }

          )}

        </div>

      </div>

    </div>
  );
}