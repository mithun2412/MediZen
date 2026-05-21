import { useState, useEffect, useRef } from "react";
import api from "./api";
import Dashboard from "./Dashboard";
import HospitalFinder from "./HospitalFinder";
import { generatePDFReport } from "./PDFReport";

function getSeverityStyle(severity) {
  switch (severity) {
    case "Critical": return { bg: "bg-red-100", border: "border-red-500", text: "text-red-700", dot: "bg-red-500" };
    case "High":     return { bg: "bg-orange-100", border: "border-orange-400", text: "text-orange-700", dot: "bg-orange-500" };
    case "Moderate": return { bg: "bg-yellow-100", border: "border-yellow-400", text: "text-yellow-700", dot: "bg-yellow-500" };
    default:         return { bg: "bg-green-100", border: "border-green-400", text: "text-green-700", dot: "bg-green-500" };
  }
}

// ─── Auth Page ────────────────────────────────────────────────────────────────
function AuthPage({ onLogin }) {
  const [isLogin, setIsLogin] = useState(true);
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handle = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const submit = async () => {
    setError(""); setLoading(true);
    try {
      const url = isLogin ? "/auth/login" : "/auth/signup";
      const body = isLogin
        ? { email: form.email, password: form.password }
        : { name: form.name, email: form.email, password: form.password };
      const res = await api.post(url, body);
      localStorage.setItem("token", res.data.access_token);
      localStorage.setItem("user_name", res.data.user_name);
      onLogin(res.data.user_name);
    } catch (err) {
      setError(err.response?.data?.detail || "Something went wrong.");
    } finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md">
        <div className="text-center mb-6">
          <h1 className="text-3xl font-bold text-indigo-700">🏥 MediVoice AI</h1>
          <p className="text-gray-500 mt-1 text-sm">AI-Powered Healthcare Assistant</p>
        </div>
        <div className="flex bg-gray-100 rounded-xl p-1 mb-6">
          <button onClick={() => { setIsLogin(true); setError(""); }}
            className={`flex-1 py-2 rounded-lg font-semibold text-sm transition ${isLogin ? "bg-white shadow text-indigo-700" : "text-gray-500"}`}>
            Login
          </button>
          <button onClick={() => { setIsLogin(false); setError(""); }}
            className={`flex-1 py-2 rounded-lg font-semibold text-sm transition ${!isLogin ? "bg-white shadow text-indigo-700" : "text-gray-500"}`}>
            Sign Up
          </button>
        </div>
        <div className="space-y-4">
          {!isLogin && (
            <input name="name" placeholder="Full Name" value={form.name} onChange={handle}
              className="w-full border border-gray-300 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400" />
          )}
          <input name="email" type="email" placeholder="Email Address" value={form.email} onChange={handle}
            className="w-full border border-gray-300 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400" />
          <input name="password" type="password" placeholder="Password" value={form.password} onChange={handle}
            onKeyDown={(e) => e.key === "Enter" && submit()}
            className="w-full border border-gray-300 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400" />
        </div>
        {error && <p className="text-red-500 text-sm mt-3">⚠️ {error}</p>}
        <button onClick={submit} disabled={loading}
          className="w-full mt-5 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 rounded-xl transition disabled:opacity-50">
          {loading ? "Please wait..." : isLogin ? "Login" : "Create Account"}
        </button>
        <p className="text-center text-gray-400 text-xs mt-4">
          {isLogin ? "No account? " : "Already have an account? "}
          <button onClick={() => { setIsLogin(!isLogin); setError(""); }}
            className="text-indigo-500 underline">{isLogin ? "Sign Up" : "Login"}</button>
        </p>
      </div>
    </div>
  );
}

// ─── Emergency Banner ─────────────────────────────────────────────────────────
function EmergencyBanner() {
  return (
    <div className="bg-red-600 text-white rounded-2xl p-6 mb-6 text-center shadow-lg animate-pulse">
      <p className="text-3xl mb-2">🚨</p>
      <h2 className="text-2xl font-bold mb-1">EMERGENCY DETECTED</h2>
      <p className="text-sm mb-4 opacity-90">
        Your symptoms may require <strong>immediate medical attention.</strong>
      </p>
      <div className="flex gap-3 justify-center flex-wrap">
        <a href="tel:112" className="bg-white text-red-600 font-bold px-6 py-3 rounded-xl hover:bg-red-50 transition text-sm">
          📞 Call 112 Now
        </a>
        <a href="tel:108" className="bg-white text-red-600 font-bold px-6 py-3 rounded-xl hover:bg-red-50 transition text-sm">
          🚑 Call 108 (Ambulance)
        </a>
        <a href="https://www.google.com/maps/search/hospital+near+me"
          target="_blank" rel="noreferrer"
          className="bg-red-700 text-white font-bold px-6 py-3 rounded-xl hover:bg-red-800 transition text-sm">
          🏥 Find Nearest Hospital
        </a>
      </div>
    </div>
  );
}

// ─── History Page ─────────────────────────────────────────────────────────────
function HistoryPage() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState("");
  const user = localStorage.getItem("user_name") || "User";

  const fetchHistory = async () => {
    try {
      const res = await api.get("/history");
      setHistory(res.data);
    } catch (err) {
      setError("Failed to load history. " + (err.response?.data?.detail || ""));
    } finally { setLoading(false); }
  };

  useEffect(() => { fetchHistory(); }, []);

  const deleteRecord = async (id) => {
    try {
      await api.delete(`/history/${id}`);
      setHistory(history.filter(h => h.id !== id));
    } catch { alert("Failed to delete record."); }
  };

  if (loading) return (
    <div className="text-center text-gray-400 py-12">
      <p className="text-4xl mb-3">⏳</p>
      <p>Loading history...</p>
    </div>
  );

  if (error) return (
    <div className="text-center text-red-400 py-12">
      <p className="text-4xl mb-3">⚠️</p><p>{error}</p>
    </div>
  );

  if (history.length === 0) return (
    <div className="text-center text-gray-400 py-12">
      <p className="text-4xl mb-3">📋</p>
      <p>No symptom history yet.</p>
      <p className="text-sm mt-1">Analyze your first symptom to see it here.</p>
    </div>
  );

  return (
    <div>
      {/* Header + PDF Button */}
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-gray-700 font-bold text-lg">Your History</h2>
        <button
          onClick={() => generatePDFReport(user, history)}
          className="bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold px-4 py-2 rounded-xl transition flex items-center gap-2">
          📄 Download PDF
        </button>
      </div>

      {/* History Cards */}
      <div className="space-y-4">
        {history.map(item => {
          const s = getSeverityStyle(item.severity);
          return (
            <div key={item.id}
              className={`bg-white rounded-2xl shadow p-5 ${item.severity === "Critical" ? "border-2 border-red-400" : ""}`}>
              <div className="flex justify-between items-start mb-3">
                <div>
                  {item.severity === "Critical" && (
                    <span className="text-xs bg-red-100 text-red-600 font-bold px-2 py-1 rounded-full mb-2 inline-block">
                      🚨 Emergency Record
                    </span>
                  )}
                  <p className="font-semibold text-gray-800 text-sm">"{item.symptom}"</p>
                  <p className="text-gray-400 text-xs mt-1">
                    {new Date(item.created_at).toLocaleString()}
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`text-xs font-bold px-3 py-1 rounded-full border ${s.bg} ${s.text} ${s.border}`}>
                    {item.severity}
                  </span>
                  <button onClick={() => deleteRecord(item.id)}
                    className="text-gray-300 hover:text-red-400 transition text-lg leading-none">✕</button>
                </div>
              </div>
              <div className="bg-gray-50 rounded-xl p-4 text-gray-600 text-xs leading-relaxed whitespace-pre-wrap max-h-40 overflow-y-auto">
                {item.analysis}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ─── Symptom Chat ─────────────────────────────────────────────────────────────
function SymptomChat({ onNavigateHistory, onAnalysisComplete }) {
  const [mode, setMode]         = useState("quick");
  const [symptom, setSymptom]   = useState("");
  const [error, setError]       = useState("");
  const [result, setResult]     = useState(null);
  const [loadingQuick, setLoadingQuick] = useState(false);

  // Chat states
  const [chatPhase, setChatPhase]   = useState("idle");
  const [messages, setMessages]     = useState([]);
  const [conversation, setConversation] = useState([]);
  const [userInput, setUserInput]   = useState("");
  const [loadingChat, setLoadingChat] = useState(false);
  const [finalResult, setFinalResult] = useState(null);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleQuickAnalyze = async () => {
    if (!symptom.trim()) { setError("Please enter symptoms."); return; }
    setLoadingQuick(true); setError(""); setResult(null);
    try {
      const res = await api.post("/analyze", { symptom });
      setResult(res.data);
      onAnalysisComplete?.(symptom);
    } catch (err) {
      setError(err.response?.data?.detail || "Analysis failed.");
    } finally { setLoadingQuick(false); }
  };

  const callFollowup = async (symp, convo) => {
    try {
      const res = await api.post("/symptom/followup", { symptoms: symp, conversation: convo });
      return res.data;
    } catch (err) {
      setError(err.response?.data?.detail || "Follow-up failed.");
      return null;
    }
  };

  const handleChatStart = async () => {
    if (!symptom.trim()) { setError("Please enter symptoms."); return; }
    setChatPhase("chatting");
    setMessages([{ from: "user", text: symptom }]);
    setLoadingChat(true);
    const data = await callFollowup(symptom, []);
    setLoadingChat(false);
    handleChatResponse(data, []);
  };

  const handleChatSend = async () => {
    if (!userInput.trim()) return;
    const userMsg = { role: "user", content: userInput };
    const newConvo = [...conversation, userMsg];
    setMessages(prev => [...prev, { from: "user", text: userInput }]);
    setUserInput("");
    setConversation(newConvo);
    setLoadingChat(true);
    const data = await callFollowup(symptom, newConvo);
    setLoadingChat(false);
    handleChatResponse(data, newConvo);
  };

  const handleChatResponse = (data, convo) => {
    if (!data) return;
    if (data.is_done && data.final_analysis) {
      setMessages(prev => [...prev, { from: "ai", text: "I have enough information. Here's your analysis 👇" }]);
      setFinalResult(data.final_analysis);
      onAnalysisComplete?.(symptom);
      setChatPhase("done");
    } else if (data.question) {
      setMessages(prev => [...prev, { from: "ai", text: data.question }]);
      setConversation([...convo, { role: "assistant", content: data.question }]);
    }
  };

  const s = result ? getSeverityStyle(result.severity) : null;

  return (
    <div>
      {result?.is_emergency && <EmergencyBanner />}

      {/* Mode Switch */}
      <div className="flex bg-white rounded-2xl shadow p-1 mb-4">
        <button onClick={() => setMode("quick")}
          className={`flex-1 py-2 rounded-xl text-sm font-semibold transition ${mode === "quick" ? "bg-indigo-600 text-white" : "text-gray-500"}`}>
          ⚡ Quick Analysis
        </button>
        <button onClick={() => setMode("chat")}
          className={`flex-1 py-2 rounded-xl text-sm font-semibold transition ${mode === "chat" ? "bg-indigo-600 text-white" : "text-gray-500"}`}>
          🤖 AI Chat
        </button>
      </div>

      {/* Quick Mode */}
      {mode === "quick" && (
        <>
          <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
            <label className="block text-gray-700 font-semibold mb-2">Describe Your Symptoms</label>
            <textarea rows={4}
              placeholder="e.g. fever, headache, body pain since 2 days..."
              value={symptom}
              onChange={(e) => setSymptom(e.target.value)}
              className="w-full border border-gray-300 rounded-xl p-4 text-gray-700 resize-none focus:outline-none focus:ring-2 focus:ring-indigo-400" />
            <div className="flex gap-3 mt-4">
              <button onClick={handleQuickAnalyze} disabled={loadingQuick}
                className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 rounded-xl transition disabled:opacity-50">
                {loadingQuick ? "⏳ Analyzing..." : "🔍 Analyze Symptoms"}
              </button>
              <button onClick={() => { setSymptom(""); setResult(null); setError(""); }}
                className="px-5 bg-gray-100 hover:bg-gray-200 text-gray-600 font-semibold py-3 rounded-xl transition">
                Clear
              </button>
            </div>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-300 text-red-700 rounded-xl p-4 mb-6">⚠️ {error}</div>
          )}

          {result && (
            <div className="bg-white rounded-2xl shadow-lg p-6">
              <div className={`flex items-center gap-3 p-4 rounded-xl border-2 mb-5 ${s.bg} ${s.border}`}>
                <span className={`w-4 h-4 rounded-full ${s.dot}`}></span>
                <span className={`font-bold text-lg ${s.text}`}>
                  {result.severity === "Critical" ? "🚨" :
                   result.severity === "High"     ? "⚠️" :
                   result.severity === "Moderate" ? "💛" : "✅"} Severity: {result.severity}
                </span>
              </div>
              <h2 className="text-gray-800 font-bold text-xl mb-3">🤖 AI Medical Analysis</h2>
              <div className="bg-gray-50 rounded-xl p-5 text-gray-700 leading-relaxed whitespace-pre-wrap text-sm mb-4">
                {result.analysis}
              </div>
              {result.remedies?.length > 0 && (
                <div className="mb-4">
                  <h3 className="font-semibold text-gray-700 mb-2">💊 Remedies</h3>
                  <ul className="space-y-1">
                    {result.remedies.map((r, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-gray-600">
                        <span className="text-indigo-400 mt-0.5">•</span>{r}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              {result.when_to_see_doctor && (
                <div className="bg-indigo-50 border-l-4 border-indigo-400 rounded-xl p-4 mb-4">
                  <p className="text-sm font-semibold text-indigo-700 mb-1">👨‍⚕️ When to See a Doctor</p>
                  <p className="text-sm text-indigo-600">{result.when_to_see_doctor}</p>
                </div>
              )}
              <button onClick={() => onNavigateHistory()}
                className="text-indigo-500 text-sm underline">
                View in history →
              </button>
            </div>
          )}
        </>
      )}

      {/* Chat Mode */}
      {mode === "chat" && (
        <>
          {chatPhase === "idle" && (
            <div className="bg-white rounded-2xl shadow-lg p-6">
              <label className="block text-gray-700 font-semibold mb-2">Describe Your Symptoms</label>
              <textarea rows={3}
                placeholder="Describe symptoms to start AI consultation..."
                value={symptom}
                onChange={(e) => setSymptom(e.target.value)}
                className="w-full border border-gray-300 rounded-xl p-4 text-gray-700 resize-none focus:outline-none focus:ring-2 focus:ring-indigo-400" />
              {error && <p className="text-red-500 text-sm mt-2">⚠️ {error}</p>}
              <button onClick={handleChatStart}
                className="w-full mt-4 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 rounded-xl transition">
                🤖 Start AI Consultation
              </button>
            </div>
          )}

          {(chatPhase === "chatting" || chatPhase === "done") && (
            <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
              <div className="h-96 overflow-y-auto p-4 flex flex-col gap-3">
                {messages.map((msg, i) => (
                  <div key={i} className={`flex ${msg.from === "user" ? "justify-end" : "justify-start"}`}>
                    <div className={`max-w-xs px-4 py-2 rounded-2xl text-sm ${
                      msg.from === "user" ? "bg-indigo-600 text-white" : "bg-gray-100 text-gray-800"}`}>
                      {msg.text}
                    </div>
                  </div>
                ))}
                {loadingChat && (
                  <div className="flex justify-start">
                    <div className="bg-gray-100 px-4 py-2 rounded-2xl text-sm text-gray-500 animate-pulse">
                      AI is thinking...
                    </div>
                  </div>
                )}
                {finalResult && (
                  <div className="bg-gray-50 rounded-2xl p-4 mt-3 border border-gray-200">
                    <h3 className="font-bold mb-2 text-gray-700">📋 Final Analysis</h3>
                    <p className="text-sm mb-2 font-semibold">Severity: {finalResult.severity}</p>
                    <p className="text-sm whitespace-pre-wrap text-gray-600">{finalResult.analysis}</p>
                  </div>
                )}
                <div ref={bottomRef} />
              </div>
              {chatPhase === "chatting" && (
                <div className="border-t p-3 flex gap-2">
                  <input value={userInput}
                    onChange={(e) => setUserInput(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleChatSend()}
                    placeholder="Type your answer..."
                    className="flex-1 border border-gray-200 rounded-2xl px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300" />
                  <button onClick={handleChatSend}
                    className="bg-indigo-600 hover:bg-indigo-700 text-white px-5 rounded-2xl transition">
                    Send
                  </button>
                </div>
              )}
              {chatPhase === "done" && (
                <div className="border-t p-3 text-center">
                  <button onClick={() => { setChatPhase("idle"); setMessages([]); setFinalResult(null); setSymptom(""); }}
                    className="text-indigo-500 text-sm underline">
                    Start new consultation
                  </button>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}

// ─── Main App ─────────────────────────────────────────────────────────────────
export default function App() {
  const [user, setUser]           = useState(null);
  const [page, setPage]           = useState("analyze");
  const [lastDisease, setLastDisease] = useState("");

  useEffect(() => {
    const n = localStorage.getItem("user_name");
    const t = localStorage.getItem("token");
    if (n && t) setUser(n);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user_name");
    setUser(null); setPage("analyze");
  };

  if (!user) return <AuthPage onLogin={setUser} />;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-2xl mx-auto">

        {/* Header */}
        <div className="flex justify-between items-center py-6">
          <div>
            <h1 className="text-2xl font-bold text-indigo-700">🏥 MediVoice AI</h1>
            <p className="text-gray-500 text-sm">Welcome, {user} 👋</p>
          </div>
          <button onClick={handleLogout}
            className="text-sm text-gray-400 hover:text-red-400 transition border border-gray-200 px-4 py-2 rounded-xl">
            Logout
          </button>
        </div>

        {/* Nav Tabs */}
        <div className="flex bg-white rounded-2xl shadow p-1 mb-6">
          <button onClick={() => setPage("analyze")}
            className={`flex-1 py-2 rounded-xl font-semibold text-sm transition ${page === "analyze" ? "bg-indigo-600 text-white" : "text-gray-500 hover:text-indigo-600"}`}>
            🔍 Analyze
          </button>
          <button onClick={() => setPage("dashboard")}
            className={`flex-1 py-2 rounded-xl font-semibold text-sm transition ${page === "dashboard" ? "bg-indigo-600 text-white" : "text-gray-500 hover:text-indigo-600"}`}>
            📊 Dashboard
          </button>
          <button onClick={() => setPage("history")}
            className={`flex-1 py-2 rounded-xl font-semibold text-sm transition ${page === "history" ? "bg-indigo-600 text-white" : "text-gray-500 hover:text-indigo-600"}`}>
            📋 History
          </button>
          <button onClick={() => setPage("hospitals")}
            className={`flex-1 py-2 rounded-xl font-semibold text-sm transition ${page === "hospitals" ? "bg-indigo-600 text-white" : "text-gray-500 hover:text-indigo-600"}`}>
            🏥 Hospitals
          </button>
        </div>

        {/* Pages */}
        {page === "analyze"   && (
          <SymptomChat
            onNavigateHistory={() => setPage("history")}
            onAnalysisComplete={(disease) => setLastDisease(disease)}
          />
        )}
        {page === "dashboard" && <Dashboard />}
        {page === "history"   && <HistoryPage />}
        {page === "hospitals" && <HospitalFinder disease={lastDisease} />}

        <p className="text-center text-gray-400 text-xs mt-8 pb-6">
          ⚠️ MediVoice AI is for informational purposes only. Not a substitute for professional medical advice.
        </p>
      </div>
    </div>
  );
}