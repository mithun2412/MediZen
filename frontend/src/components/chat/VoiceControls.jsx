// src/components/chat/VoiceControls.jsx

import { Mic, MicOff } from "lucide-react";
import { useState } from "react";

export default function VoiceControls({ setInput, autoSend = true, onSend }) {
  const [isRecording, setIsRecording] = useState(false);
  const [recognition, setRecognition] = useState(null);

  const startRecording = () => {
    if (!('webkitSpeechRecognition' in window)) {
      alert('Speech recognition is not supported in this browser.');
      return;
    }

    const recognitionInstance = new window.webkitSpeechRecognition();
    recognitionInstance.lang = 'en-US';
    recognitionInstance.continuous = false;
    recognitionInstance.interimResults = true;

    setRecognition(recognitionInstance);
    setIsRecording(true);

    recognitionInstance.onresult = (event) => {
      let transcript = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          setInput(transcript);
          setIsRecording(false);
          if (autoSend && onSend) {
            onSend(transcript);
          }
        }
      }
    };

    recognitionInstance.onerror = () => {
      setIsRecording(false);
    };

    recognitionInstance.onend = () => {
      setIsRecording(false);
    };

    recognitionInstance.start();
  };

  const stopRecording = () => {
    if (recognition) {
      recognition.stop();
    }
    setIsRecording(false);
  };

  return (
    <button
      onClick={isRecording ? stopRecording : startRecording}
      className={`w-12 h-12 rounded-2xl border border-white/10 flex items-center justify-center transition flex-shrink-0 ${
        isRecording 
          ? 'bg-red-500/20 border-red-500/30 hover:bg-red-500/30' 
          : 'bg-white/5 hover:bg-white/10'
      }`}
    >
      {isRecording ? (
        <MicOff className="text-red-400 w-5 h-5 animate-pulse" />
      ) : (
        <Mic className="text-white w-5 h-5" />
      )}
    </button>
  );
}