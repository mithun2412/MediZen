import { useState, useEffect, useRef, useCallback } from "react";
import api from "../api/api";

// ─────────────────────────────────────────────────────────
// CONSTANTS
// ─────────────────────────────────────────────────────────
const FREQUENCY_OPTIONS = [
  { value: "daily",        label: "Once Daily",  defaultTimes: ["08:00"] },
  { value: "twice_daily",  label: "Twice Daily", defaultTimes: ["08:00", "20:00"] },
  { value: "thrice_daily", label: "3× Daily",    defaultTimes: ["08:00", "14:00", "20:00"] },
  { value: "weekly",       label: "Weekly",      defaultTimes: ["08:00"] },
  { value: "custom",       label: "Custom",      defaultTimes: ["08:00"] },
];

const MEDICINE_ICONS = ["💊", "💉", "🧴", "🫁", "🩻", "🧪", "💆", "🌿"];

const STATUS_CONFIG = {
  taken:   { label: "Taken",   bg: "bg-emerald-100 text-emerald-700 border-emerald-300", icon: "✅" },
  missed:  { label: "Missed",  bg: "bg-red-100 text-red-700 border-red-300",             icon: "❌" },
  snoozed: { label: "Snoozed", bg: "bg-amber-100 text-amber-700 border-amber-300",       icon: "⏰" },
};

// ─────────────────────────────────────────────────────────
// HELPERS
// ─────────────────────────────────────────────────────────
function formatTime(t) {
  const [h, m] = t.split(":");
  const hour = parseInt(h);
  return `${hour % 12 || 12}:${m} ${hour >= 12 ? "PM" : "AM"}`;
}

function getMedicineIcon(name) {
  return MEDICINE_ICONS[name.charCodeAt(0) % MEDICINE_ICONS.length];
}

function getAdherence(history) {
  if (!history.length) return null;
  return Math.round((history.filter(h => h.status === "taken").length / history.length) * 100);
}

// ─────────────────────────────────────────────────────────
// BROWSER NOTIFICATION PERMISSION
// ─────────────────────────────────────────────────────────
async function requestNotificationPermission() {
  if (!("Notification" in window)) return "unsupported";
  if (Notification.permission === "granted") return "granted";
  if (Notification.permission === "denied") return "denied";
  const result = await Notification.requestPermission();
  return result;
}

function sendBrowserNotification(medicine, dosage, notes) {
  if (Notification.permission !== "granted") return;
  const n = new Notification(`💊 Time to take ${medicine}`, {
    body: `${dosage}${notes ? `\n📝 ${notes}` : ""}`,
    icon: "https://cdn.jsdelivr.net/npm/twemoji@14/ext/72x72/1f48a.png",
    badge: "https://cdn.jsdelivr.net/npm/twemoji@14/ext/72x72/1f48a.png",
    tag: medicine,
    requireInteraction: true,
  });
  n.onclick = () => { window.focus(); n.close(); };
  return n;
}

// ─────────────────────────────────────────────────────────
// SCHEDULER  (pure frontend — checks every 30s)
// ─────────────────────────────────────────────────────────
function useReminderScheduler(reminders, onAlert) {
  const firedRef = useRef(new Set()); // "reminderId_HH:MM" fired today

  useEffect(() => {
    const check = () => {
      const now  = new Date();
      const hhmm = `${String(now.getHours()).padStart(2, "0")}:${String(now.getMinutes()).padStart(2, "0")}`;
      const today = now.toDateString();

      // Reset fired set at midnight
      if (firedRef.current._date !== today) {
        firedRef.current = new Set();
        firedRef.current._date = today;
      }

      reminders.forEach(r => {
        if (!r.is_active) return;
        if (r.today_status === "taken") return; // already taken

        r.reminder_times.forEach(t => {
          const key = `${r.id}_${t}`;
          if (t === hhmm && !firedRef.current.has(key)) {
            firedRef.current.add(key);
            sendBrowserNotification(r.medicine_name, r.dosage, r.notes);
            onAlert(r); // show in-app alert banner
          }
        });
      });
    };

    check(); // run immediately
    const interval = setInterval(check, 30_000); // every 30s
    return () => clearInterval(interval);
  }, [reminders, onAlert]);
}

// ─────────────────────────────────────────────────────────
// IN-APP ALERT BANNER
// ─────────────────────────────────────────────────────────
function AlertBanner({ reminder, onTaken, onSnooze, onDismiss }) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    setTimeout(() => setVisible(true), 50); // trigger animation
  }, []);

  return (
    <div
      className={`fixed top-4 left-1/2 z-50 w-full max-w-sm transition-all duration-500 ${
        visible ? "-translate-x-1/2 opacity-100" : "-translate-x-1/2 -translate-y-8 opacity-0"
      }`}
    >
      <div className="bg-white rounded-3xl shadow-2xl border-2 border-violet-200 overflow-hidden mx-4">
        {/* Pulsing top bar */}
        <div className="bg-gradient-to-r from-violet-500 to-indigo-500 h-1.5 animate-pulse" />

        <div className="p-5">
          <div className="flex items-start gap-3">
            <div className="text-3xl animate-bounce">💊</div>
            <div className="flex-1">
              <p className="font-bold text-gray-900 text-base">Medicine Reminder</p>
              <p className="text-violet-700 font-semibold text-sm">{reminder.medicine_name}</p>
              <p className="text-gray-500 text-xs mt-0.5">{reminder.dosage}{reminder.notes ? ` · ${reminder.notes}` : ""}</p>
            </div>
            <button onClick={onDismiss} className="text-gray-300 hover:text-gray-600 text-xl leading-none mt-0.5">×</button>
          </div>

          <div className="flex gap-2 mt-4">
            <button
              onClick={onTaken}
              className="flex-1 bg-emerald-500 hover:bg-emerald-600 text-white font-bold text-sm py-2.5 rounded-2xl transition"
            >
              ✅ Taken
            </button>
            <button
              onClick={onSnooze}
              className="flex-1 bg-amber-50 hover:bg-amber-100 text-amber-700 font-semibold text-sm py-2.5 rounded-2xl transition border border-amber-200"
            >
              ⏰ +30 min
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────
// ADD / EDIT MODAL
// ─────────────────────────────────────────────────────────
function ReminderModal({ reminder, onClose, onSaved }) {
  const isEdit = !!reminder?.id;
  const [form, setForm] = useState({
    medicine_name:  reminder?.medicine_name  || "",
    dosage:         reminder?.dosage         || "",
    frequency:      reminder?.frequency      || "daily",
    reminder_times: reminder?.reminder_times || ["08:00"],
    notes:          reminder?.notes          || "",
    end_date:       reminder?.end_date       || "",
  });
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState("");

  const setFreq = (freq) => {
    const opt = FREQUENCY_OPTIONS.find(o => o.value === freq);
    setForm(f => ({ ...f, frequency: freq, reminder_times: opt?.defaultTimes || ["08:00"] }));
  };

  const updateTime = (i, val) => {
    const times = [...form.reminder_times];
    times[i] = val;
    setForm(f => ({ ...f, reminder_times: times }));
  };

  const submit = async () => {
    if (!form.medicine_name.trim()) { setError("Medicine name required"); return; }
    if (!form.reminder_times.length){ setError("Add at least one time");  return; }
    setLoading(true); setError("");
    try {
      if (isEdit) await api.patch(`/reminders/${reminder.id}`, form);
      else        await api.post("/reminders/", form);
      onSaved();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to save");
    } finally { setLoading(false); }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-end sm:items-center justify-center z-40 p-4">
      <div className="bg-white rounded-3xl w-full max-w-md max-h-[90vh] overflow-y-auto shadow-2xl">

        {/* Header */}
        <div className="bg-gradient-to-r from-violet-600 to-indigo-600 p-6 rounded-t-3xl flex justify-between items-start">
          <div>
            <h2 className="text-white font-bold text-xl">
              {isEdit ? "✏️ Edit Reminder" : "➕ New Reminder"}
            </h2>
            <p className="text-violet-200 text-xs mt-0.5">In-app + browser notifications</p>
          </div>
          <button onClick={onClose} className="text-white/60 hover:text-white text-2xl leading-none">×</button>
        </div>

        <div className="p-6 space-y-5">

          {/* Medicine name */}
          <div>
            <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1.5 block">Medicine Name</label>
            <input
              value={form.medicine_name}
              onChange={e => setForm(f => ({ ...f, medicine_name: e.target.value }))}
              placeholder="e.g. Metformin, Paracetamol"
              className="w-full border border-gray-200 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-violet-400"
            />
          </div>

          {/* Dosage */}
          <div>
            <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1.5 block">Dosage</label>
            <input
              value={form.dosage}
              onChange={e => setForm(f => ({ ...f, dosage: e.target.value }))}
              placeholder="e.g. 500mg, 1 tablet, 10ml"
              className="w-full border border-gray-200 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-violet-400"
            />
          </div>

          {/* Frequency */}
          <div>
            <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1.5 block">Frequency</label>
            <div className="flex flex-wrap gap-2">
              {FREQUENCY_OPTIONS.map(opt => (
                <button
                  key={opt.value}
                  onClick={() => setFreq(opt.value)}
                  className={`px-3 py-1.5 rounded-xl text-xs font-semibold border transition ${
                    form.frequency === opt.value
                      ? "bg-violet-600 text-white border-violet-600"
                      : "bg-white text-gray-600 border-gray-200 hover:border-violet-300"
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>

          {/* Times */}
          <div>
            <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1.5 block">Reminder Times</label>
            <div className="space-y-2">
              {form.reminder_times.map((t, i) => (
                <div key={i} className="flex gap-2 items-center">
                  <input
                    type="time"
                    value={t}
                    onChange={e => updateTime(i, e.target.value)}
                    className="flex-1 border border-gray-200 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-violet-400"
                  />
                  {form.reminder_times.length > 1 && (
                    <button
                      onClick={() => setForm(f => ({ ...f, reminder_times: f.reminder_times.filter((_, j) => j !== i) }))}
                      className="text-red-400 hover:text-red-600 text-xl leading-none w-8"
                    >×</button>
                  )}
                </div>
              ))}
              {form.frequency === "custom" && (
                <button
                  onClick={() => setForm(f => ({ ...f, reminder_times: [...f.reminder_times, "12:00"] }))}
                  className="text-violet-600 text-sm font-semibold hover:underline"
                >+ Add Time</button>
              )}
            </div>
          </div>

          {/* Notes */}
          <div>
            <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1.5 block">Notes (optional)</label>
            <input
              value={form.notes}
              onChange={e => setForm(f => ({ ...f, notes: e.target.value }))}
              placeholder="e.g. Take after meals, with water"
              className="w-full border border-gray-200 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-violet-400"
            />
          </div>

          {/* End date */}
          <div>
            <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1.5 block">End Date (optional)</label>
            <input
              type="date"
              value={form.end_date}
              onChange={e => setForm(f => ({ ...f, end_date: e.target.value }))}
              className="w-full border border-gray-200 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-violet-400"
            />
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 rounded-xl p-3 text-sm">⚠️ {error}</div>
          )}

          <button
            onClick={submit}
            disabled={loading}
            className="w-full bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700 text-white font-bold py-3.5 rounded-2xl transition disabled:opacity-50"
          >
            {loading ? "Saving..." : isEdit ? "Update Reminder" : "Create Reminder 🔔"}
          </button>
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────
// HISTORY DRAWER
// ─────────────────────────────────────────────────────────
function HistoryDrawer({ reminder, onClose }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get(`/reminders/history/${reminder.id}`)
      .then(r => setHistory(r.data))
      .finally(() => setLoading(false));
  }, [reminder.id]);

  const adherence = getAdherence(history);

  return (
    <div className="fixed inset-0 bg-black/50 flex items-end justify-center z-40">
      <div className="bg-white rounded-t-3xl w-full max-w-md max-h-[75vh] overflow-y-auto shadow-2xl">
        <div className="p-5 border-b border-gray-100 flex justify-between items-center sticky top-0 bg-white rounded-t-3xl">
          <div>
            <h3 className="font-bold text-gray-800">{reminder.medicine_name} — History</h3>
            {adherence !== null && (
              <p className="text-xs text-gray-500 mt-0.5">
                {adherence}% adherence ·{" "}
                <span className={adherence >= 80 ? "text-emerald-500" : adherence >= 50 ? "text-amber-500" : "text-red-500"}>
                  {adherence >= 80 ? "Excellent 🌟" : adherence >= 50 ? "Fair 📈" : "Needs attention ⚠️"}
                </span>
              </p>
            )}
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-700 text-2xl">×</button>
        </div>

        {adherence !== null && (
          <div className="px-5 pt-4">
            <div className="bg-gray-100 rounded-full h-2.5">
              <div
                className={`h-2.5 rounded-full transition-all ${
                  adherence >= 80 ? "bg-emerald-500" : adherence >= 50 ? "bg-amber-500" : "bg-red-500"
                }`}
                style={{ width: `${adherence}%` }}
              />
            </div>
          </div>
        )}

        <div className="p-5 space-y-2">
          {loading && <div className="text-center py-10 text-gray-400 text-sm">Loading...</div>}
          {!loading && history.length === 0 && (
            <div className="text-center py-10">
              <p className="text-4xl mb-2">📋</p>
              <p className="text-gray-500 text-sm">No dose logs yet</p>
            </div>
          )}
          {history.map((log, i) => {
            const cfg = STATUS_CONFIG[log.status] || STATUS_CONFIG.missed;
            const dt = new Date(log.logged_at);
            return (
              <div key={i} className={`flex items-center gap-3 p-3 rounded-2xl border ${cfg.bg}`}>
                <span className="text-xl">{cfg.icon}</span>
                <div className="flex-1">
                  <p className="text-sm font-semibold">{cfg.label}</p>
                  {log.snoozed_until && (
                    <p className="text-xs opacity-75">
                      Until {new Date(log.snoozed_until).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                    </p>
                  )}
                </div>
                <div className="text-right text-xs opacity-75">
                  <p>{dt.toLocaleDateString("en-IN", { day: "numeric", month: "short" })}</p>
                  <p>{dt.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────
// REMINDER CARD
// ─────────────────────────────────────────────────────────
function ReminderCard({ reminder, onEdit, onDelete, onLogDose, onViewHistory, onToggle }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const status    = reminder.today_status;
  const statusCfg = status ? STATUS_CONFIG[status] : null;
  const icon      = getMedicineIcon(reminder.medicine_name);

  return (
    <div className={`bg-white rounded-3xl border shadow-sm transition-all ${
      reminder.is_active ? "border-gray-100 hover:shadow-md" : "opacity-50 grayscale border-gray-200"
    }`}>
      <div className="p-5">

        {/* Top row */}
        <div className="flex items-start gap-3">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-violet-100 to-indigo-100 flex items-center justify-center text-2xl flex-shrink-0">
            {icon}
          </div>

          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <h3 className="font-bold text-gray-900">{reminder.medicine_name}</h3>
              {!reminder.is_active && (
                <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-gray-100 text-gray-500">Paused</span>
              )}
              {statusCfg && (
                <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border ${statusCfg.bg}`}>
                  {statusCfg.icon} {statusCfg.label}
                </span>
              )}
            </div>

            <p className="text-sm text-gray-500 mt-0.5">{reminder.dosage}</p>

            <div className="flex flex-wrap gap-1.5 mt-2">
              {reminder.reminder_times.map((t, i) => (
                <span key={i} className="text-xs font-semibold bg-violet-50 text-violet-700 px-2.5 py-1 rounded-full">
                  🕐 {formatTime(t)}
                </span>
              ))}
            </div>

            {reminder.notes && (
              <p className="text-xs text-gray-400 mt-1.5 italic">📝 {reminder.notes}</p>
            )}
            {reminder.end_date && (
              <p className="text-xs text-gray-400 mt-0.5">
                📅 Until {new Date(reminder.end_date).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" })}
              </p>
            )}
          </div>

          {/* Menu */}
          <div className="relative">
            <button onClick={() => setMenuOpen(o => !o)} className="text-gray-400 hover:text-gray-700 p-1 text-xl">⋯</button>
            {menuOpen && (
              <div className="absolute right-0 top-8 bg-white rounded-2xl shadow-xl border border-gray-100 z-20 w-44">
                {[
                  { label: "✏️ Edit",         action: () => onEdit(reminder) },
                  { label: reminder.is_active ? "⏸️ Pause" : "▶️ Resume", action: () => onToggle(reminder) },
                  { label: "📋 History",      action: () => onViewHistory(reminder) },
                  { label: "🗑️ Delete",       action: () => onDelete(reminder.id), danger: true },
                ].map(item => (
                  <button
                    key={item.label}
                    onClick={() => { item.action(); setMenuOpen(false); }}
                    className={`w-full text-left px-4 py-3 text-sm hover:bg-gray-50 flex items-center gap-2 ${item.danger ? "text-red-500" : ""}`}
                  >
                    {item.label}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Action buttons */}
        {reminder.is_active && status !== "taken" && (
          <div className="flex gap-2 mt-4">
            <button onClick={() => onLogDose(reminder.id, "taken")}
              className="flex-1 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 font-semibold text-sm py-2.5 rounded-2xl transition">
              ✅ Taken
            </button>
            <button onClick={() => onLogDose(reminder.id, "missed")}
              className="flex-1 bg-red-50 hover:bg-red-100 text-red-600 font-semibold text-sm py-2.5 rounded-2xl transition">
              ❌ Missed
            </button>
            <button onClick={() => onLogDose(reminder.id, "snoozed", new Date(Date.now() + 30 * 60000).toISOString())}
              className="flex-1 bg-amber-50 hover:bg-amber-100 text-amber-700 font-semibold text-sm py-2.5 rounded-2xl transition">
              ⏰ +30m
            </button>
          </div>
        )}

        {status === "taken" && (
          <div className="mt-4 bg-emerald-50 rounded-2xl py-3 text-center text-emerald-700 text-sm font-semibold">
            ✅ Dose logged for today — great job!
          </div>
        )}
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────
// TODAY SUMMARY
// ─────────────────────────────────────────────────────────
function TodaySummary({ reminders }) {
  const active  = reminders.filter(r => r.is_active);
  if (!active.length) return null;

  const taken   = active.filter(r => r.today_status === "taken").length;
  const missed  = active.filter(r => r.today_status === "missed").length;
  const pending = active.filter(r => !r.today_status).length;

  return (
    <div className="bg-gradient-to-r from-violet-600 to-indigo-600 rounded-3xl p-5 mb-5 text-white">
      <p className="text-sm font-semibold opacity-80 mb-3">📅 Today's Overview</p>
      <div className="grid grid-cols-3 gap-3">
        {[
          { label: "Taken",   value: taken,   emoji: "✅" },
          { label: "Pending", value: pending, emoji: "⏳" },
          { label: "Missed",  value: missed,  emoji: "❌" },
        ].map(({ label, value, emoji }) => (
          <div key={label} className="bg-white/20 rounded-2xl p-3 text-center">
            <p className="text-2xl font-bold">{value}</p>
            <p className="text-xs opacity-80 mt-0.5">{emoji} {label}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────
// NOTIFICATION PERMISSION BANNER
// ─────────────────────────────────────────────────────────
function NotificationPermBanner({ onGrant }) {
  const [perm, setPerm] = useState(
    "Notification" in window ? Notification.permission : "unsupported"
  );

  if (perm === "granted" || perm === "unsupported") return null;

  const request = async () => {
    const result = await requestNotificationPermission();
    setPerm(result);
    if (result === "granted") onGrant?.();
  };

  return (
    <div className="bg-amber-50 border border-amber-200 rounded-2xl p-4 mb-4 flex items-center gap-3">
      <span className="text-2xl">🔔</span>
      <div className="flex-1">
        <p className="text-amber-800 font-semibold text-sm">Enable browser notifications</p>
        <p className="text-amber-600 text-xs mt-0.5">Get alerts even when you switch tabs</p>
      </div>
      <button
        onClick={request}
        className="bg-amber-500 hover:bg-amber-600 text-white text-xs font-bold px-4 py-2 rounded-xl transition"
      >
        Enable
      </button>
    </div>
  );
}

// ─────────────────────────────────────────────────────────
// MAIN PAGE
// ─────────────────────────────────────────────────────────
export default function MedicineReminder() {
  const [reminders,     setReminders]     = useState([]);
  const [loading,       setLoading]       = useState(true);
  const [showModal,     setShowModal]     = useState(false);
  const [editTarget,    setEditTarget]    = useState(null);
  const [historyTarget, setHistoryTarget] = useState(null);
  const [toast,         setToast]         = useState("");
  const [alertReminder, setAlertReminder] = useState(null); // in-app alert

  const showToast = (msg) => {
    setToast(msg);
    setTimeout(() => setToast(""), 3000);
  };

  const fetchReminders = async () => {
    try {
      const res = await api.get("/reminders/");
      setReminders(res.data);
    } catch { showToast("Failed to load reminders"); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchReminders(); }, []);

  // ── Scheduler ──
  const handleAlert = useCallback((reminder) => {
    setAlertReminder(reminder);
  }, []);

  useReminderScheduler(reminders, handleAlert);

  // ── Actions ──
  const handleLogDose = async (id, status, snoozeUntil = null) => {
    try {
      await api.post("/reminders/log", { reminder_id: id, status, snoozed_until: snoozeUntil });
      const msgs = { taken: "✅ Dose taken!", missed: "❌ Logged as missed", snoozed: "⏰ Snoozed 30 min" };
      showToast(msgs[status]);
      if (alertReminder?.id === id) setAlertReminder(null);

      // Re-schedule snooze in-app alert
      if (status === "snoozed" && snoozeUntil) {
        const delay = new Date(snoozeUntil) - Date.now();
        if (delay > 0) {
          setTimeout(() => {
            const r = reminders.find(r => r.id === id);
            if (r) {
              sendBrowserNotification(r.medicine_name, r.dosage, r.notes);
              setAlertReminder(r);
            }
          }, delay);
        }
      }
      fetchReminders();
    } catch { showToast("Failed to log dose"); }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this reminder?")) return;
    try {
      await api.delete(`/reminders/${id}`);
      showToast("🗑️ Deleted");
      fetchReminders();
    } catch { showToast("Failed to delete"); }
  };

  const handleToggle = async (reminder) => {
    try {
      await api.patch(`/reminders/${reminder.id}`, { is_active: !reminder.is_active });
      showToast(reminder.is_active ? "⏸️ Paused" : "▶️ Resumed");
      fetchReminders();
    } catch { showToast("Failed to update"); }
  };

  const handleSaved = () => {
    setShowModal(false);
    setEditTarget(null);
    showToast("🔔 Reminder saved!");
    fetchReminders();
  };

  const active = reminders.filter(r => r.is_active);
  const paused = reminders.filter(r => !r.is_active);

  return (
    <div className="relative">

      {/* Toast */}
      {toast && (
        <div className="fixed top-4 left-1/2 -translate-x-1/2 bg-gray-900 text-white text-sm font-semibold px-5 py-3 rounded-2xl shadow-lg z-50">
          {toast}
        </div>
      )}

      {/* In-app alert banner */}
      {alertReminder && (
        <AlertBanner
          reminder={alertReminder}
          onTaken={() => handleLogDose(alertReminder.id, "taken")}
          onSnooze={() => handleLogDose(alertReminder.id, "snoozed", new Date(Date.now() + 30 * 60000).toISOString())}
          onDismiss={() => setAlertReminder(null)}
        />
      )}

      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <div>
          <h2 className="text-xl font-bold text-gray-800">💊 Medicine Reminders</h2>
          <p className="text-gray-500 text-xs mt-0.5">In-app + browser notifications</p>
        </div>
        <button
          onClick={() => { setEditTarget(null); setShowModal(true); }}
          className="bg-gradient-to-r from-violet-600 to-indigo-600 text-white font-semibold px-5 py-2.5 rounded-2xl text-sm shadow hover:shadow-md transition"
        >
          + Add
        </button>
      </div>

      {/* Notification permission banner */}
      <NotificationPermBanner onGrant={() => showToast("🔔 Notifications enabled!")} />

      {/* Today summary */}
      {!loading && <TodaySummary reminders={reminders} />}

      {/* Loading */}
      {loading && (
        <div className="text-center py-16 text-gray-400">
          <p className="text-4xl mb-3">⏳</p>
          <p className="text-sm">Loading reminders...</p>
        </div>
      )}

      {/* Empty state */}
      {!loading && reminders.length === 0 && (
        <div className="text-center py-16">
          <p className="text-6xl mb-4">💊</p>
          <h3 className="text-gray-700 font-bold text-lg">No reminders yet</h3>
          <p className="text-gray-400 text-sm mt-1 mb-6">Add your medicines and never miss a dose</p>
          <button
            onClick={() => setShowModal(true)}
            className="bg-gradient-to-r from-violet-600 to-indigo-600 text-white font-semibold px-6 py-3 rounded-2xl"
          >
            + Add First Reminder
          </button>
        </div>
      )}

      {/* Active reminders */}
      {active.length > 0 && (
        <div className="space-y-4 mb-6">
          {active.map(r => (
            <ReminderCard
              key={r.id}
              reminder={r}
              onEdit={r => { setEditTarget(r); setShowModal(true); }}
              onDelete={handleDelete}
              onLogDose={handleLogDose}
              onViewHistory={setHistoryTarget}
              onToggle={handleToggle}
            />
          ))}
        </div>
      )}

      {/* Paused */}
      {paused.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
            Paused ({paused.length})
          </p>
          <div className="space-y-3">
            {paused.map(r => (
              <ReminderCard
                key={r.id}
                reminder={r}
                onEdit={r => { setEditTarget(r); setShowModal(true); }}
                onDelete={handleDelete}
                onLogDose={handleLogDose}
                onViewHistory={setHistoryTarget}
                onToggle={handleToggle}
              />
            ))}
          </div>
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <ReminderModal
          reminder={editTarget}
          onClose={() => { setShowModal(false); setEditTarget(null); }}
          onSaved={handleSaved}
        />
      )}

      {/* History drawer */}
      {historyTarget && (
        <HistoryDrawer
          reminder={historyTarget}
          onClose={() => setHistoryTarget(null)}
        />
      )}
    </div>
  );
}