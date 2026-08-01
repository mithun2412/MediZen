import { Loader2, Mic, MicOff, Send, Sparkles } from "lucide-react";
import { useEffect, useRef } from "react";

export default function ChatInput({ input, setInput, onSend, onVoiceRecord, isRecording = false, loading = false }) {
  const inputRef = useRef(null);

  useEffect(() => {
    if (!loading) inputRef.current?.focus();
  }, [loading]);

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      if (input.trim() && !loading) onSend();
    }
  };

  return (
    <div className="border-t border-white/10 bg-slate-950/85 px-5 py-4 backdrop-blur-xl sm:px-8">
      <div className="mx-auto max-w-4xl">
        <div className="flex items-end gap-3 rounded-3xl border border-white/10 bg-white/[0.045] p-3 shadow-[0_16px_45px_rgba(0,0,0,0.2)] focus-within:border-cyan-400/50 focus-within:ring-4 focus-within:ring-cyan-400/10">
          <div className="hidden h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-cyan-400 text-slate-950 sm:flex">
            {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : <Sparkles className="h-5 w-5" />}
          </div>
          <textarea
            ref={inputRef}
            autoFocus
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={handleKeyDown}
            rows={1}
            disabled={loading}
            placeholder="Describe how you feel or ask a health question…"
            className="max-h-36 min-h-10 flex-1 resize-none bg-transparent py-2 text-[15px] leading-6 text-white outline-none placeholder:text-slate-500 disabled:cursor-not-allowed"
          />
          <button onClick={onVoiceRecord} disabled={loading} aria-label="Use voice input" className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl border transition ${isRecording ? "border-rose-400/40 bg-rose-400/15 text-rose-300" : "border-white/10 bg-white/5 text-slate-300 hover:bg-white/10"}`}>
            {isRecording ? <MicOff className="h-4 w-4 animate-pulse" /> : <Mic className="h-4 w-4" />}
          </button>
          <button onClick={onSend} disabled={!input.trim() || loading} aria-label="Send message" className="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-cyan-400 text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-40">
            {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : <Send className="h-5 w-5" />}
          </button>
        </div>
        <p className="mt-2 px-2 text-xs text-slate-500">Press Enter to send · Shift + Enter for a new line</p>
      </div>
    </div>
  );
}
