import { useState, useRef, useEffect, useCallback } from "react";

// ─────────────────────────────────────────────
//  CONFIG
// ─────────────────────────────────────────────
const API_BASE = "http://127.0.0.1:8000";

const QUICK_PROMPTS = [
  { icon: "🤕", label: "Headache & Nausea",  text: "I have a severe headache and feel nauseous since this morning." },
  { icon: "😮‍💨", label: "Breathing Issues", text: "I'm experiencing shortness of breath and chest tightness." },
  { icon: "🤒", label: "Fever & Chills",      text: "I have a high fever with chills and body ache for 2 days." },
  { icon: "🫃", label: "Stomach Pain",         text: "I have sharp stomach cramps and bloating after eating." },
  { icon: "😴", label: "Fatigue",              text: "I feel extremely tired and weak, can't focus on anything." },
  { icon: "💊", label: "Medicine Query",       text: "Can you explain the side effects of Metformin 500mg?" },
];

const SEVERITY_CONFIG = {
  Critical: {
    color: "#ff3b3b", bg: "rgba(255,59,59,0.12)", border: "rgba(255,59,59,0.4)",
    glow: "rgba(255,59,59,0.25)", icon: "🚨", label: "Critical — Emergency",
    advice: "Call 112 / go to the nearest emergency room IMMEDIATELY.", pulse: true,
  },
  High: {
    color: "#ef4444", bg: "rgba(239,68,68,0.10)", border: "rgba(239,68,68,0.3)",
    glow: "rgba(239,68,68,0.18)", icon: "⛔", label: "High Severity",
    advice: "Seek immediate medical attention today.", pulse: false,
  },
  Moderate: {
    color: "#f59e0b", bg: "rgba(245,158,11,0.10)", border: "rgba(245,158,11,0.3)",
    glow: "rgba(245,158,11,0.18)", icon: "⚠️", label: "Moderate Severity",
    advice: "See a doctor within 1–2 days. Monitor symptoms closely.", pulse: false,
  },
  Low: {
    color: "#22d3ee", bg: "rgba(34,211,238,0.08)", border: "rgba(34,211,238,0.25)",
    glow: "rgba(34,211,238,0.12)", icon: "✅", label: "Low Severity",
    advice: "Rest, stay hydrated, and monitor for any changes.", pulse: false,
  },
};

// ─────────────────────────────────────────────
//  HELPERS
// ─────────────────────────────────────────────
function now() {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function looksConfused(userText, lastAiQuestion) {
  if (!lastAiQuestion || !userText) return false;
  const u = userText.toLowerCase().trim();
  const q = lastAiQuestion.toLowerCase().trim();
  const CONFUSION_PHRASES = [
    "i don't understand", "i dont understand", "what do you mean",
    "what does that mean", "i don't know what", "dont know what",
    "can you explain", "what are you asking", "not sure what you mean",
    "i'm confused", "im confused", "unclear", "rephrase", "simplify",
    "what question", "huh", "what?", "i don't get it", "dont get it",
  ];
  if (CONFUSION_PHRASES.some(p => u.includes(p))) return true;
  const uWords = new Set(u.split(/\s+/).filter(w => w.length > 3));
  const qWords = q.split(/\s+/).filter(w => w.length > 3);
  if (qWords.length === 0) return false;
  const overlap = qWords.filter(w => uWords.has(w)).length;
  return overlap / qWords.length > 0.4;
}

function todayLabel() {
  return new Date().toLocaleDateString([], { month: "short", day: "numeric" });
}

function uid() {
  return Math.random().toString(36).slice(2, 10);
}

function headers() {
  const token = localStorage.getItem("token");
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

// Strip markdown for cleaner TTS
function stripMarkdown(text) {
  if (!text) return "";
  return text
    .replace(/\*\*(.*?)\*\*/g, "$1")
    .replace(/\*(.*?)\*/g, "$1")
    .replace(/#{1,6}\s/g, "")
    .replace(/`{1,3}[^`]*`{1,3}/g, "")
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
    .replace(/🚨|⚠️|✅|⛔|🔍|🌿|🏥|📊/g, "")
    .replace(/\n{2,}/g, ". ")
    .replace(/\n/g, " ")
    .trim();
}

// Build a plain-English summary from a final analysis for TTS
function buildAnalysisSpeech(parsed, severity, isEmergency) {
  const parts = [];
  if (isEmergency) {
    parts.push("Emergency alert. Seek immediate medical help. Call 112 or go to the nearest emergency room now.");
  }
  if (parsed?.conditions?.length) {
    const names = parsed.conditions.map(c => c.name).join(", ");
    parts.push(`Based on your symptoms, possible conditions include: ${names}.`);
  }
  if (severity) {
    const cfg = SEVERITY_CONFIG[severity];
    parts.push(`Severity is rated ${severity}. ${cfg?.advice || ""}`);
  }
  if (parsed?.whenDoctor) {
    parts.push(`Regarding when to see a doctor: ${parsed.whenDoctor}`);
  }
  return parts.join(" ");
}

// ─────────────────────────────────────────────
//  STORAGE
// ─────────────────────────────────────────────
const STORAGE_KEY = "medizen_chat_sessions";

function loadSessions() {
  try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]"); }
  catch { return []; }
}

function saveSessions(sessions) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions));
}

// ─────────────────────────────────────────────
//  VOICE HOOK
// ─────────────────────────────────────────────
function useVoice({ autoSpeak }) {
  const [isRecording, setIsRecording] = useState(false);
  const [isSpeaking,  setIsSpeaking]  = useState(false);
  const mediaRecorderRef = useRef(null);
  const chunksRef        = useRef([]);
  const utteranceRef     = useRef(null);
  const voicesReadyRef   = useRef(false);

  // Pre-load voices (Chrome needs this)
  useEffect(() => {
    const load = () => { window.speechSynthesis.getVoices(); voicesReadyRef.current = true; };
    load();
    window.speechSynthesis.onvoiceschanged = load;
    return () => { window.speechSynthesis.onvoiceschanged = null; };
  }, []);

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mimeType = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
        ? "audio/webm;codecs=opus"
        : MediaRecorder.isTypeSupported("audio/webm")
        ? "audio/webm"
        : "audio/ogg";
      const recorder = new MediaRecorder(stream, { mimeType });
      mediaRecorderRef.current = recorder;
      chunksRef.current = [];
      recorder.ondataavailable = (e) => { if (e.data.size > 0) chunksRef.current.push(e.data); };
      recorder.start(250);
      setIsRecording(true);
    } catch (err) {
      console.error("Mic access denied:", err);
      alert("Microphone access is required for voice input. Please allow mic access and try again.");
    }
  }, []);

  const stopRecording = useCallback(() => {
    return new Promise((resolve) => {
      const recorder = mediaRecorderRef.current;
      if (!recorder || recorder.state === "inactive") return resolve("");
      recorder.onstop = async () => {
        setIsRecording(false);
        const blob = new Blob(chunksRef.current, { type: recorder.mimeType });
        const formData = new FormData();
        formData.append("file", blob, "recording.webm");
        try {
          const token = localStorage.getItem("token");
          const res = await fetch(`${API_BASE}/voice/transcribe`, {
            method: "POST",
            headers: token ? { Authorization: `Bearer ${token}` } : {},
            body: formData,
          });
          const data = await res.json();
          resolve(data.transcript || "");
        } catch (err) {
          console.error("Transcription error:", err);
          resolve("");
        }
        recorder.stream.getTracks().forEach(t => t.stop());
      };
      recorder.stop();
    });
  }, []);

  const speak = useCallback((text) => {
    if (!autoSpeak) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utteranceRef.current = utterance;
    const voices = window.speechSynthesis.getVoices();
    const preferred = voices.find(v =>
      v.lang.startsWith("en") &&
      (v.name.includes("Google") || v.name.includes("Natural") || v.name.includes("Samantha") || v.name.includes("Karen"))
    ) || voices.find(v => v.lang.startsWith("en"));
    if (preferred) utterance.voice = preferred;
    utterance.rate   = 0.95;
    utterance.pitch  = 1.0;
    utterance.volume = 1.0;
    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend   = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);
    window.speechSynthesis.speak(utterance);
  }, [autoSpeak]);

  const stopSpeaking = useCallback(() => {
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
  }, []);

  return { isRecording, isSpeaking, startRecording, stopRecording, speak, stopSpeaking };
}

// ─────────────────────────────────────────────
//  TYPING INDICATOR
// ─────────────────────────────────────────────
function TypingIndicator() {
  return (
    <div style={{ display: "flex", gap: 5, padding: "14px 18px", alignItems: "center" }}>
      {[0, 1, 2].map(i => (
        <div key={i} style={{
          width: 8, height: 8, borderRadius: "50%", background: "#22d3ee",
          animation: "typingBounce 1.2s ease-in-out infinite",
          animationDelay: `${i * 0.2}s`,
        }} />
      ))}
    </div>
  );
}

// ─────────────────────────────────────────────
//  SIMPLIFY QUESTION
// ─────────────────────────────────────────────
function simplifyQuestion(question) {
  if (!question) return "Could you tell me a bit more?";
  const q = question.toLowerCase();
  if (q.includes("scale") || q.includes("1 to 10") || q.includes("rate it"))
    return "How bad does it feel? Think of it like a score — 1 means barely noticeable, 10 means unbearable. What number would you give it?";
  if (q.includes("sharp") || q.includes("dull") || q.includes("burning") || q.includes("character"))
    return "What does the feeling actually feel like? For example: is it sharp (like a needle), dull (like a bruise), burning (like heat), or something else?";
  if (q.includes("radiat") || q.includes("spread") || q.includes("travel"))
    return "Does the pain or discomfort stay in one spot, or does it move to another part of your body?";
  if (q.includes("onset") || q.includes("started") || q.includes("sudden") || q.includes("gradual"))
    return "When did this start? And did it hit you all at once (like suddenly), or did it slowly get worse over time?";
  if (q.includes("aggravat") || q.includes("reliev") || q.includes("makes it"))
    return "Is there anything that makes it feel better or worse? For example: lying down, moving around, eating, or resting?";
  if (q.includes("constant") || q.includes("comes and goes") || q.includes("pattern"))
    return "Is it there all the time, or does it come and go? If it comes and goes, how long does each time last?";
  if (q.includes("fever") || q.includes("temperature") || q.includes("thermometer"))
    return "Do you have a thermometer? If yes, what did it show? If not — do you feel very hot to the touch or just a little warm?";
  if (q.includes("bowel") || q.includes("stool") || q.includes("diarrhea") || q.includes("meal"))
    return "Did your stomach problems start after eating something? And have your toilet habits changed?";
  if (q.includes("breath") || q.includes("lying") || q.includes("wheez"))
    return "Is it harder to breathe when you're lying down compared to sitting up? And do you hear any whistling or crackling sounds?";
  if (q.includes("vision") || q.includes("numbness") || q.includes("weakness") || q.includes("neuro"))
    return "Are you noticing anything unusual like blurry vision, numbness, or feeling unusually confused?";
  if (q.includes("medical history") || q.includes("condition") || q.includes("medication"))
    return "Do you have any health conditions a doctor has told you about? And are you taking any medicines right now?";
  if (q.includes("travel") || q.includes("exposure") || q.includes("stress"))
    return "Have you done anything different lately — like travelling, eating something new, or been around someone who was sick?";
  if (q.includes("daily") || q.includes("work") || q.includes("sleep") || q.includes("functional"))
    return "How much is this affecting your normal day? Can you still sleep, eat, and do basic things?";
  return question.length > 120 ? question.slice(0, 120).trim() + "… (just answer the part you understand best)" : question;
}

// ─────────────────────────────────────────────
//  AI BUBBLE
// ─────────────────────────────────────────────
const labelStyle = {
  fontSize: 11, fontFamily: "'Space Mono',monospace",
  letterSpacing: "0.09em", textTransform: "uppercase", color: "#475569",
};

function AIBubble({ msg }) {
  const sev = SEVERITY_CONFIG[msg.severity] || SEVERITY_CONFIG["Low"];
  return (
    <div style={{
      background: msg.type === "error" ? "rgba(239,68,68,0.07)" : "rgba(255,255,255,0.04)",
      border: msg.type === "error" ? "1px solid rgba(239,68,68,0.2)" : "1px solid rgba(255,255,255,0.08)",
      borderRadius: "4px 20px 20px 20px",
      padding: "20px 22px", fontSize: 14, lineHeight: 1.7, color: "#cbd5e1",
      minWidth: 260, display: "flex", flexDirection: "column", gap: 14,
    }}>
      {(msg.type === "welcome" || msg.type === "error" || msg.type === "question") && (
        <p style={{ margin: 0 }}>{msg.text}</p>
      )}
      {msg.type === "clarify" && (
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          <div style={{
            background: "rgba(245,158,11,0.08)", border: "1px solid rgba(245,158,11,0.22)",
            borderRadius: 12, padding: "10px 14px", display: "flex", alignItems: "flex-start", gap: 10,
          }}>
            <span style={{ fontSize: 18, flexShrink: 0 }}>💡</span>
            <div>
              <div style={{ fontWeight: 700, fontSize: 13, color: "#fbbf24", marginBottom: 4 }}>
                No worries — let me put that more simply!
              </div>
              <p style={{ margin: 0, fontSize: 13, color: "#fde68a", lineHeight: 1.6 }}>
                {simplifyQuestion(msg.question)}
              </p>
            </div>
          </div>
          <p style={{ margin: 0, fontSize: 12, color: "#64748b" }}>
            Just type whatever feels natural — even a few words is fine.
          </p>
        </div>
      )}
      {msg.type === "analysis" && msg.parsed && (<>
        {msg.isEmergency && (
          <div style={{
            background: "rgba(255,59,59,0.15)", border: "1px solid rgba(255,59,59,0.5)",
            borderRadius: 14, padding: "12px 16px", display: "flex", alignItems: "center", gap: 10,
            animation: "emergencyPulse 1.2s ease-in-out infinite",
          }}>
            <span style={{ fontSize: 22 }}>🚨</span>
            <div>
              <div style={{ fontWeight: 800, color: "#ff3b3b", fontSize: 15 }}>EMERGENCY ALERT</div>
              <div style={{ fontSize: 13, color: "#fca5a5" }}>Call 112 or go to the nearest emergency room NOW.</div>
            </div>
          </div>
        )}
        {msg.parsed.conditions?.length > 0 && (
          <div>
            <div style={labelStyle}>🔍 Possible Conditions</div>
            <div style={{ display: "flex", flexDirection: "column", gap: 8, marginTop: 8 }}>
              {msg.parsed.conditions.map((c, i) => (
                <div key={i} style={{
                  background: "rgba(167,139,250,0.07)", border: "1px solid rgba(167,139,250,0.18)",
                  borderRadius: 12, padding: "10px 14px", borderLeft: "3px solid rgba(167,139,250,0.5)",
                }}>
                  <div style={{ fontWeight: 700, fontSize: 13, color: "#c4b5fd", marginBottom: c.desc ? 3 : 0 }}>{c.name}</div>
                  {c.desc && <div style={{ fontSize: 12, color: "#94a3b8", lineHeight: 1.6 }}>{c.desc}</div>}
                </div>
              ))}
            </div>
          </div>
        )}
        <div>
          <div style={labelStyle}>📊 Severity Assessment</div>
          <div style={{
            display: "inline-flex", alignItems: "center", gap: 10,
            background: sev.bg, border: `1px solid ${sev.border}`,
            borderRadius: 14, padding: "11px 16px", marginTop: 6,
            boxShadow: `0 0 20px ${sev.glow}`,
            animation: sev.pulse ? "emergencyPulse 1.2s ease-in-out infinite" : "none",
          }}>
            <span style={{ fontSize: 20 }}>{sev.icon}</span>
            <div>
              <div style={{ fontWeight: 700, fontSize: 14, color: sev.color }}>{sev.label}</div>
              <div style={{ fontSize: 12, color: "#94a3b8", marginTop: 1 }}>{sev.advice}</div>
            </div>
          </div>
        </div>
        {msg.parsed.remedies?.length > 0 && (
          <div>
            <div style={labelStyle}>🌿 Home Remedies</div>
            <div style={{ display: "flex", flexDirection: "column", gap: 7, marginTop: 8 }}>
              {msg.parsed.remedies.map((r, i) => (
                <div key={i} style={{
                  display: "flex", alignItems: "flex-start", gap: 12,
                  background: "rgba(52,211,153,0.05)", border: "1px solid rgba(52,211,153,0.14)",
                  borderRadius: 12, padding: "10px 14px",
                }}>
                  <div style={{
                    width: 24, height: 24, borderRadius: 8, flexShrink: 0, marginTop: 1,
                    background: "rgba(52,211,153,0.15)", border: "1px solid rgba(52,211,153,0.3)",
                    display: "flex", alignItems: "center", justifyContent: "center",
                    fontSize: 12, color: "#34d399", fontWeight: 700,
                  }}>{i + 1}</div>
                  <div>
                    <div style={{ fontWeight: 700, fontSize: 13, color: "#6ee7b7", marginBottom: r.tip ? 2 : 0 }}>{r.title}</div>
                    {r.tip && <div style={{ fontSize: 12, color: "#94a3b8", lineHeight: 1.6 }}>{r.tip}</div>}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        {msg.parsed.whenDoctor && (
          <div style={{
            background: "rgba(251,146,60,0.08)", border: "1px solid rgba(251,146,60,0.2)",
            borderRadius: 12, padding: "12px 14px",
          }}>
            <div style={{ ...labelStyle, color: "#fb923c", marginBottom: 4 }}>🏥 When to See a Doctor</div>
            <p style={{ margin: 0, fontSize: 13, color: "#fed7aa", lineHeight: 1.6 }}>{msg.parsed.whenDoctor}</p>
          </div>
        )}
        <div style={{
          fontSize: 11, color: "#334155", borderTop: "1px solid rgba(255,255,255,0.06)",
          paddingTop: 10, fontStyle: "italic",
        }}>
          ⚠️ This analysis is for informational purposes only and is NOT professional medical advice.
        </div>
      </>)}
    </div>
  );
}

// ─────────────────────────────────────────────
//  SIDEBAR
// ─────────────────────────────────────────────
function Sidebar({ sessions, activeId, onSelect, onNew, onDelete, collapsed, onToggle }) {
  return (
    <div style={{
      width: collapsed ? 56 : 260, minWidth: collapsed ? 56 : 260,
      height: "100%", background: "rgba(8,12,24,0.95)",
      borderRight: "1px solid rgba(255,255,255,0.07)",
      display: "flex", flexDirection: "column",
      transition: "width 0.25s cubic-bezier(.4,0,.2,1), min-width 0.25s cubic-bezier(.4,0,.2,1)",
      overflow: "hidden", flexShrink: 0,
    }}>
      <div style={{
        display: "flex", alignItems: "center", justifyContent: "space-between",
        padding: collapsed ? "16px 10px" : "16px 14px",
        borderBottom: "1px solid rgba(255,255,255,0.06)", gap: 8,
      }}>
        {!collapsed && (
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{ fontSize: 16 }}>🗂️</span>
            <span style={{ fontWeight: 700, fontSize: 13, color: "#94a3b8", letterSpacing: "0.05em", fontFamily: "'Space Mono',monospace" }}>
              HISTORY
            </span>
          </div>
        )}
        <button onClick={onToggle} style={{
          background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.1)",
          borderRadius: 8, width: 30, height: 30, cursor: "pointer",
          display: "flex", alignItems: "center", justifyContent: "center",
          color: "#64748b", fontSize: 14, flexShrink: 0, transition: "all 0.2s",
        }}
          onMouseOver={e => { e.currentTarget.style.color = "#22d3ee"; e.currentTarget.style.borderColor = "rgba(34,211,238,0.3)"; }}
          onMouseOut={e => { e.currentTarget.style.color = "#64748b"; e.currentTarget.style.borderColor = "rgba(255,255,255,0.1)"; }}
          title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >{collapsed ? "›" : "‹"}</button>
      </div>
      <div style={{ padding: collapsed ? "10px 8px" : "10px 10px" }}>
        <button onClick={onNew} style={{
          width: "100%", background: "linear-gradient(135deg,rgba(34,211,238,0.15),rgba(14,165,233,0.1))",
          border: "1px solid rgba(34,211,238,0.25)", borderRadius: 12,
          color: "#22d3ee", cursor: "pointer", fontWeight: 700,
          fontSize: 12, padding: collapsed ? "10px 0" : "10px 14px",
          display: "flex", alignItems: "center", justifyContent: collapsed ? "center" : "flex-start",
          gap: 8, transition: "all 0.2s", fontFamily: "'DM Sans',sans-serif",
        }}
          onMouseOver={e => { e.currentTarget.style.background = "linear-gradient(135deg,rgba(34,211,238,0.25),rgba(14,165,233,0.18))"; }}
          onMouseOut={e => { e.currentTarget.style.background = "linear-gradient(135deg,rgba(34,211,238,0.15),rgba(14,165,233,0.1))"; }}
          title="New Chat"
        >
          <span style={{ fontSize: 16 }}>✚</span>
          {!collapsed && "New Chat"}
        </button>
      </div>
      <div style={{ flex: 1, overflowY: "auto", padding: collapsed ? "4px 6px" : "4px 8px" }}>
        {sessions.length === 0 && !collapsed && (
          <div style={{ textAlign: "center", color: "#334155", fontSize: 12, marginTop: 24, fontFamily: "'Space Mono',monospace" }}>
            No chats yet
          </div>
        )}
        {sessions.map(s => (
          <div key={s.id} onClick={() => onSelect(s.id)} title={s.title} style={{
            display: "flex", alignItems: "center", gap: 8,
            padding: collapsed ? "10px 0" : "9px 10px",
            borderRadius: 10, cursor: "pointer", marginBottom: 2,
            background: s.id === activeId ? "rgba(34,211,238,0.1)" : "transparent",
            border: s.id === activeId ? "1px solid rgba(34,211,238,0.2)" : "1px solid transparent",
            transition: "all 0.15s", justifyContent: collapsed ? "center" : "flex-start",
          }}
            onMouseOver={e => { if (s.id !== activeId) e.currentTarget.style.background = "rgba(255,255,255,0.04)"; }}
            onMouseOut={e => { if (s.id !== activeId) e.currentTarget.style.background = "transparent"; }}
          >
            <span style={{ fontSize: 15, flexShrink: 0 }}>
              {s.severity === "Critical" ? "🚨" : s.severity === "High" ? "⛔" : s.severity === "Moderate" ? "⚠️" : "🧠"}
            </span>
            {!collapsed && (
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{
                  fontSize: 12, fontWeight: 600, color: s.id === activeId ? "#22d3ee" : "#94a3b8",
                  whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis",
                }}>{s.title}</div>
                <div style={{ fontSize: 10, color: "#334155", fontFamily: "'Space Mono',monospace", marginTop: 1 }}>
                  {s.date} · {s.turns} turns
                </div>
              </div>
            )}
            {!collapsed && (
              <button onClick={e => { e.stopPropagation(); onDelete(s.id); }} style={{
                background: "transparent", border: "none", cursor: "pointer",
                color: "#334155", fontSize: 14, padding: "2px 4px", borderRadius: 4,
                transition: "color 0.15s", flexShrink: 0,
              }}
                onMouseOver={e => { e.currentTarget.style.color = "#ef4444"; }}
                onMouseOut={e => { e.currentTarget.style.color = "#334155"; }}
                title="Delete chat"
              >×</button>
            )}
          </div>
        ))}
      </div>
      {!collapsed && (
        <div style={{
          padding: "10px 14px", borderTop: "1px solid rgba(255,255,255,0.06)",
          fontSize: 10, color: "#1e293b", fontFamily: "'Space Mono',monospace",
          display: "flex", alignItems: "center", gap: 6,
        }}>
          <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#22d3ee", display: "inline-block", boxShadow: "0 0 5px #22d3ee" }} />
          Full context window active
        </div>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────
//  MIC BUTTON
// ─────────────────────────────────────────────
function MicButton({ isRecording, disabled, onPress }) {
  return (
    <button
      onClick={onPress}
      disabled={disabled && !isRecording}
      title={isRecording ? "Stop recording & send" : "Hold to speak"}
      style={{
        background: isRecording
          ? "linear-gradient(135deg,#ef4444,#dc2626)"
          : "linear-gradient(135deg,rgba(34,211,238,0.15),rgba(14,165,233,0.1))",
        border: isRecording
          ? "1px solid rgba(239,68,68,0.5)"
          : "1px solid rgba(34,211,238,0.25)",
        borderRadius: 16,
        width: 46, height: 46,
        display: "flex", alignItems: "center", justifyContent: "center",
        cursor: "pointer", fontSize: 18, flexShrink: 0,
        transition: "all 0.2s cubic-bezier(.34,1.56,.64,1)",
        animation: isRecording ? "recordingPulse 1.2s ease-in-out infinite" : "none",
        boxShadow: isRecording ? "0 0 20px rgba(239,68,68,0.4)" : "0 0 12px rgba(34,211,238,0.15)",
      }}
    >
      {isRecording ? "⏹" : "🎤"}
    </button>
  );
}

// ─────────────────────────────────────────────
//  MAIN COMPONENT
// ─────────────────────────────────────────────
export default function ChatPage() {
  const bottomRef = useRef(null);

  // Sidebar
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [sessions, setSessions]                 = useState(() => loadSessions());
  const [activeSessionId, setActiveSessionId]   = useState(null);

  // Chat
  const [messages, setMessages]     = useState([welcomeMsg()]);
  const [history, setHistory]       = useState([]);
  const [initSymptom, setInitSymptom] = useState("");
  const [started, setStarted]       = useState(false);

  // Input
  const [symptom, setSymptom]   = useState("");
  const [loading, setLoading]   = useState(false);
  const [lastAiQuestion, setLastAiQuestion] = useState("");

  // UI panels
  const [showContext, setShowContext]   = useState(false);

  // Voice
  const [autoSpeak, setAutoSpeak]           = useState(true);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const { isRecording, isSpeaking, startRecording, stopRecording, speak, stopSpeaking } = useVoice({ autoSpeak });

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, loading]);
  useEffect(() => { saveSessions(sessions); }, [sessions]);

  function welcomeMsg() {
    return {
      role: "ai", type: "welcome",
      text: "Hello! I'm MediZen AI 🧠 Tell me what's going on — you can type or tap the mic to speak. I'll ask a few follow-up questions, then give you a detailed analysis.",
      time: now(),
    };
  }

  // ── Session management ──────────────────────
  const createNewSession = useCallback(() => {
    stopSpeaking();
    const id = uid();
    const session = { id, title: "New Chat", date: todayLabel(), turns: 0, severity: null, messages: [welcomeMsg()], history: [], initSymptom: "", started: false };
    setSessions(prev => [session, ...prev]);
    setActiveSessionId(id);
    setMessages([welcomeMsg()]);
    setHistory([]); setInitSymptom(""); setStarted(false); setSymptom(""); setLastAiQuestion("");
  }, [stopSpeaking]);

  const selectSession = useCallback((id) => {
    stopSpeaking();
    if (activeSessionId) {
      setSessions(prev => prev.map(s => s.id === activeSessionId ? { ...s, messages, history, initSymptom, started } : s));
    }
    const s = sessions.find(x => x.id === id);
    if (!s) return;
    setActiveSessionId(id);
    setMessages(s.messages || [welcomeMsg()]);
    setHistory(s.history || []);
    setInitSymptom(s.initSymptom || "");
    setStarted(s.started || false);
    setLastAiQuestion("");
  }, [activeSessionId, messages, history, initSymptom, started, sessions, stopSpeaking]);

  const deleteSession = useCallback((id) => {
    setSessions(prev => prev.filter(s => s.id !== id));
    if (activeSessionId === id) {
      setActiveSessionId(null); setMessages([welcomeMsg()]); setHistory([]);
      setInitSymptom(""); setStarted(false); setLastAiQuestion("");
    }
  }, [activeSessionId]);

  const syncSession = useCallback((newMessages, newHistory, newInitSymptom, newStarted, severity) => {
    if (!activeSessionId) return;
    setSessions(prev => prev.map(s => {
      if (s.id !== activeSessionId) return s;
      const firstUser = newMessages.find(m => m.role === "user");
      const title = firstUser ? firstUser.text.slice(0, 38) + (firstUser.text.length > 38 ? "…" : "") : s.title;
      return { ...s, title, turns: newMessages.filter(m => m.role === "user").length, messages: newMessages, history: newHistory, initSymptom: newInitSymptom, started: newStarted, severity: severity || s.severity };
    }));
  }, [activeSessionId]);

  // ── Voice mic handler ───────────────────────
  const handleMicPress = async () => {
    if (isRecording) {
      setIsTranscribing(true);
      const text = await stopRecording();
      setIsTranscribing(false);
      if (text.trim()) {
        setSymptom(text);
        // Auto-send after short delay so user can see the transcribed text
        setTimeout(() => send(text), 200);
      }
    } else {
      stopSpeaking();
      await startRecording();
    }
  };

  // ── Send ────────────────────────────────────
  const send = async (overrideText) => {
    const text = (overrideText || symptom).trim();
    if (!text || loading) return;

    if (started && lastAiQuestion && looksConfused(text, lastAiQuestion)) {
      setSymptom("");
      const clarifyMsg = { role: "ai", type: "clarify", question: lastAiQuestion, time: now() };
      const clarifyText = simplifyQuestion(lastAiQuestion);
      setMessages(prev => [...prev, { role: "user", text, time: now() }, clarifyMsg]);
      speak(clarifyText);
      return;
    }

    let sessionId = activeSessionId;
    if (!sessionId) {
      const id = uid();
      const session = { id, title: text.slice(0, 38) + (text.length > 38 ? "…" : ""), date: todayLabel(), turns: 0, severity: null, messages: [welcomeMsg()], history: [], initSymptom: "", started: false };
      setSessions(prev => [session, ...prev]);
      setActiveSessionId(id);
      sessionId = id;
    }

    setSymptom("");
    setLoading(true);
    stopSpeaking();

    const userMsg = { role: "user", text, time: now() };
    const newMessages = [...messages, userMsg];
    setMessages(newMessages);

    const newUserEntry = { role: "user", content: text };
    const currentInitSymptom = !started ? text : initSymptom;
    const newInitSymptom = !started ? text : initSymptom;
    const newStarted = true;
    const updatedHistory = [...history, newUserEntry];

    if (!started) setInitSymptom(text);
    setStarted(true);

    try {
      const res = await fetch(`${API_BASE}/symptom/followup`, {
        method: "POST",
        headers: headers(),
        body: JSON.stringify({
          symptoms: currentInitSymptom,
          conversation: updatedHistory.map(m => ({ role: m.role, content: m.content })),
        }),
      });

      if (!res.ok) throw Object.assign(new Error(), { status: res.status });

      const data = await res.json();
      const { is_done, question, final_analysis, is_emergency } = data;

      let aiMsg, aiEntry, finalSeverity = null;

      if (is_done && final_analysis) {
        const fa = final_analysis;
        finalSeverity = fa.severity || "Low";
        const parsed = {
          conditions: (fa.possible_conditions || []).map(c => {
            const idx = c.indexOf(":");
            return idx > 0 ? { name: c.slice(0, idx).trim(), desc: c.slice(idx + 1).trim() } : { name: c, desc: "" };
          }),
          remedies: (fa.remedies || []).map(r => {
            const idx = r.indexOf(":");
            return idx > 0 ? { title: r.slice(0, idx).trim(), tip: r.slice(idx + 1).trim() } : { title: r, tip: "" };
          }),
          whenDoctor: fa.when_to_see_doctor || "",
        };
        aiMsg = { role: "ai", type: "analysis", severity: fa.severity || "Low", isEmergency: is_emergency || fa.is_emergency || false, parsed, time: now() };
        aiEntry = { role: "assistant", content: `[Final analysis. Severity: ${fa.severity}]` };

        // Speak the final analysis summary
        const speechText = buildAnalysisSpeech(parsed, fa.severity, is_emergency || fa.is_emergency);
        speak(speechText);
      } else {
        aiMsg = { role: "ai", type: "question", text: question || "Could you tell me more?", time: now() };
        aiEntry = { role: "assistant", content: question || "Could you tell me more?" };
        setLastAiQuestion(question || "");

        // Speak the follow-up question
        speak(stripMarkdown(question || "Could you tell me more?"));
      }

      const finalMessages = [...newMessages, aiMsg];
      const finalHistory  = [...updatedHistory, aiEntry];
      setMessages(finalMessages);
      setHistory(finalHistory);
      syncSession(finalMessages, finalHistory, newInitSymptom, newStarted, finalSeverity);

    } catch (err) {
      const status = err?.status;
      const errText = status === 401
        ? "Authentication failed (401). Please log out and log back in."
        : status === 422
        ? "The server couldn't process that. Try rephrasing your message."
        : "Could not reach the server. Make sure your backend is running on port 8000.";
      const errMsg = { role: "ai", type: "error", text: errText, time: now() };
      const finalMessages = [...newMessages, errMsg];
      setMessages(finalMessages);
      syncSession(finalMessages, updatedHistory, newInitSymptom, newStarted, null);
    } finally {
      setLoading(false);
    }
  };

  const handleKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); }
  };

  return (
    <div style={{
      height: "100vh", display: "flex", flexDirection: "row",
      background: "linear-gradient(135deg,#0a0f1e 0%,#0d1525 50%,#0a0e1a 100%)",
      color: "#f1f5f9", fontFamily: "'DM Sans',sans-serif", overflow: "hidden",
    }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700;800;900&family=Space+Mono:wght@400;700&display=swap');
        *{box-sizing:border-box;margin:0;padding:0;}
        @keyframes typingBounce{0%,60%,100%{transform:translateY(0);opacity:.4}30%{transform:translateY(-6px);opacity:1}}
        @keyframes fadeSlideUp{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}
        @keyframes emergencyPulse{0%,100%{box-shadow:0 0 0 0 rgba(255,59,59,0.4)}50%{box-shadow:0 0 0 8px rgba(255,59,59,0)}}
        @keyframes recordingPulse{0%,100%{box-shadow:0 0 0 0 rgba(239,68,68,0.5)}50%{box-shadow:0 0 0 10px rgba(239,68,68,0)}}
        @keyframes speakingPulse{0%,100%{opacity:1}50%{opacity:0.5}}
        .msg-appear{animation:fadeSlideUp .35s cubic-bezier(.34,1.2,.64,1) both}
        .quick-chip{cursor:pointer;border:1px solid rgba(255,255,255,.08);border-radius:20px;padding:8px 14px;
          background:rgba(255,255,255,.04);color:#94a3b8;font-size:12px;font-weight:500;white-space:nowrap;
          transition:all .2s ease;display:flex;align-items:center;gap:6px;font-family:'DM Sans',sans-serif;}
        .quick-chip:hover{border-color:rgba(34,211,238,.4);color:#22d3ee;background:rgba(34,211,238,.06);transform:translateY(-2px);}
        .quick-chip:disabled{opacity:.4;cursor:not-allowed;transform:none;}
        .send-btn{background:linear-gradient(135deg,#22d3ee,#0ea5e9);border:none;border-radius:16px;
          width:46px;height:46px;display:flex;align-items:center;justify-content:center;cursor:pointer;
          font-size:18px;color:#000;box-shadow:0 0 20px rgba(34,211,238,.3);transition:all .2s cubic-bezier(.34,1.56,.64,1);flex-shrink:0;}
        .send-btn:hover{transform:scale(1.08);box-shadow:0 0 30px rgba(34,211,238,.45);}
        .send-btn:disabled{opacity:.4;cursor:not-allowed;transform:none;}
        textarea{background:transparent;border:none;outline:none;color:#f1f5f9;font-size:14px;
          font-family:'DM Sans',sans-serif;resize:none;flex:1;line-height:1.5;padding:4px 0;}
        textarea::placeholder{color:#475569;}
        ::-webkit-scrollbar{width:4px;}
        ::-webkit-scrollbar-thumb{background:rgba(255,255,255,.08);border-radius:2px;}
      `}</style>

      <Sidebar
        sessions={sessions} activeId={activeSessionId}
        onSelect={selectSession} onNew={createNewSession} onDelete={deleteSession}
        collapsed={sidebarCollapsed} onToggle={() => setSidebarCollapsed(v => !v)}
      />

      <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden", minWidth: 0 }}>

        {/* NAVBAR */}
        <nav style={{
          display: "flex", alignItems: "center", justifyContent: "space-between",
          padding: "12px 24px", borderBottom: "1px solid rgba(255,255,255,.07)",
          backdropFilter: "blur(12px)", background: "rgba(10,15,30,.8)", flexShrink: 0,
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div style={{
              width: 36, height: 36, borderRadius: 10,
              background: "linear-gradient(135deg,#22d3ee,#0ea5e9)",
              display: "flex", alignItems: "center", justifyContent: "center",
              fontSize: 17, boxShadow: "0 0 14px rgba(34,211,238,.3)",
            }}>🧠</div>
            <div>
              <div style={{ fontWeight: 800, fontSize: 15, letterSpacing: "-0.02em" }}>
                {activeSessionId ? (sessions.find(s => s.id === activeSessionId)?.title || "AI Symptom Chat") : "AI Symptom Chat"}
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 5, marginTop: 1 }}>
                <span style={{ width: 5, height: 5, borderRadius: "50%", background: "#22d3ee", display: "inline-block", boxShadow: "0 0 5px #22d3ee" }} />
                <span style={{ fontSize: 10, color: "#22d3ee", fontWeight: 600, letterSpacing: "0.06em" }}>LIVE AI ANALYSIS</span>
              </div>
            </div>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            {/* Voice auto-speak toggle */}
            <button
              onClick={() => { stopSpeaking(); setAutoSpeak(v => !v); }}
              title={autoSpeak ? "Voice replies ON — click to mute" : "Voice replies OFF — click to enable"}
              style={{
                background: autoSpeak ? "rgba(34,211,238,0.1)" : "rgba(255,255,255,0.04)",
                border: autoSpeak ? "1px solid rgba(34,211,238,0.3)" : "1px solid rgba(255,255,255,0.1)",
                color: autoSpeak ? "#22d3ee" : "#475569",
                borderRadius: 10, padding: "6px 12px", cursor: "pointer", fontSize: 11,
                fontWeight: 600, transition: "all .2s", fontFamily: "'Space Mono',monospace",
                display: "flex", alignItems: "center", gap: 5,
              }}
            >
              {autoSpeak ? "🔊 Voice ON" : "🔇 Voice OFF"}
            </button>

            {/* Stop speaking button — only visible when speaking */}
            {isSpeaking && (
              <button onClick={stopSpeaking} style={{
                background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.3)",
                color: "#ef4444", borderRadius: 10, padding: "6px 12px",
                cursor: "pointer", fontSize: 11, fontWeight: 600,
                animation: "speakingPulse 1.5s ease-in-out infinite",
                fontFamily: "'Space Mono',monospace",
              }}>
                ⏹ Stop
              </button>
            )}

            <button onClick={() => setShowContext(v => !v)} style={{
              background: showContext ? "rgba(167,139,250,0.15)" : "rgba(255,255,255,.04)",
              border: showContext ? "1px solid rgba(167,139,250,0.35)" : "1px solid rgba(255,255,255,.1)",
              color: showContext ? "#a78bfa" : "#64748b",
              borderRadius: 10, padding: "6px 12px", cursor: "pointer", fontSize: 11,
              fontWeight: 600, transition: "all .2s", fontFamily: "'Space Mono',monospace",
              display: "flex", alignItems: "center", gap: 5,
            }}>
              🧵 Context ({history.length})
            </button>

            <div style={{
              background: "rgba(34,211,238,.06)", border: "1px solid rgba(34,211,238,.15)",
              borderRadius: 10, padding: "5px 12px", fontSize: 11,
              color: "#64748b", fontFamily: "'Space Mono',monospace",
            }}>
              {messages.filter(m => m.role === "user").length} turns
            </div>

            <button onClick={createNewSession} style={{
              background: "rgba(255,255,255,.04)", border: "1px solid rgba(255,255,255,.1)",
              color: "#64748b", borderRadius: 10, padding: "6px 12px",
              cursor: "pointer", fontSize: 11, fontWeight: 600,
              transition: "all .2s", fontFamily: "'DM Sans',sans-serif",
              display: "flex", alignItems: "center", gap: 5,
            }}
              onMouseOver={e => { e.currentTarget.style.color = "#f1f5f9"; e.currentTarget.style.borderColor = "rgba(255,255,255,.25)"; }}
              onMouseOut={e => { e.currentTarget.style.color = "#64748b"; e.currentTarget.style.borderColor = "rgba(255,255,255,.1)"; }}
            >↺ New Chat</button>
          </div>
        </nav>

        {/* CONTEXT PANEL */}
        {showContext && (
          <div style={{
            background: "rgba(15,20,40,0.95)", borderBottom: "1px solid rgba(167,139,250,0.15)",
            padding: "12px 24px", maxHeight: 180, overflowY: "auto", flexShrink: 0,
            animation: "fadeSlideUp 0.2s ease",
          }}>
            <div style={{ fontSize: 10, color: "#475569", fontFamily: "'Space Mono',monospace", marginBottom: 8, letterSpacing: "0.08em" }}>
              🧵 CONTEXT WINDOW — {history.length} messages sent to API each turn
            </div>
            {history.length === 0 ? (
              <div style={{ color: "#334155", fontSize: 12 }}>No history yet. Send your first message.</div>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                {history.map((h, i) => (
                  <div key={i} style={{
                    display: "flex", gap: 8, fontSize: 11,
                    color: h.role === "user" ? "#a78bfa" : "#22d3ee",
                    padding: "3px 0", borderBottom: "1px solid rgba(255,255,255,0.03)",
                  }}>
                    <span style={{ fontFamily: "'Space Mono',monospace", minWidth: 70, flexShrink: 0 }}>
                      [{h.role === "user" ? "USER" : "ASST"}]
                    </span>
                    <span style={{ color: "#64748b", lineHeight: 1.5 }}>
                      {h.content.length > 120 ? h.content.slice(0, 120) + "…" : h.content}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* MESSAGES */}
        <div style={{ flex: 1, overflowY: "auto", padding: "24px 0", display: "flex", flexDirection: "column" }}>
          <div style={{
            maxWidth: 780, width: "100%", margin: "0 auto", padding: "0 20px",
            display: "flex", flexDirection: "column", gap: 18,
          }}>
            {messages.map((msg, i) => (
              <div key={i} className="msg-appear" style={{
                display: "flex",
                flexDirection: msg.role === "user" ? "row-reverse" : "row",
                alignItems: "flex-start", gap: 10,
              }}>
                <div style={{
                  width: 34, height: 34, borderRadius: 10, flexShrink: 0,
                  display: "flex", alignItems: "center", justifyContent: "center", fontSize: 15,
                  background: msg.role === "ai" ? "linear-gradient(135deg,#22d3ee20,#0ea5e920)" : "linear-gradient(135deg,#a78bfa20,#6366f120)",
                  border: msg.role === "ai" ? "1px solid rgba(34,211,238,.2)" : "1px solid rgba(167,139,250,.2)",
                }}>
                  {msg.role === "ai" ? "🧠" : "👤"}
                </div>
                <div style={{
                  maxWidth: "76%", display: "flex", flexDirection: "column", gap: 4,
                  alignItems: msg.role === "user" ? "flex-end" : "flex-start",
                }}>
                  {msg.role === "user" ? (
                    <div style={{
                      background: "linear-gradient(135deg,rgba(167,139,250,.18),rgba(99,102,241,.12))",
                      border: "1px solid rgba(167,139,250,.2)", borderRadius: "20px 4px 20px 20px",
                      padding: "12px 16px", fontSize: 14, lineHeight: 1.6, color: "#e2e8f0",
                    }}>{msg.text}</div>
                  ) : (
                    <AIBubble msg={msg} />
                  )}
                  <div style={{ fontSize: 10, color: "#334155", fontFamily: "'Space Mono',monospace" }}>{msg.time}</div>
                </div>
              </div>
            ))}

            {loading && (
              <div className="msg-appear" style={{ display: "flex", alignItems: "flex-start", gap: 10 }}>
                <div style={{
                  width: 34, height: 34, borderRadius: 10, flexShrink: 0,
                  display: "flex", alignItems: "center", justifyContent: "center", fontSize: 15,
                  background: "linear-gradient(135deg,#22d3ee20,#0ea5e920)",
                  border: "1px solid rgba(34,211,238,.2)",
                }}>🧠</div>
                <div style={{ background: "rgba(255,255,255,.04)", border: "1px solid rgba(255,255,255,.08)", borderRadius: "4px 20px 20px 20px" }}>
                  <TypingIndicator />
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        </div>

        {/* QUESTION REMINDER BAR */}
        {lastAiQuestion && !loading && (
          <div style={{
            borderTop: "1px solid rgba(34,211,238,0.1)", background: "rgba(34,211,238,0.04)",
            padding: "8px 0", flexShrink: 0, animation: "fadeSlideUp 0.3s ease",
          }}>
            <div style={{ maxWidth: 780, margin: "0 auto", padding: "0 20px", display: "flex", alignItems: "center", gap: 10 }}>
              <span style={{ fontSize: 10, fontFamily: "'Space Mono',monospace", color: "#22d3ee", letterSpacing: "0.07em", flexShrink: 0 }}>
                💬 WAITING FOR:
              </span>
              <span style={{ fontSize: 12, color: "#94a3b8", flex: 1, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                {lastAiQuestion}
              </span>
              {/* Re-speak button */}
              <button
                onClick={() => speak(stripMarkdown(lastAiQuestion))}
                style={{
                  background: "rgba(34,211,238,0.08)", border: "1px solid rgba(34,211,238,0.2)",
                  color: "#22d3ee", borderRadius: 8, padding: "4px 10px",
                  fontSize: 11, fontWeight: 600, cursor: "pointer", flexShrink: 0,
                  fontFamily: "'DM Sans',sans-serif", transition: "all 0.2s",
                }}
                onMouseOver={e => { e.currentTarget.style.background = "rgba(34,211,238,0.18)"; }}
                onMouseOut={e => { e.currentTarget.style.background = "rgba(34,211,238,0.08)"; }}
                title="Hear the question again"
              >🔊 Repeat</button>
              <button
                onClick={() => {
                  setSymptom("");
                  const clarifyMsg = { role: "ai", type: "clarify", question: lastAiQuestion, time: now() };
                  setMessages(prev => [...prev, clarifyMsg]);
                  speak(simplifyQuestion(lastAiQuestion));
                }}
                style={{
                  background: "rgba(245,158,11,0.1)", border: "1px solid rgba(245,158,11,0.25)",
                  color: "#fbbf24", borderRadius: 8, padding: "4px 10px",
                  fontSize: 11, fontWeight: 600, cursor: "pointer", flexShrink: 0,
                  fontFamily: "'DM Sans',sans-serif", transition: "all 0.2s",
                }}
                onMouseOver={e => { e.currentTarget.style.background = "rgba(245,158,11,0.2)"; }}
                onMouseOut={e => { e.currentTarget.style.background = "rgba(245,158,11,0.1)"; }}
                title="Get a simpler version of this question"
              >💡 Simplify</button>
            </div>
          </div>
        )}

        {/* VOICE STATUS BAR */}
        {(isRecording || isTranscribing || isSpeaking) && (
          <div style={{
            background: isRecording
              ? "rgba(239,68,68,0.08)"
              : isSpeaking
              ? "rgba(34,211,238,0.06)"
              : "rgba(167,139,250,0.06)",
            borderTop: isRecording
              ? "1px solid rgba(239,68,68,0.2)"
              : isSpeaking
              ? "1px solid rgba(34,211,238,0.15)"
              : "1px solid rgba(167,139,250,0.15)",
            padding: "6px 0", flexShrink: 0,
            display: "flex", alignItems: "center", justifyContent: "center", gap: 8,
          }}>
            {isRecording && (
              <>
                <span style={{ width: 8, height: 8, borderRadius: "50%", background: "#ef4444", animation: "recordingPulse 1.2s ease-in-out infinite" }} />
                <span style={{ fontSize: 12, color: "#ef4444", fontFamily: "'Space Mono',monospace", letterSpacing: "0.05em" }}>
                  LISTENING… tap ⏹ to send
                </span>
              </>
            )}
            {isTranscribing && !isRecording && (
              <>
                <span style={{ fontSize: 12, color: "#a78bfa", fontFamily: "'Space Mono',monospace", letterSpacing: "0.05em" }}>
                  ✦ Transcribing…
                </span>
              </>
            )}
            {isSpeaking && !isRecording && (
              <>
                <span style={{ fontSize: 12, color: "#22d3ee", fontFamily: "'Space Mono',monospace", letterSpacing: "0.05em", animation: "speakingPulse 1.5s ease-in-out infinite" }}>
                  🔊 SPEAKING…
                </span>
                <button onClick={stopSpeaking} style={{
                  background: "transparent", border: "1px solid rgba(34,211,238,0.2)",
                  color: "#22d3ee", borderRadius: 6, padding: "2px 8px",
                  fontSize: 10, cursor: "pointer", fontFamily: "'Space Mono',monospace",
                }}>stop</button>
              </>
            )}
          </div>
        )}

        {/* QUICK PROMPTS */}
        <div style={{ borderTop: "1px solid rgba(255,255,255,.06)", padding: "10px 0 0", flexShrink: 0, background: "rgba(10,15,30,.5)", backdropFilter: "blur(8px)" }}>
          <div style={{ maxWidth: 780, margin: "0 auto", padding: "0 20px" }}>
            <div style={{ fontSize: 10, color: "#334155", marginBottom: 6, fontFamily: "'Space Mono',monospace", letterSpacing: "0.06em" }}>QUICK PROMPTS</div>
            <div style={{ display: "flex", gap: 6, overflowX: "auto", paddingBottom: 10 }}>
              {lastAiQuestion && (
                <button className="quick-chip" disabled={loading}
                  onClick={() => {
                    const clarifyMsg = { role: "ai", type: "clarify", question: lastAiQuestion, time: now() };
                    setMessages(prev => [...prev, clarifyMsg]);
                    speak(simplifyQuestion(lastAiQuestion));
                  }}
                  style={{ borderColor: "rgba(245,158,11,0.35)", color: "#fbbf24", background: "rgba(245,158,11,0.07)" }}
                >
                  <span>🤔</span> I don't understand
                </button>
              )}
              {QUICK_PROMPTS.map(p => (
                <button key={p.label} className="quick-chip" onClick={() => send(p.text)} disabled={loading}>
                  <span>{p.icon}</span>{p.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* INPUT BAR */}
        <div style={{ padding: "10px 0 18px", flexShrink: 0, background: "rgba(10,15,30,.8)", backdropFilter: "blur(12px)" }}>
          <div style={{ maxWidth: 780, margin: "0 auto", padding: "0 20px" }}>
            <div style={{
              display: "flex", alignItems: "flex-end", gap: 10,
              background: "rgba(255,255,255,.05)", border: "1px solid rgba(255,255,255,.1)",
              borderRadius: 20, padding: "10px 12px", transition: "border-color .2s",
            }}
              onFocusCapture={e => { e.currentTarget.style.borderColor = "rgba(34,211,238,.35)"; }}
              onBlurCapture={e => { e.currentTarget.style.borderColor = "rgba(255,255,255,.1)"; }}
            >
              {/* Mic button */}
              <MicButton
                isRecording={isRecording}
                disabled={loading || isTranscribing}
                onPress={handleMicPress}
              />

              <textarea rows={2}
                placeholder={
                  isRecording ? "Listening… tap ⏹ to finish"
                  : isTranscribing ? "Transcribing your voice…"
                  : "Describe your symptoms, or tap 🎤 to speak…"
                }
                value={symptom}
                onChange={e => setSymptom(e.target.value)}
                onKeyDown={handleKey}
                disabled={isRecording || isTranscribing}
                style={{ maxHeight: 120, opacity: (isRecording || isTranscribing) ? 0.5 : 1 }}
              />

              <button className="send-btn" onClick={() => send()} disabled={loading || !symptom.trim() || isRecording || isTranscribing} title="Send (Enter)">
                {loading ? "⏳" : isTranscribing ? "✦" : "↑"}
              </button>
            </div>

            <div style={{ textAlign: "center", fontSize: 10, color: "#1e293b", marginTop: 6, fontFamily: "'Space Mono',monospace" }}>
              Enter to send · Shift+Enter for new line · 🎤 tap to speak · Not a substitute for professional medical advice
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}