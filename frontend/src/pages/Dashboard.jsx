import { motion } from "framer-motion";

import {

  BrainCircuit,

  FileText,

  Upload,

  HeartPulse,

  ArrowRight,

  History,

  Bell,

  BarChart3,

  Sparkles,

  LogOut,

} from "lucide-react";

import {

  useNavigate

} from "react-router-dom";

import {

  useAuth

} from "../context/AuthContext";


export default function Dashboard() {

  const navigate = useNavigate();

  const {

    user,

    logout

  } = useAuth();


  // ─────────────────────────────
  // FEATURE CARDS
  // ─────────────────────────────

  const cards = [

    {

      title: "AI Health Chat",

      icon: BrainCircuit,

      desc:
        "Conversational healthcare intelligence powered by multimodal AI.",

      route: "/chat",
    },

    {

      title: "Medical OCR",

      icon: Upload,

      desc:
        "Upload blood reports, prescriptions, and medical images for AI analysis.",

      route: "/chat",
    },

    {

      title: "PDF Intelligence",

      icon: FileText,

      desc:
        "Chat with uploaded medical reports using AI-powered PDF reasoning.",

      route: "/chat",
    },

    {

      title: "Health Analytics",

      icon: BarChart3,

      desc:
        "Track symptom recurrence, adherence, and AI-powered healthcare insights.",

      route: "/analytics",
    },

    {

      title: "Medical History",

      icon: History,

      desc:
        "Access saved AI healthcare conversations and downloadable reports.",

      route: "/history",
    },

    {

      title: "Medicine Reminder",

      icon: Bell,

      desc:
        "Track medicine adherence with smart reminder management.",

      route: "/reminders",
    },
  ];


  // ─────────────────────────────
  // LOGOUT
  // ─────────────────────────────

  const handleLogout = () => {

    logout();

    navigate("/login");
  };


  return (

    <div className="min-h-screen bg-black text-white overflow-hidden relative">

      {/* BACKGROUND */}

      <div className="absolute inset-0">

        <div className="absolute top-[-150px] left-[-120px] w-[450px] h-[450px] bg-cyan-500/20 blur-[140px] rounded-full" />

        <div className="absolute bottom-[-180px] right-[-100px] w-[450px] h-[450px] bg-emerald-500/20 blur-[140px] rounded-full" />

      </div>


      {/* GRID */}

      <div className="absolute inset-0 opacity-10 bg-[linear-gradient(to_right,#ffffff10_1px,transparent_1px),linear-gradient(to_bottom,#ffffff10_1px,transparent_1px)] bg-[size:60px_60px]" />


      {/* MAIN */}

      <div className="relative z-10">

        {/* HEADER */}

        <header className="border-b border-white/10 bg-white/5 backdrop-blur-xl">

          <div className="max-w-7xl mx-auto px-8 py-6 flex items-center justify-between">

            {/* BRAND */}

            <div className="flex items-center gap-5">

              <div className="w-16 h-16 rounded-3xl bg-cyan-400 flex items-center justify-center shadow-[0_0_30px_rgba(0,255,255,0.3)]">

                <HeartPulse className="text-black w-8 h-8" />

              </div>


              <div>

                <h1 className="text-4xl font-black tracking-tight">

                  MediZen AI

                </h1>

                <p className="text-slate-400 mt-1">

                  Intelligent Healthcare Platform

                </p>

              </div>

            </div>


            {/* USER */}

            <div className="flex items-center gap-4">

              <div className="hidden md:flex flex-col text-right">

                <span className="font-bold text-cyan-300">

                  {user?.name || "User"}

                </span>

                <span className="text-slate-400 text-sm">

                  {user?.email}

                </span>

              </div>


              {/* LOGOUT */}

              <motion.button

                whileHover={{

                  scale: 1.05,
                }}

                whileTap={{

                  scale: 0.95,
                }}

                onClick={handleLogout}

                className="w-14 h-14 rounded-2xl bg-white/5 hover:bg-red-500/10 border border-white/10 hover:border-red-500/30 flex items-center justify-center transition"
              >

                <LogOut className="text-red-300 w-5 h-5" />

              </motion.button>

            </div>

          </div>

        </header>


        {/* HERO */}

        <section className="max-w-7xl mx-auto px-8 pt-16">

          <motion.div

            initial={{

              opacity: 0,

              y: 30,
            }}

            animate={{

              opacity: 1,

              y: 0,
            }}

            transition={{

              duration: 0.7,
            }}

            className="bg-white/5 border border-white/10 rounded-[40px] p-10 backdrop-blur-2xl relative overflow-hidden"
          >

            {/* GLOW */}

            <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/10 via-transparent to-emerald-500/10 pointer-events-none" />


            <div className="relative z-10">

              <div className="inline-flex items-center gap-3 px-5 py-3 rounded-2xl bg-cyan-400/10 border border-cyan-400/20 text-cyan-300 font-bold">

                <Sparkles className="w-5 h-5" />

                AI-Powered Healthcare Intelligence

              </div>


              <h1 className="text-6xl font-black mt-8 max-w-4xl leading-tight">

                Your Intelligent Healthcare Workspace

              </h1>


              <p className="text-slate-400 text-xl leading-9 mt-8 max-w-3xl">

                Conversational healthcare AI,
                OCR analysis,
                PDF reasoning,
                health analytics,
                adherence tracking,
                and multimodal medical intelligence —
                all in one platform.

              </p>


              {/* CTA */}

              <motion.button

                whileHover={{

                  scale: 1.03,
                }}

                whileTap={{

                  scale: 0.97,
                }}

                onClick={() =>
                  navigate("/chat")
                }

                className="mt-10 inline-flex items-center gap-4 bg-cyan-400 hover:bg-cyan-300 text-black font-black px-8 py-5 rounded-3xl transition shadow-[0_0_40px_rgba(0,255,255,0.25)]"
              >

                Start AI Healthcare Chat

                <ArrowRight className="w-6 h-6" />

              </motion.button>

            </div>

          </motion.div>

        </section>


        {/* FEATURES */}

        <section className="max-w-7xl mx-auto px-8 py-16">

          <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-8">

            {cards.map((card, index) => {

              const Icon = card.icon;

              return (

                <motion.div

                  key={index}

                  initial={{

                    opacity: 0,

                    y: 30,
                  }}

                  animate={{

                    opacity: 1,

                    y: 0,
                  }}

                  transition={{

                    delay: index * 0.08,
                  }}

                  whileHover={{

                    y: -8,
                  }}

                  onClick={() =>
                    navigate(card.route)
                  }

                  className="group cursor-pointer bg-white/5 hover:bg-white/[0.07] border border-white/10 hover:border-cyan-400/30 rounded-[32px] p-8 transition-all duration-300 backdrop-blur-2xl relative overflow-hidden"
                >

                  {/* HOVER */}

                  <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition bg-gradient-to-br from-cyan-500/10 via-transparent to-emerald-500/10 pointer-events-none" />


                  {/* ICON */}

                  <div className="relative z-10 w-16 h-16 rounded-3xl bg-cyan-400 flex items-center justify-center shadow-[0_0_30px_rgba(0,255,255,0.2)]">

                    <Icon className="text-black w-8 h-8" />

                  </div>


                  {/* CONTENT */}

                  <div className="relative z-10">

                    <h2 className="text-3xl font-black mt-8">

                      {card.title}

                    </h2>

                    <p className="text-slate-400 leading-8 mt-5">

                      {card.desc}

                    </p>

                  </div>


                  {/* FOOTER */}

                  <div className="relative z-10 flex items-center gap-3 mt-8 text-cyan-300 font-bold">

                    Open Workspace

                    <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition" />

                  </div>

                </motion.div>
              );
            })}

          </div>

        </section>


        {/* FOOTER */}

        <footer className="border-t border-white/10 bg-white/5 backdrop-blur-xl">

          <div className="max-w-7xl mx-auto px-8 py-6 flex flex-col md:flex-row items-center justify-between gap-4">

            <p className="text-slate-500 text-sm">

              © 2026 MediZen AI — Advanced Healthcare Intelligence Platform

            </p>


            <div className="flex items-center gap-6 text-sm text-slate-500">

              <span>Conversational AI</span>

              <span>OCR Intelligence</span>

              <span>PDF RAG</span>

              <span>Analytics</span>

            </div>

          </div>

        </footer>

      </div>

    </div>
  );
}