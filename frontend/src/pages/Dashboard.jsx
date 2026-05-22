import { useState, useEffect } from "react";
import { getHealthInsights } from "../api/health";
import { Link, useNavigate } from "react-router-dom";

// Mock auth — replace with your real auth context/hook
function useAuth() {
  const user = JSON.parse(localStorage.getItem("user") || "null");
  return { user: user || { name: "Alex Johnson", email: "alex@example.com" } };
}




const features = [
  {
    id: "chat",
    icon: "🧠",
    label: "AI Chat",
    sublabel: "Symptom Analysis",
    desc: "Describe your symptoms and get intelligent AI-powered health insights instantly.",
    accent: "#22d3ee",
    glow: "rgba(34,211,238,0.18)",
    path: "/chat",
    stat: "1.2K analyzed",
    statLabel: "Total Symptoms",
    badge: "Live AI",
  },
  {
    id: "reminders",
    icon: "💊",
    label: "Medicine",
    sublabel: "Reminders",
    desc: "Smart adaptive reminders so you never miss a dose — with snooze and history.",
    accent: "#a78bfa",
    glow: "rgba(167,139,250,0.18)",
    path: "/reminders",
    stat: "18 active",
    statLabel: "Reminders",
    badge: "Smart Alerts",
  },
  {
    id: "history",
    icon: "📋",
    label: "Medical",
    sublabel: "History",
    desc: "Browse all past symptom checks, medicines taken, and AI-generated summaries.",
    accent: "#34d399",
    glow: "rgba(52,211,153,0.18)",
    path: "/history",
    stat: "47 records",
    statLabel: "Health Logs",
    badge: "Secure",
  },
  {
    id: "hospitals",
    icon: "🏥",
    label: "Nearby",
    sublabel: "Hospitals",
    desc: "Find clinics and hospitals near you with real-time GPS and distance info.",
    accent: "#fb923c",
    glow: "rgba(251,146,60,0.18)",
    path: "/hospitals",
    stat: "3 nearby",
    statLabel: "Open Now",
    badge: "GPS Live",
  },
  {
    id: "reports",
    icon: "📄",
    label: "PDF",
    sublabel: "Reports",
    desc: "Generate professional health reports from your history to share with your doctor.",
    accent: "#f472b6",
    glow: "rgba(244,114,182,0.18)",
    path: "/reports",
    stat: "5 reports",
    statLabel: "Generated",
    badge: "Export",
  },
  {
    id: "insights",
    icon: "📈",
    label: "Health",
    sublabel: "Insights",
    desc: "Track adherence trends, mood patterns, and AI-identified health improvements.",
    accent: "#facc15",
    glow: "rgba(250,204,21,0.18)",
    path: "/insights",
    stat: "92%",
    statLabel: "Adherence",
    badge: "Analytics",
  },
];

const recentActivity = [
  { icon: "✅", text: "Metformin 500mg — Taken", time: "8:00 AM", color: "#34d399" },
  { icon: "😴", text: "Vitamin D — Snoozed", time: "12:00 PM", color: "#facc15" },
  { icon: "🧠", text: "AI Chat — Headache analyzed", time: "2:30 PM", color: "#22d3ee" },
  { icon: "📄", text: "PDF Report generated", time: "Yesterday", color: "#f472b6" },
];

export default function Dashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [hoveredCard, setHoveredCard] = useState(null);
  const [healthData, setHealthData] = useState(null);
  const [mounted, setMounted] = useState(false);
  const [greeting, setGreeting] = useState("Good morning");

  useEffect(() => {
    setMounted(true);
    const h = new Date().getHours();
    if (h < 12) setGreeting("Good morning");
    else if (h < 17) setGreeting("Good afternoon");
    else setGreeting("Good evening");

    getHealthInsights()
  .then((data) => {
    setHealthData(data);
  })
  .catch(console.error);

  }, []);

  const handleLogout = () => {
    localStorage.removeItem("user");
    navigate("/login");
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "linear-gradient(135deg, #0a0f1e 0%, #0d1525 50%, #0a0e1a 100%)",
        color: "#f1f5f9",
        fontFamily: "'DM Sans', sans-serif",
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* Google Font */}
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700;800;900&family=Space+Mono:wght@400;700&display=swap');

        * { box-sizing: border-box; margin: 0; padding: 0; }

        .feature-card {
          transition: transform 0.3s cubic-bezier(0.34,1.56,0.64,1), box-shadow 0.3s ease, border-color 0.3s ease;
          cursor: pointer;
          background: rgba(255,255,255,0.04);
          border: 1px solid rgba(255,255,255,0.08);
          border-radius: 28px;
          padding: 28px;
          position: relative;
          overflow: hidden;
          animation: fadeSlideUp 0.5s ease both;
        }
        .feature-card:hover {
          transform: translateY(-6px) scale(1.01);
        }
        .feature-card::before {
          content: '';
          position: absolute;
          inset: 0;
          border-radius: 28px;
          opacity: 0;
          transition: opacity 0.3s ease;
          pointer-events: none;
        }
        .feature-card:hover::before {
          opacity: 1;
        }

        @keyframes fadeSlideUp {
          from { opacity: 0; transform: translateY(24px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes pulse-slow {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-10px); }
        }

        .pulse-dot { animation: pulse-slow 2s infinite; }
        .nav-link { transition: color 0.2s; }
        .nav-link:hover { color: #22d3ee; }

        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }

        .stat-chip {
          font-family: 'Space Mono', monospace;
          font-size: 11px;
          letter-spacing: 0.05em;
        }
      `}</style>

      {/* BG glows */}
      <div style={{ position: "absolute", width: 600, height: 600, background: "radial-gradient(circle, rgba(34,211,238,0.07) 0%, transparent 70%)", top: -200, right: -200, pointerEvents: "none" }} />
      <div style={{ position: "absolute", width: 500, height: 500, background: "radial-gradient(circle, rgba(167,139,250,0.07) 0%, transparent 70%)", bottom: -150, left: -150, pointerEvents: "none" }} />

      {/* NAVBAR */}
      <nav style={{
        display: "flex", alignItems: "center", justifyContent: "space-between",
        padding: "18px 40px",
        borderBottom: "1px solid rgba(255,255,255,0.08)",
        backdropFilter: "blur(12px)",
        background: "rgba(10,15,30,0.6)",
        position: "sticky", top: 0, zIndex: 50,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{
            width: 40, height: 40, borderRadius: 14,
            background: "linear-gradient(135deg, #22d3ee, #0ea5e9)",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontWeight: 900, fontSize: 18, color: "#000",
            boxShadow: "0 0 20px rgba(34,211,238,0.3)",
          }}>M</div>
          <div>
            <div style={{ fontWeight: 800, fontSize: 18, letterSpacing: "-0.02em" }}>MediZen AI</div>
            <div style={{ fontSize: 11, color: "#64748b", letterSpacing: "0.12em", textTransform: "uppercase" }}>Healthcare Assistant</div>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <div style={{
            display: "flex", alignItems: "center", gap: 10,
            background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.1)",
            borderRadius: 20, padding: "8px 16px",
          }}>
            <div style={{
              width: 32, height: 32, borderRadius: "50%",
              background: "linear-gradient(135deg, #22d3ee, #a78bfa)",
              display: "flex", alignItems: "center", justifyContent: "center",
              fontWeight: 700, fontSize: 13, color: "#000",
            }}>
              {(user?.name || "U")[0].toUpperCase()}
            </div>
            <div>
              <div style={{ fontWeight: 600, fontSize: 13 }}>{user?.name || "User"}</div>
              <div style={{ fontSize: 11, color: "#64748b" }}>{user?.email || ""}</div>
            </div>
          </div>
          <button
            onClick={handleLogout}
            style={{
              background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.2)",
              color: "#f87171", padding: "8px 18px", borderRadius: 14,
              fontWeight: 600, fontSize: 13, cursor: "pointer",
              transition: "all 0.2s",
            }}
            onMouseOver={e => { e.currentTarget.style.background = "rgba(239,68,68,0.2)"; }}
            onMouseOut={e => { e.currentTarget.style.background = "rgba(239,68,68,0.1)"; }}
          >
            Logout
          </button>
        </div>
      </nav>

      <main style={{ maxWidth: 1200, margin: "0 auto", padding: "40px 32px 60px" }}>

        {/* GREETING */}
        <div style={{ marginBottom: 40, animation: "fadeSlideUp 0.4s ease both" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
            <span className="pulse-dot" style={{ width: 8, height: 8, borderRadius: "50%", background: "#34d399", display: "inline-block" }} />
            <span style={{ fontSize: 13, color: "#34d399", fontWeight: 600, letterSpacing: "0.08em", textTransform: "uppercase" }}>
              All systems active
            </span>
          </div>
          <h1 style={{ fontSize: 38, fontWeight: 800, letterSpacing: "-0.03em", lineHeight: 1.1, marginBottom: 8 }}>
            {greeting}, <span style={{ color: "#22d3ee" }}>{(user?.name || "there").split(" ")[0]}</span> 👋
          </h1>
          <p style={{ color: "#64748b", fontSize: 16 }}>
            What would you like to do today?
          </p>
        </div>

        {/* QUICK STATS ROW */}
        <div style={{
          display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 40,
          animation: "fadeSlideUp 0.45s ease both",
        }}>
          {[
  {
    label: "Health Score",

    value: healthData
      ? `${healthData.health_score.health_score}%`
      : "--",

    color: "#22d3ee",

    bar: healthData
      ? healthData.health_score.health_score
      : 0,
  },

  {
    label: "Risk Level",

    value: healthData
      ? healthData.health_score.risk_level
      : "--",

    color: "#f59e0b",

    bar: null,
  },

  {
    label: "Stress Score",

    value: healthData
      ? `${healthData.health_score.stress_score}%`
      : "--",

    color: "#a78bfa",

    bar: healthData
      ? healthData.health_score.stress_score
      : 0,
  },

  {
    label: "Adherence",

    value: healthData
      ? `${healthData.health_score.medicine_adherence}%`
      : "--",

    color: "#34d399",

    bar: healthData
      ? healthData.health_score.medicine_adherence
      : 0,
  },
].map((s, i) => (
            <div key={i} style={{
              background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.08)",
              borderRadius: 20, padding: "20px 22px",
            }}>
              <div style={{ fontSize: 12, color: "#64748b", marginBottom: 6, textTransform: "uppercase", letterSpacing: "0.08em" }}>
                {s.label}
              </div>
              <div style={{ fontSize: 32, fontWeight: 800, color: s.color, letterSpacing: "-0.02em" }}>
                {s.value}
              </div>
              {s.bar && (
                <div style={{ marginTop: 10, height: 3, background: "rgba(255,255,255,0.07)", borderRadius: 2 }}>
                  <div style={{ width: `${s.bar}%`, height: "100%", background: s.color, borderRadius: 2, boxShadow: `0 0 8px ${s.color}` }} />
                </div>
              )}
            </div>
          ))}
        </div>

        {healthData && (

  <div
    style={{
      marginBottom: 40,
      background: "rgba(255,255,255,0.04)",
      border: "1px solid rgba(255,255,255,0.08)",
      borderRadius: 24,
      padding: 24,
    }}
  >

    <h2
      style={{
        fontSize: 22,
        fontWeight: 800,
        marginBottom: 18,
      }}
    >
      AI Health Insights
    </h2>

    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: 12,
      }}
    >

      {healthData.insights.map((insight, i) => (

        <div
          key={i}
          style={{
            background: "rgba(34,211,238,0.08)",
            border: "1px solid rgba(34,211,238,0.15)",
            borderRadius: 14,
            padding: "14px 18px",
            color: "#e2e8f0",
            fontSize: 14,
          }}
        >
          🧠 {insight}
        </div>

      ))}

    </div>

  </div>

)}

        {/* FEATURES GRID */}
        <div style={{ marginBottom: 16 }}>
          <h2 style={{ fontSize: 22, fontWeight: 800, letterSpacing: "-0.02em", marginBottom: 4 }}>
            Your Features
          </h2>
          <p style={{ color: "#64748b", fontSize: 14, marginBottom: 24 }}>
            Tap any card to get started
          </p>
        </div>

        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(3, 1fr)",
          gap: 18,
          marginBottom: 40,
        }}>
          {features.map((f, i) => (
            <div
              key={f.id}
              className="feature-card"
              style={{
                animationDelay: `${i * 0.07}s`,
                borderColor: hoveredCard === f.id ? `${f.accent}40` : "rgba(255,255,255,0.08)",
                boxShadow: hoveredCard === f.id ? `0 20px 60px ${f.glow}, 0 0 0 1px ${f.accent}20` : "0 4px 24px rgba(0,0,0,0.2)",
              }}
              onMouseEnter={() => setHoveredCard(f.id)}
              onMouseLeave={() => setHoveredCard(null)}
              onClick={() => navigate(f.path)}
            >
              {/* Glow overlay on hover */}
              <div style={{
                position: "absolute", inset: 0, borderRadius: 28,
                background: `radial-gradient(circle at 30% 30%, ${f.glow}, transparent 60%)`,
                opacity: hoveredCard === f.id ? 1 : 0,
                transition: "opacity 0.3s ease",
                pointerEvents: "none",
              }} />

              {/* Badge */}
              <div style={{
                position: "absolute", top: 20, right: 20,
                background: `${f.accent}15`, border: `1px solid ${f.accent}30`,
                color: f.accent, borderRadius: 8, padding: "3px 10px",
                fontSize: 11, fontWeight: 700, letterSpacing: "0.06em",
              }}>
                {f.badge}
              </div>

              {/* Icon */}
              <div style={{
                fontSize: 40, marginBottom: 16, lineHeight: 1,
                filter: hoveredCard === f.id ? `drop-shadow(0 0 12px ${f.accent})` : "none",
                transition: "filter 0.3s ease",
                display: "inline-block",
              }}>
                {f.icon}
              </div>

              {/* Title */}
              <div style={{ marginBottom: 8 }}>
                <div style={{
                  fontSize: 20, fontWeight: 800, letterSpacing: "-0.02em",
                  color: hoveredCard === f.id ? f.accent : "#f1f5f9",
                  transition: "color 0.3s ease",
                  lineHeight: 1.1,
                }}>
                  {f.label}
                </div>
                <div style={{ fontSize: 13, color: "#64748b", fontWeight: 500 }}>
                  {f.sublabel}
                </div>
              </div>

              {/* Desc */}
              <p style={{ color: "#94a3b8", fontSize: 13, lineHeight: 1.6, marginBottom: 18 }}>
                {f.desc}
              </p>

              {/* Footer */}
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <div className="stat-chip" style={{
                  background: `${f.accent}12`, border: `1px solid ${f.accent}25`,
                  color: f.accent, borderRadius: 8, padding: "4px 10px",
                }}>
                  {f.stat}
                </div>
                <div style={{
                  width: 32, height: 32, borderRadius: 10,
                  background: hoveredCard === f.id ? f.accent : "rgba(255,255,255,0.06)",
                  border: `1px solid ${hoveredCard === f.id ? f.accent : "rgba(255,255,255,0.1)"}`,
                  display: "flex", alignItems: "center", justifyContent: "center",
                  color: hoveredCard === f.id ? "#000" : "#94a3b8",
                  fontSize: 16, fontWeight: 700,
                  transition: "all 0.3s cubic-bezier(0.34,1.56,0.64,1)",
                  transform: hoveredCard === f.id ? "rotate(45deg) scale(1.1)" : "none",
                }}>
                  →
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* BOTTOM ROW: Recent Activity + Quick Action */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 380px", gap: 18 }}>

          {/* Recent Activity */}
          <div style={{
            background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.08)",
            borderRadius: 24, padding: 28, animation: "fadeSlideUp 0.6s ease both",
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
              <div>
                <h3 style={{ fontWeight: 800, fontSize: 17, letterSpacing: "-0.01em" }}>Recent Activity</h3>
                <p style={{ color: "#64748b", fontSize: 13, marginTop: 2 }}>Your last interactions</p>
              </div>
              <Link to="/history" style={{
                fontSize: 12, color: "#22d3ee", fontWeight: 600,
                textDecoration: "none", border: "1px solid rgba(34,211,238,0.2)",
                padding: "6px 14px", borderRadius: 10, letterSpacing: "0.04em",
              }}>
                View All →
              </Link>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {recentActivity.map((item, i) => (
                <div key={i} style={{
                  display: "flex", alignItems: "center", gap: 14,
                  padding: "12px 16px",
                  background: "rgba(255,255,255,0.03)", borderRadius: 14,
                  border: "1px solid rgba(255,255,255,0.05)",
                }}>
                  <div style={{
                    width: 36, height: 36, borderRadius: 10,
                    background: `${item.color}15`, border: `1px solid ${item.color}30`,
                    display: "flex", alignItems: "center", justifyContent: "center",
                    fontSize: 16,
                  }}>{item.icon}</div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: 14, fontWeight: 500, color: "#e2e8f0" }}>{item.text}</div>
                  </div>
                  <div className="stat-chip" style={{ color: "#64748b" }}>{item.time}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Quick AI Chat Launch */}
          <div
            style={{
              background: "linear-gradient(135deg, rgba(34,211,238,0.08) 0%, rgba(14,165,233,0.05) 100%)",
              border: "1px solid rgba(34,211,238,0.2)",
              borderRadius: 24, padding: 28,
              display: "flex", flexDirection: "column", justifyContent: "space-between",
              cursor: "pointer", animation: "fadeSlideUp 0.65s ease both",
              transition: "all 0.3s ease",
            }}
            onClick={() => navigate("/chat")}
            onMouseOver={e => { e.currentTarget.style.borderColor = "rgba(34,211,238,0.45)"; e.currentTarget.style.transform = "translateY(-3px)"; }}
            onMouseOut={e => { e.currentTarget.style.borderColor = "rgba(34,211,238,0.2)"; e.currentTarget.style.transform = "none"; }}
          >
            <div>
              <div style={{
                width: 56, height: 56, borderRadius: 18,
                background: "linear-gradient(135deg, #22d3ee, #0ea5e9)",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: 26, marginBottom: 16,
                boxShadow: "0 0 30px rgba(34,211,238,0.3)",
                animation: "float 3s ease-in-out infinite",
              }}>🧠</div>
              <h3 style={{ fontSize: 22, fontWeight: 800, letterSpacing: "-0.02em", marginBottom: 8 }}>
                AI Symptom Chat
              </h3>
              <p style={{ color: "#94a3b8", fontSize: 14, lineHeight: 1.6 }}>
                Tell the AI how you're feeling. Get instant health insights, possible conditions, and recommended actions.
              </p>
            </div>
            <div style={{
              marginTop: 24, background: "#22d3ee", color: "#000",
              fontWeight: 800, fontSize: 15, textAlign: "center",
              padding: "14px", borderRadius: 14,
              boxShadow: "0 4px 20px rgba(34,211,238,0.3)",
              letterSpacing: "-0.01em",
            }}>
              Start AI Chat →
            </div>
          </div>

        </div>
      </main>
    </div>
  );
}