import { motion } from "framer-motion";
import { useCallback, useEffect, useState } from "react";
import {
  ArrowRight,
  BarChart3,
  Bell,
  BrainCircuit,
  FileSearch,
  HeartPulse,
  History,
  LogOut,
  Pill,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { getHealthAnalyticsDashboard, getMedicationToday } from "../api/api";

const tools = [
  { title: "AI Health Chat", detail: "Describe symptoms and answer a few guided follow-up questions.", icon: BrainCircuit, route: "/chat" },
  { title: "Medical Report Analysis", detail: "Upload a PDF or image and ask questions about it directly.", icon: FileSearch, route: "/report-analysis" },
  { title: "Medication Tracker", detail: "Check today's doses, your adherence, and your current streak.", icon: Pill, route: "/medication-tracker" },
  { title: "Medication Reminders", detail: "Set up and manage your medicine schedule.", icon: Bell, route: "/reminders" },
  { title: "Health Analytics", detail: "Track your health score and how it's trending over time.", icon: BarChart3, route: "/analytics" },
  { title: "Report History", detail: "Revisit past assessments and reports you've saved.", icon: History, route: "/history" },
];

const RISK_STYLES = {
  low: { label: "Low risk", text: "text-[#0F5E56]", bg: "bg-[#E9F1EF]" },
  moderate: { label: "Moderate risk", text: "text-[#92600B]", bg: "bg-[#FBF0DA]" },
  high: { label: "High risk", text: "text-[#9B2C2C]", bg: "bg-[#FBEAEA]" },
};

// Fonts are loaded at runtime so this file is a drop-in replacement.
// For a production build, move this <link> into index.html instead.
function useMediVoiceFonts() {
  useEffect(() => {
    const id = "medivoice-fonts";
    if (document.getElementById(id)) return;
    const link = document.createElement("link");
    link.id = id;
    link.rel = "stylesheet";
    link.href =
      "https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,450;9..144,560&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap";
    document.head.appendChild(link);
  }, []);
}

export default function Dashboard() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const firstName = user?.name?.trim()?.split(" ")[0] || "there";
  const [today, setToday] = useState({ loading: true, score: null, streak: 0, nextDose: null, risk: null, updatedAt: null });
  useMediVoiceFonts();

  const refreshToday = useCallback(async () => {
    if (!user?.id) return;

    try {
      const [dashboardResponse, medicationResponse] = await Promise.all([
        getHealthAnalyticsDashboard(),
        getMedicationToday(),
      ]);
      const dashboard = dashboardResponse.data;
      const now = new Date();
      const nextDose = (medicationResponse.data || [])
        .filter((dose) => dose.status === "Pending" && new Date(dose.scheduled_time) >= now)
        .sort((a, b) => new Date(a.scheduled_time) - new Date(b.scheduled_time))[0] || null;

      setToday({
        loading: false,
        score: dashboard.health_score,
        streak: dashboard.medication_statistics?.current_streak || 0,
        nextDose,
        risk: dashboard.risk_level,
        updatedAt: new Date(),
      });
    } catch (error) {
      console.error("Unable to refresh dashboard data:", error);
      setToday((current) => ({ ...current, loading: false }));
    }
  }, [user?.id]);

  useEffect(() => {
    refreshToday();
    const interval = window.setInterval(refreshToday, 30000);
    const refreshOnFocus = () => {
      if (document.visibilityState === "visible") refreshToday();
    };
    document.addEventListener("visibilitychange", refreshOnFocus);
    return () => {
      window.clearInterval(interval);
      document.removeEventListener("visibilitychange", refreshOnFocus);
    };
  }, [refreshToday]);

  const risk = today.risk ? RISK_STYLES[today.risk.toLowerCase()] || RISK_STYLES.low : null;

  return (
    <main className="min-h-screen bg-white text-[#12231F] [font-family:'IBM_Plex_Sans',sans-serif]">
      {/* Header */}
      <header className="sticky top-0 z-10 border-b border-[#E5E9E7] bg-white/95 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5 sm:px-8">
          <button onClick={() => navigate("/dashboard")} className="flex items-center gap-3 text-left">
            <span className="grid h-10 w-10 place-items-center rounded-xl bg-[#0F5E56]">
              <HeartPulse className="h-5 w-5 text-white" />
            </span>
            <span>
              <span className="block text-[1.05rem] font-medium tracking-tight [font-family:'Fraunces',serif]">
                MediVoice
              </span>
              <span className="block text-[0.65rem] uppercase tracking-[0.14em] text-[#5B6E68] [font-family:'IBM_Plex_Mono',monospace]">
                Health workspace
              </span>
            </span>
          </button>
          <div className="flex items-center gap-4">
            <span className="hidden text-sm text-[#5B6E68] sm:block">{user?.email}</span>
            <button
              onClick={() => {
                logout();
                navigate("/login", { replace: true });
              }}
              className="inline-flex items-center gap-2 rounded-lg border border-[#E5E9E7] px-3.5 py-2 text-sm font-medium text-[#3C4C47] transition hover:border-[#C7D0CC] hover:bg-[#F6F8F7]"
            >
              <LogOut className="h-4 w-4" /> Sign out
            </button>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="mx-auto max-w-7xl px-6 pt-12 sm:px-8">
        <div className="flex flex-col gap-6 border-b border-[#E5E9E7] pb-10 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-xs font-medium uppercase tracking-[0.12em] text-[#5B6E68] [font-family:'IBM_Plex_Mono',monospace]">
              Overview
            </p>
            <h1 className="mt-3 text-3xl font-medium leading-tight tracking-tight sm:text-4xl [font-family:'Fraunces',serif]">
              Good to see you, {firstName}.
            </h1>
            <p className="mt-3 max-w-lg text-[0.95rem] leading-7 text-[#5B6E68]">
              Symptoms, medications, reports, and trends — kept in one place, and easy to pick back up
              wherever you left off.
            </p>
          </div>
          <button
            onClick={() => navigate("/chat")}
            className="inline-flex shrink-0 items-center gap-2 rounded-lg bg-[#0F5E56] px-5 py-3 text-sm font-semibold text-white transition hover:bg-[#0C4B45]"
          >
            <BrainCircuit className="h-4 w-4" /> Start health chat <ArrowRight className="h-4 w-4" />
          </button>
        </div>

        {/* Stat strip */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="mt-8 grid grid-cols-2 overflow-hidden rounded-2xl border border-[#E5E9E7] sm:grid-cols-4"
        >
          <StatTile label="Health score" loading={today.loading} className="border-l-0">
            <span className="text-3xl [font-family:'IBM_Plex_Mono',monospace]">{today.score ?? "—"}</span>
            <span className="ml-1 text-xs text-[#8A9691]">/ 100</span>
          </StatTile>

          <StatTile label="Risk level" loading={today.loading}>
            {risk ? (
              <span className={`inline-flex items-center rounded-md px-2.5 py-1 text-sm font-medium ${risk.bg} ${risk.text}`}>
                {risk.label}
              </span>
            ) : (
              <span className="text-sm text-[#8A9691]">Not assessed yet</span>
            )}
          </StatTile>

          <StatTile label="Medication streak" loading={today.loading}>
            <span className="text-3xl [font-family:'IBM_Plex_Mono',monospace]">{today.streak}</span>
            <span className="ml-1 text-xs text-[#8A9691]">day{today.streak === 1 ? "" : "s"}</span>
          </StatTile>

          <StatTile label="Next dose" loading={today.loading}>
            {today.nextDose ? (
              <>
                <span className="block truncate text-sm font-medium" title={today.nextDose.medicine_name}>
                  {today.nextDose.medicine_name}
                </span>
                <span className="text-xs text-[#8A9691]">{formatDoseTime(today.nextDose.scheduled_time)}</span>
              </>
            ) : (
              <span className="text-sm text-[#8A9691]">Nothing scheduled</span>
            )}
          </StatTile>
        </motion.div>

        {today.updatedAt && (
          <p className="mt-3 text-right text-xs text-[#8A9691]">
            Updated {today.updatedAt.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })}
          </p>
        )}
      </section>

      {/* Tools */}
      <section className="mx-auto mt-14 max-w-7xl px-6 pb-20 sm:px-8">
        <div className="flex items-end justify-between gap-4 border-b border-[#E5E9E7] pb-5">
          <div>
            <p className="text-xs font-medium uppercase tracking-[0.12em] text-[#0F5E56] [font-family:'IBM_Plex_Mono',monospace]">
              Workspace
            </p>
            <h2 className="mt-1 text-2xl font-medium tracking-tight [font-family:'Fraunces',serif]">
              Choose where to continue
            </h2>
          </div>
          <p className="hidden max-w-sm text-right text-sm text-[#5B6E68] sm:block">
            Each tool stays focused, so it's easy to come back and pick up where you left off.
          </p>
        </div>

        <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {tools.map(({ title, detail, icon: Icon, route }, index) => (
            <motion.button
              key={title}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.04 }}
              onClick={() => navigate(route)}
              className="group rounded-2xl border border-[#E5E9E7] bg-white p-5 text-left transition hover:-translate-y-0.5 hover:border-[#0F5E56] hover:shadow-md"
            >
              <div className="flex items-start justify-between">
                <span className="grid h-10 w-10 place-items-center rounded-xl bg-[#E9F1EF] text-[#0F5E56] transition group-hover:bg-[#0F5E56] group-hover:text-white">
                  <Icon className="h-4.5 w-4.5" />
                </span>
                <ArrowRight className="mt-2 h-4 w-4 text-[#C7D0CC] transition group-hover:translate-x-1 group-hover:text-[#0F5E56]" />
              </div>
              <h3 className="mt-6 text-[0.95rem] font-semibold">{title}</h3>
              <p className="mt-1.5 text-sm leading-6 text-[#5B6E68]">{detail}</p>
            </motion.button>
          ))}
        </div>
      </section>
    </main>
  );
}

function StatTile({ label, loading, children, className = "" }) {
  return (
    <div className={`border-l border-t border-[#E5E9E7] p-5 first:border-l-0 sm:border-t-0 sm:first:border-l-0 ${className}`}>
      <p className="text-xs font-medium uppercase tracking-[0.08em] text-[#8A9691]">{label}</p>
      <div className="mt-2 min-h-[2rem]">
        {loading ? <div className="h-6 w-16 animate-pulse rounded bg-[#EEF1F0]" /> : children}
      </div>
    </div>
  );
}

function formatDoseTime(dateTime) {
  return new Date(dateTime).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
}