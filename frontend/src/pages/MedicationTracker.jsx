import { useEffect, useMemo, useState } from "react";
import { CalendarDays, CheckCircle2, Clock3, Pill, TrendingUp, XCircle } from "lucide-react";
import { getMedicationHistory, getMedicationToday, updateMedicationLogStatus } from "../api/api";
import { calculateStreak } from "../utils/healthMetrics";

const card = "rounded-3xl border border-white/10 bg-white/[0.04] p-6 backdrop-blur-xl";
const dayKey = (value) => new Date(value).toISOString().slice(0, 10);
const time = (value) => new Date(value).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
const completionColors = ["bg-slate-100", "bg-cyan-100", "bg-cyan-300", "bg-cyan-500", "bg-cyan-700"];

export default function MedicationTracker() {
  const [logs, setLogs] = useState([]);
  const [todayLogs, setTodayLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [due, setDue] = useState(null);

  const load = async () => {
    try {
      const [today, history] = await Promise.all([getMedicationToday(), getMedicationHistory()]);
      const current = today.data || [];
      setTodayLogs(current);
      setLogs(history.data || []);
      setDue(current.find((log) => log.status === "Pending" && new Date(log.scheduled_time) <= new Date()) || null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    const timer = setInterval(load, 30000);
    return () => clearInterval(timer);
  }, []);

  const taken = todayLogs.filter((log) => log.status === "Taken").length;
  const pending = todayLogs.filter((log) => log.status === "Pending").length;
  const missed = todayLogs.filter((log) => log.status === "Missed").length;
  const completion = todayLogs.length ? Math.round((taken / todayLogs.length) * 100) : 0;
  const days = useMemo(() => Array.from({ length: 28 }, (_, index) => {
    const date = new Date();
    date.setDate(date.getDate() - 27 + index);
    const key = dayKey(date);
    const items = logs.filter((log) => dayKey(log.scheduled_time) === key);
    const level = items.length ? Math.ceil((items.filter((log) => log.status === "Taken").length / items.length) * 4) : 0;
    return { key, level };
  }), [logs]);

  const take = async (id) => {
    const { data } = await updateMedicationLogStatus(id, "Taken");
    setTodayLogs((items) => items.map((log) => log.id === id ? data : log));
    setLogs((items) => items.map((log) => log.id === id ? data : log));
    if (due?.id === id) setDue(null);
  };

  if (loading) return <main className="medivoice-light-theme min-h-screen bg-[#F6F8F7] p-8 text-[#12231F]"><div className="mx-auto h-64 max-w-7xl animate-pulse rounded-3xl bg-white/5" /></main>;

  return <main className="medivoice-light-theme min-h-screen bg-[#F6F8F7] px-5 py-8 text-[#12231F] sm:px-8"><div className="mx-auto max-w-7xl space-y-7">
    <header><span className="inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-4 py-2 text-sm text-cyan-700"><Pill className="h-4 w-4" /> Medication tracker</span><h1 className="mt-4 text-4xl font-black">Stay on track, every day.</h1></header>
    {due && <section className="flex flex-wrap items-center justify-between gap-4 rounded-3xl border border-cyan-300/40 bg-cyan-400/10 p-5"><div><p className="font-black text-cyan-950">Time to take {due.medicine_name}</p><p className="text-sm text-cyan-800">Scheduled for {time(due.scheduled_time)}. Please mark it after taking it.</p></div><button onClick={() => take(due.id)} className="rounded-xl bg-cyan-300 px-5 py-3 font-bold text-slate-950">Mark taken</button></section>}
    <section className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4"><Stat icon={CheckCircle2} name="Taken today" value={taken} /><Stat icon={Clock3} name="Pending" value={pending} /><Stat icon={XCircle} name="Missed" value={missed} /><Stat icon={TrendingUp} name="Current streak" value={`${calculateStreak(logs)} days`} /></section>
    <section className="grid gap-5 xl:grid-cols-3"><div className={`${card} xl:col-span-2`}><div className="flex justify-between"><div><h2 className="font-bold">Today's medicines</h2><p className="mt-1 text-sm text-slate-400">{completion}% complete</p></div><b className="text-3xl text-cyan-600">{completion}%</b></div><div className="mt-6 space-y-3">{todayLogs.length ? todayLogs.map((log) => <div key={log.id} className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-white/10 bg-black/20 p-4"><div><p className="font-semibold">{log.medicine_name}</p><p className="text-sm text-slate-400">{time(log.scheduled_time)} · {log.status}</p></div>{log.status === "Pending" && <button onClick={() => take(log.id)} className="rounded-xl bg-cyan-400 px-4 py-2 text-sm font-bold text-slate-950">Mark taken</button>}</div>) : <p className="rounded-2xl border border-dashed border-white/10 p-6 text-sm text-slate-400">No doses scheduled today.</p>}</div></div><CompletionCalendar days={days} /></section>
  </div></main>;
}

function CompletionCalendar({ days }) {
  return <div className={card}><CalendarDays className="text-cyan-500" /><h2 className="mt-4 font-bold">28-day completion</h2><p className="mt-1 text-sm text-slate-500">Each square represents one day.</p><div className="mt-5 grid grid-cols-7 gap-2">{days.map((day) => <div title={`${day.key}: ${day.level * 25}% complete`} key={day.key} className={`aspect-square rounded-md border border-slate-200 ${completionColors[day.level]}`} />)}</div><div className="mt-4 flex items-center justify-between text-xs text-slate-500"><span>Less complete</span><div className="flex gap-1">{completionColors.map((color) => <span key={color} className={`h-3 w-3 rounded-sm border border-slate-200 ${color}`} />)}</div><span>More complete</span></div></div>;
}

function Stat({ icon: Icon, name, value }) {
  return <div className={card}><Icon className="h-6 w-6 text-cyan-500" /><p className="mt-5 text-sm text-slate-400">{name}</p><p className="mt-1 text-3xl font-black">{value}</p></div>;
}
