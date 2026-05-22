// src/hooks/useVoiceChat.js

import { useState, useRef, useCallback } from "react";

const API_BASE = import.meta.env.VITE_API_URL;

export function useVoiceChat() {

  const [isRecording, setIsRecording] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [transcript, setTranscript] = useState("");

  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const utteranceRef = useRef(null);

  // START RECORDING
  const startRecording = useCallback(async () => {

    try {

      const stream = await navigator.mediaDevices.getUserMedia({
        audio: true,
      });

      const mimeType = MediaRecorder.isTypeSupported(
        "audio/webm;codecs=opus"
      )
        ? "audio/webm;codecs=opus"
        : MediaRecorder.isTypeSupported("audio/webm")
        ? "audio/webm"
        : "audio/ogg";

      const recorder = new MediaRecorder(stream, {
        mimeType,
      });

      mediaRecorderRef.current = recorder;
      chunksRef.current = [];

      recorder.ondataavailable = (e) => {

        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      recorder.start(250);

      setIsRecording(true);

    } catch (err) {

      console.error("Mic access denied:", err);

      alert(
        "Microphone access is required for voice input."
      );
    }

  }, []);

  // STOP RECORDING
  const stopRecording = useCallback(() => {

    return new Promise((resolve) => {

      const recorder = mediaRecorderRef.current;

      if (!recorder) {
        return resolve("");
      }

      recorder.onstop = async () => {

        setIsRecording(false);

        const blob = new Blob(chunksRef.current, {
          type: recorder.mimeType,
        });

        const formData = new FormData();

        formData.append(
          "file",
          blob,
          "recording.webm"
        );

        try {

          const res = await fetch(
            `${API_BASE}/voice/transcribe`,
            {
              method: "POST",
              body: formData,
            }
          );

          const data = await res.json();

          const text = data.transcript || "";

          setTranscript(text);

          resolve(text);

        } catch (err) {

          console.error(
            "Transcription error:",
            err
          );

          resolve("");
        }

        recorder.stream
          .getTracks()
          .forEach((t) => t.stop());
      };

      recorder.stop();
    });

  }, []);

  // SPEAK
  const speak = useCallback((text) => {

    if (!text?.trim()) return;

    if (!window.speechSynthesis) {

      console.warn(
        "Speech synthesis not supported"
      );

      return;
    }

    window.speechSynthesis.cancel();

    const utterance =
      new SpeechSynthesisUtterance(text);

    utteranceRef.current = utterance;

    const voices =
      window.speechSynthesis.getVoices();

    const preferred = voices.find(
      (v) =>
        v.lang.startsWith("en") &&
        (
          v.name.includes("Google") ||
          v.name.includes("Natural") ||
          v.name.includes("Female")
        )
    );

    if (preferred) {
      utterance.voice = preferred;
    }

    utterance.rate = 0.95;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;

    utterance.onstart = () =>
      setIsSpeaking(true);

    utterance.onend = () =>
      setIsSpeaking(false);

    utterance.onerror = () =>
      setIsSpeaking(false);

    window.speechSynthesis.speak(
      utterance
    );

  }, []);

  // STOP SPEAKING
  const stopSpeaking = useCallback(() => {

    window.speechSynthesis.cancel();

    setIsSpeaking(false);

  }, []);

  return {

    isRecording,
    isSpeaking,
    transcript,

    startRecording,
    stopRecording,

    speak,
    stopSpeaking,
  };
}