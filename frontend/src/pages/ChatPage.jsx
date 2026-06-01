import { useEffect, useRef, useState } from "react";

import { motion, AnimatePresence } from "framer-motion";

import {

  BrainCircuit,

  ShieldCheck,

  Activity,

  Upload,

  FileText,

  Mic,

  HeartPulse,

} from "lucide-react";

import {

  sendMessage,

  uploadMedicalImage,

  uploadMedicalPDF,

} from "../api/api";

import { useAuth } from "../context/AuthContext";

import MessageBubble from "../components/chat/MessageBubble";

import ChatInput from "../components/chat/ChatInput";

import TypingLoader from "../components/chat/TypingLoader";

import FollowupOptions from "../components/chat/FollowupOptions";


// ─────────────────────────────────────────────
// SEVERITY CONFIG
// ─────────────────────────────────────────────

const severityConfig = {

  Low: {

    bg: "bg-emerald-500/10",

    text: "text-emerald-300",

    icon: "✅",
  },

  Moderate: {

    bg: "bg-yellow-500/10",

    text: "text-yellow-300",

    icon: "⚠️",
  },

  High: {

    bg: "bg-red-500/10",

    text: "text-red-300",

    icon: "🚨",
  },
};


export default function ChatPage() {

  const { user } = useAuth();

  const [messages, setMessages] = useState([]);

  const [loading, setLoading] = useState(false);

  const [input, setInput] = useState("");

  const [location, setLocation] = useState({

    latitude: null,

    longitude: null,
  });

  const bottomRef = useRef(null);


  // ─────────────────────────
  // AUTO SCROLL
  // ─────────────────────────

  useEffect(() => {

    bottomRef.current?.scrollIntoView({

      behavior: "smooth",
    });

  }, [messages, loading]);


  // ─────────────────────────
  // GET LOCATION
  // ─────────────────────────

  useEffect(() => {

    navigator.geolocation.getCurrentPosition(

      (position) => {

        setLocation({

          latitude:
            position.coords.latitude,

          longitude:
            position.coords.longitude,
        });
      },

      () => {

        console.log(
          "Location access denied"
        );
      }
    );

  }, []);


  // ─────────────────────────
  // SPEECH
  // ─────────────────────────

  const speak = (text) => {

    const speech = new SpeechSynthesisUtterance(
      text
    );

    speech.lang = "en-US";

    window.speechSynthesis.speak(
      speech
    );
  };


  // ─────────────────────────
  // SEND MESSAGE
  // ─────────────────────────

  const handleSendMessage = async (

    customMessage = null
  ) => {

    const finalMessage =
      customMessage || input;

    if (!finalMessage.trim()) return;

    // USER MESSAGE
    const userMessage = {

      role: "user",

      content: finalMessage,
    };

    setMessages((prev) => [

      ...prev,

      userMessage,
    ]);

    setInput("");

    setLoading(true);

    try {

      // BACKEND REQUEST
      const response = await sendMessage({

        user_id: user.id,

        message: finalMessage,

        latitude:
          location.latitude,

        longitude:
          location.longitude,

        conversation_history:
          messages,
      });

      const data = response.data;

      // AI MESSAGE
      const aiMessage = {

        role: "assistant",

        content:
          data.response ||

          "No response received.",

        severity:
          data.severity,

        hospitals:
          data.hospitals || [],

        pdfUrl:
          data.pdf_url || null,

        followup_options:
          data.followup_options || [],
      };

      setMessages((prev) => [

        ...prev,

        aiMessage,
      ]);

    } catch (err) {

      console.log(err);

      setMessages((prev) => [

        ...prev,

        {

          role: "assistant",

          content:
            "Unable to connect to MediZen AI backend.",
        },
      ]);

    } finally {

      setLoading(false);
    }
  };


  // ─────────────────────────
  // IMAGE UPLOAD
  // ─────────────────────────

  const handleImageUpload = async (
    file
  ) => {

    const formData = new FormData();

    formData.append("file", file);

    setLoading(true);

    try {

      const response =
        await uploadMedicalImage(
          formData
        );

      const data = response.data;

      setMessages((prev) => [

        ...prev,

        {

          role: "assistant",

          content:
            data.analysis,

          severity:
            data.severity ||

            "Moderate",

          pdfUrl:
            data.pdf_url,

          image:
            `http://127.0.0.1:8000${data.image_url}`,
        },
      ]);

    } catch (err) {

      console.log(err);

    } finally {

      setLoading(false);
    }
  };


  // ─────────────────────────
  // PDF UPLOAD
  // ─────────────────────────

  const handlePDFUpload = async (
    file
  ) => {

    const formData = new FormData();

    formData.append("file", file);

    setLoading(true);

    try {

      const response =
        await uploadMedicalPDF(
          formData
        );

      const data = response.data;

      setMessages((prev) => [

        ...prev,

        {

          role: "assistant",

          content:

            `PDF uploaded successfully.\n\n` +

            `Indexed ${data.chunks_indexed} document chunks.\n\n` +

            `You can now ask questions from this report.`,
        },
      ]);

    } catch (err) {

      console.log(err);

    } finally {

      setLoading(false);
    }
  };


  return (

    <div className="min-h-screen bg-black text-white flex overflow-hidden">

      {/* SIDEBAR */}

      <div className="hidden xl:flex w-80 border-r border-white/10 bg-white/5 backdrop-blur-xl p-8 flex-col">

        {/* LOGO */}

        <div className="flex items-center gap-4">

          <div className="w-16 h-16 rounded-3xl bg-cyan-400 flex items-center justify-center">

            <HeartPulse className="text-black w-8 h-8" />

          </div>

          <div>

            <h1 className="text-3xl font-black">

              MediZen AI

            </h1>

            <p className="text-slate-400 mt-1">

              Intelligent Healthcare
            </p>

          </div>

        </div>


        {/* USER */}

        <div className="mt-12 bg-white/5 border border-white/10 rounded-3xl p-6">

          <h3 className="text-lg font-bold">

            Logged In As
          </h3>

          <p className="mt-4 text-cyan-300 font-bold">

            {user?.name}
          </p>

          <p className="text-slate-400 mt-1">

            {user?.email}
          </p>

        </div>


        {/* FEATURES */}

        <div className="mt-10 space-y-4">

          {[

            {
              icon: BrainCircuit,
              title: "AI Chat",
            },

            {
              icon: Upload,
              title: "OCR Analysis",
            },

            {
              icon: FileText,
              title: "PDF Intelligence",
            },

            {
              icon: Activity,
              title: "Health Analytics",
            },

            {
              icon: ShieldCheck,
              title: "Secure History",
            },
          ].map((item, index) => {

            const Icon = item.icon;

            return (

              <motion.div

                key={index}

                whileHover={{
                  scale: 1.02,
                }}

                className="bg-white/5 border border-white/10 rounded-2xl p-5 flex items-center gap-4"
              >

                <div className="w-12 h-12 rounded-2xl bg-cyan-400 flex items-center justify-center">

                  <Icon className="text-black" />

                </div>

                <h3 className="font-bold">

                  {item.title}
                </h3>

              </motion.div>
            );
          })}
        </div>

      </div>


      {/* CHAT AREA */}

      <div className="flex-1 flex flex-col">

        {/* HEADER */}

        <div className="border-b border-white/10 bg-white/5 backdrop-blur-xl px-8 py-6 flex items-center justify-between">

          <div>

            <h2 className="text-3xl font-black">

              AI Healthcare Assistant

            </h2>

            <p className="text-slate-400 mt-1">

              Conversational healthcare intelligence powered by AI
            </p>

          </div>


          {/* ACTIONS */}

          <div className="flex items-center gap-4">

            {/* IMAGE */}

            <label className="cursor-pointer bg-white/5 hover:bg-white/10 border border-white/10 rounded-2xl px-5 py-3 flex items-center gap-3 transition">

              <Upload className="w-5 h-5" />

              <span>Upload Image</span>

              <input

                type="file"

                accept="image/*"

                hidden

                onChange={(e) => {

                  if (e.target.files[0]) {

                    handleImageUpload(
                      e.target.files[0]
                    );
                  }
                }}
              />

            </label>


            {/* PDF */}

            <label className="cursor-pointer bg-white/5 hover:bg-white/10 border border-white/10 rounded-2xl px-5 py-3 flex items-center gap-3 transition">

              <FileText className="w-5 h-5" />

              <span>Upload PDF</span>

              <input

                type="file"

                accept=".pdf"

                hidden

                onChange={(e) => {

                  if (e.target.files[0]) {

                    handlePDFUpload(
                      e.target.files[0]
                    );
                  }
                }}
              />

            </label>

          </div>

        </div>


        {/* MESSAGES */}

        <div className="flex-1 overflow-y-auto px-6 py-8 space-y-6">

          {/* EMPTY */}

          {messages.length === 0 && (

            <motion.div

              initial={{

                opacity: 0,

                y: 30,
              }}

              animate={{

                opacity: 1,

                y: 0,
              }}

              className="max-w-5xl mx-auto text-center mt-20"
            >

              <div className="w-28 h-28 rounded-[40px] bg-cyan-400 mx-auto flex items-center justify-center shadow-[0_0_80px_rgba(0,255,255,0.2)]">

                <BrainCircuit className="text-black w-14 h-14" />

              </div>

              <h1 className="text-6xl font-black mt-10">

                MediZen AI
              </h1>

              <p className="text-slate-400 mt-6 text-xl leading-9 max-w-3xl mx-auto">

                Intelligent healthcare conversations, medical OCR,
                PDF reasoning, AI-powered reports, adherence
                analytics, and multimodal healthcare intelligence.
              </p>

            </motion.div>
          )}


          {/* CHAT */}

          <AnimatePresence>

            {messages.map((msg, index) => (

              <div key={index}>

                <MessageBubble

                  msg={msg}

                  severityConfig={
                    severityConfig
                  }

                  speak={speak}
                />

                {/* FOLLOWUP OPTIONS */}

                {msg.followup_options?.length >

                  0 && (

                  <FollowupOptions

                    options={
                      msg.followup_options
                    }

                    onSelect={(
                      option
                    ) =>
                      handleSendMessage(
                        option
                      )
                    }
                  />
                )}

              </div>
            ))}
          </AnimatePresence>


          {/* LOADER */}

          {loading && <TypingLoader />}

          <div ref={bottomRef} />

        </div>


        {/* INPUT */}

        <ChatInput

          input={input}

          setInput={setInput}

          onSend={handleSendMessage}
        />

      </div>

    </div>
  );
}