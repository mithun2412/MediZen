import { useEffect, useRef, useState } from "react";

import { motion } from "framer-motion";

import {

  Mic,

  MicOff,

  Volume2,

  AudioWaveform

} from "lucide-react";


export default function VoiceControls({

  setInput,

  autoSend = false,

  onSend,

}) {

  const recognitionRef = useRef(null);

  const [listening, setListening] =
    useState(false);

  const [supported, setSupported] =
    useState(true);

  const [transcript, setTranscript] =
    useState("");


  // ─────────────────────────────
  // INIT SPEECH RECOGNITION
  // ─────────────────────────────

  useEffect(() => {

    const SpeechRecognition =

      window.SpeechRecognition ||

      window.webkitSpeechRecognition;


    if (!SpeechRecognition) {

      setSupported(false);

      return;
    }


    const recognition =
      new SpeechRecognition();

    recognition.continuous = false;

    recognition.interimResults = true;

    recognition.lang = "en-US";


    // START
    recognition.onstart = () => {

      setListening(true);
    };


    // RESULT
    recognition.onresult = (event) => {

      let finalTranscript = "";

      for (

        let i = 0;

        i < event.results.length;

        i++
      ) {

        finalTranscript +=

          event.results[i][0].transcript;
      }

      setTranscript(finalTranscript);

      setInput(finalTranscript);
    };


    // END
    recognition.onend = () => {

      setListening(false);

      // AUTO SEND
      if (

        autoSend &&

        transcript.trim()
      ) {

        onSend();
      }
    };


    // ERROR
    recognition.onerror = (
      event
    ) => {

      console.log(
        "Speech recognition error:",
        event.error
      );

      setListening(false);
    };


    recognitionRef.current =
      recognition;

  }, [setInput, transcript, autoSend, onSend]);


  // ─────────────────────────────
  // START LISTENING
  // ─────────────────────────────

  const startListening = () => {

    if (
      recognitionRef.current
    ) {

      setTranscript("");

      recognitionRef.current.start();
    }
  };


  // ─────────────────────────────
  // STOP LISTENING
  // ─────────────────────────────

  const stopListening = () => {

    if (
      recognitionRef.current
    ) {

      recognitionRef.current.stop();
    }
  };


  // ─────────────────────────────
  // NOT SUPPORTED
  // ─────────────────────────────

  if (!supported) {

    return (

      <div className="flex items-center gap-3 text-red-300 text-sm">

        <MicOff className="w-5 h-5" />

        Voice recognition not supported in this browser.

      </div>
    );
  }


  return (

    <div className="flex items-center gap-4">

      {/* STATUS */}

      {listening && (

        <motion.div

          initial={{

            opacity: 0,
          }}

          animate={{

            opacity: 1,
          }}

          className="hidden md:flex items-center gap-3 px-4 py-3 rounded-2xl bg-red-500/10 border border-red-500/20 text-red-300"
        >

          <AudioWaveform className="w-5 h-5 animate-pulse" />

          <span className="text-sm font-medium">

            Listening...

          </span>

        </motion.div>
      )}


      {/* BUTTON */}

      <motion.button

        whileHover={{

          scale: 1.08,
        }}

        whileTap={{

          scale: 0.92,
        }}

        onClick={

          listening

            ? stopListening

            : startListening
        }

        className={`

          relative

          w-14

          h-14

          rounded-2xl

          flex

          items-center

          justify-center

          transition-all

          duration-300

          shadow-2xl

          border

          overflow-hidden

          ${

            listening

              ? "bg-red-500 border-red-400"

              : "bg-cyan-400 border-cyan-300"
          }
        `}
      >

        {/* PULSE */}

        {listening && (

          <motion.div

            animate={{

              scale: [1, 1.6],

              opacity: [0.7, 0],
            }}

            transition={{

              duration: 1.2,

              repeat: Infinity,
            }}

            className="absolute inset-0 rounded-2xl bg-red-400"
          />

        )}


        {/* ICON */}

        {listening ? (

          <MicOff className="relative z-10 text-white w-6 h-6" />

        ) : (

          <Mic className="relative z-10 text-black w-6 h-6" />

        )}

      </motion.button>


      {/* TRANSCRIPT */}

      {transcript && (

        <motion.div

          initial={{

            opacity: 0,

            y: 10,
          }}

          animate={{

            opacity: 1,

            y: 0,
          }}

          className="hidden xl:flex items-center gap-3 px-5 py-3 rounded-2xl bg-white/5 border border-white/10 text-slate-300 max-w-[300px] truncate"
        >

          <Volume2 className="w-5 h-5 text-cyan-300 shrink-0" />

          <span className="truncate text-sm">

            {transcript}

          </span>

        </motion.div>
      )}

    </div>
  );
}