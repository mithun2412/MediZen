import { motion } from "framer-motion";
import { Clock3, CalendarDays, Trash2 } from "lucide-react";

const formatDate = (value, options) => {
  if (!value) return "Not set";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "Not set" : date.toLocaleString(undefined, options);
};

export default function ReminderCard({ reminder, onDelete }) {
  // Support records created before and after the reminder model update.
  const scheduledAt = reminder.start_date || reminder.reminder_time;
  const endDate = reminder.end_date || reminder.continue_medicine_until;
  const status = reminder.status || (reminder.is_active === false ? "Inactive" : "Active");

  return <motion.div whileHover={{ y: -4 }} className="rounded-[28px] border border-white/10 bg-white/5 p-7 shadow-xl shadow-black/10">
    <div className="flex justify-between gap-4">
      <div><h2 className="break-words text-2xl font-black">{reminder.medicine_name}</h2><p className="mt-1 text-slate-400">{reminder.dosage || "Dosage not specified"}</p></div>
      <button aria-label={`Delete ${reminder.medicine_name} reminder`} onClick={() => onDelete(reminder.id)} className="h-11 w-11 shrink-0 rounded-2xl bg-red-500/10 transition hover:bg-red-500/20"><Trash2 className="mx-auto h-5 w-5 text-red-300" /></button>
    </div>
    <div className="mt-7 space-y-4 text-sm">
      <p className="flex items-center gap-3"><Clock3 className="h-5 w-5 text-cyan-300" /><span>{formatDate(scheduledAt, { hour: "numeric", minute: "2-digit" })}</span></p>
      <p className="flex items-center gap-3"><CalendarDays className="h-5 w-5 text-cyan-300" /><span>Continue till: <b className="text-cyan-300">{formatDate(endDate, { year: "numeric", month: "short", day: "numeric" })}</b></span></p>
      <p className="flex items-center gap-3"><CalendarDays className="h-5 w-5 text-cyan-300" /><span>Status: <b className={status === "Active" ? "text-emerald-300" : "text-slate-300"}>{status}</b></span></p>
    </div>
  </motion.div>;
}
