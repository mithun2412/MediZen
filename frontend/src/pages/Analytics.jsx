import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Activity, BrainCircuit, HeartPulse, ShieldAlert, Pill, TrendingUp } from "lucide-react";
import { Area, AreaChart, Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { getDoseLogs, getHealthAnalyticsDashboard, getHealthHistory } from "../api/api";
import { useAuth } from "../context/AuthContext";
import { buildHealthMetrics } from "../utils/healthMetrics";

const ranges = ["7D", "30D", "90D"];
const card = "rounded-3xl border border-white/10 bg-white/[0.04] p-6 backdrop-blur-xl";

export default function Analytics() {
  const { user } = useAuth();
  const [range, setRange] = useState("30D");
  const [loading, setLoading] = useState(true);
  const [metrics, setMetrics] = useState(() => buildHealthMetrics());

  useEffect(() => {
    if (!user?.id) return;
    Promise.allSettled([getHealthHistory(user.id), getDoseLogs(user.id), getHealthAnalyticsDashboard()]).then(([history, logs, dashboard]) => {
      const records = history.status === "fulfilled" ? history.value.data?.history || history.value.data || [] : [];
      const doses = logs.status === "fulfilled" ? logs.value.data || [] : [];
      const localMetrics = buildHealthMetrics(records, doses);
      const apiMetrics = dashboard.status === "fulfilled" ? dashboard.value.data : null;
      const apiInsights = apiMetrics?.ai_insights;
      const medication = apiMetrics?.medication_statistics || {};
      const insights = Array.isArray(apiInsights)
        ? apiInsights
        : apiInsights
          ? [apiInsights.summary, ...(apiInsights.insights || []), ...(apiInsights.recommendations || [])].filter(Boolean)
          : localMetrics.insights;
      setMetrics(apiMetrics ? {
        ...localMetrics,
        healthScore: apiMetrics.health_score,
        adherence: apiMetrics.adherence,
        taken: medication.taken ?? localMetrics.taken,
        pending: medication.pending ?? localMetrics.pending,
        missed: medication.missed ?? localMetrics.missed,
        risk: apiMetrics.risk_level,
        symptoms: (apiMetrics.symptom_recurrence || apiMetrics.symptom_trends?.recurrence || localMetrics.symptoms).map((item) => ({ name: item.name || item.symptom, count: item.count })),
        trend: localMetrics.trend,
        insights,
      } : localMetrics);
      setLoading(false);
    });
  }, [user?.id]);

  const visibleTrend = metrics.trend.slice(-({ "7D": 7, "30D": 30, "90D": 90 }[range]));
  const riskColor = { Low: "text-emerald-300", Medium: "text-amber-300", High: "text-rose-300" }[metrics.risk];
  return <main className="medivoice-light-theme min-h-screen bg-[#F6F8F7] px-5 py-8 text-[#12231F] sm:px-8">
    <div className="mx-auto max-w-7xl space-y-7">
      <header className="flex flex-col justify-between gap-5 md:flex-row md:items-end">
        <div><span className="inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-4 py-2 text-sm text-cyan-200"><Activity className="h-4 w-4" /> Health analytics</span><h1 className="mt-4 text-4xl font-black sm:text-5xl">Your health, in context.</h1><p className="mt-3 max-w-2xl text-slate-400">Review patterns from your reports, symptoms, and medication history.</p></div>
        <div className="flex rounded-xl border border-white/10 bg-white/5 p-1">{ranges.map((item) => <button key={item} onClick={() => setRange(item)} className={`rounded-lg px-4 py-2 text-sm ${range === item ? "bg-cyan-400 font-bold text-slate-950" : "text-slate-400"}`}>{item}</button>)}</div>
      </header>
      {loading ? <div className="grid gap-5 md:grid-cols-4">{[1,2,3,4].map((i) => <div key={i} className="h-36 animate-pulse rounded-3xl bg-white/5" />)}</div> : <>
        <section className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
          <ScoreCard icon={HeartPulse} title="Health score" value={`${metrics.healthScore}/100`} note={metrics.status} />
          <ScoreCard icon={Pill} title="Medication adherence" value={`${metrics.adherence}%`} note={`${metrics.taken} taken · ${metrics.pending} pending`} />
          <ScoreCard icon={TrendingUp} title="Most common symptom" value={metrics.symptoms[0]?.name || "No data"} note={metrics.symptoms[0] ? `${metrics.symptoms[0].count} recorded entries` : "Start a health chat"} />
          <ScoreCard icon={ShieldAlert} title="Risk assessment" value={metrics.risk} note="Based on recorded symptom severity" risk={riskColor} />
        </section>
        <section className="grid gap-5 xl:grid-cols-2"><ChartCard title="Severity trend" subtitle="Reported symptom severity over time"><ResponsiveContainer width="100%" height={250}><AreaChart data={visibleTrend}><defs><linearGradient id="severity" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stopColor="#22d3ee" stopOpacity=".55"/><stop offset="100%" stopColor="#22d3ee" stopOpacity="0"/></linearGradient></defs><CartesianGrid stroke="#ffffff12" vertical={false}/><XAxis dataKey="date" stroke="#94a3b8"/><YAxis domain={[0,3]} stroke="#94a3b8"/><Tooltip/><Area dataKey="severity" stroke="#22d3ee" fill="url(#severity)" /></AreaChart></ResponsiveContainer></ChartCard><ChartCard title="Symptom recurrence" subtitle="Most frequently reported symptoms"><ResponsiveContainer width="100%" height={250}><BarChart data={metrics.symptoms}><CartesianGrid stroke="#ffffff12" vertical={false}/><XAxis dataKey="name" stroke="#94a3b8"/><YAxis stroke="#94a3b8"/><Tooltip/><Bar dataKey="count" fill="#34d399" radius={[8,8,0,0]} /></BarChart></ResponsiveContainer></ChartCard></section>
        <section className="grid gap-5 xl:grid-cols-3"><div className={`${card} xl:col-span-2`}><div className="mb-5 flex items-center gap-3"><BrainCircuit className="text-cyan-300"/><div><h2 className="font-bold">AI healthcare insights</h2><p className="text-sm text-slate-400">Observations based on available history</p></div></div><div className="space-y-3">{metrics.insights.map((insight) => <div key={insight} className="rounded-2xl border border-cyan-400/10 bg-cyan-400/[.04] p-4 text-sm leading-6 text-slate-300">{insight}</div>)}</div></div><div className={card}><h2 className="font-bold">Suggested next step</h2><p className={`mt-5 text-3xl font-black ${riskColor}`}>{metrics.risk} risk</p><p className="mt-3 text-sm leading-6 text-slate-400">{metrics.risk === "High" ? "Arrange timely clinical advice, especially if symptoms are new, severe, or worsening." : "Keep logging symptoms and medication doses to make future insights more precise."}</p></div></section>
      </>}
    </div>
  </main>;
}
function ScoreCard({ icon: Icon, title, value, note, risk = "text-white" }) { return <motion.div initial={{opacity:0,y:10}} animate={{opacity:1,y:0}} className={card}><Icon className="mb-5 h-6 w-6 text-cyan-300"/><p className="text-sm text-slate-400">{title}</p><p className={`mt-2 text-2xl font-black ${risk}`}>{value}</p><p className="mt-2 text-xs text-slate-500">{note}</p></motion.div>; }
function ChartCard({ title, subtitle, children }) { return <div className={card}><h2 className="font-bold">{title}</h2><p className="mb-4 text-sm text-slate-400">{subtitle}</p>{children}</div>; }
