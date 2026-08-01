/**
 * @typedef {{ id?: string|number, symptom?: string, severity?: string, created_at?: string, analysis?: string, pdf_url?: string }} HealthRecord
 * @typedef {{ id?: string, medicine_name?: string, dosage?: string, reminder_time?: string }} Reminder
 * @typedef {{ id?: string, reminder_id?: string, scheduled_date?: string, status?: string, taken_at?: string }} DoseLog
 */

export const severityScore = (value) => ({ high: 3, moderate: 2, low: 1 }[(value || "").toLowerCase()] || 1);
export const titleCase = (value = "") => value.charAt(0).toUpperCase() + value.slice(1).toLowerCase();

export function buildHealthMetrics(history = [], doseLogs = []) {
  const records = [...history].sort((a, b) => new Date(a.created_at || 0) - new Date(b.created_at || 0));
  const totalSeverity = records.reduce((sum, record) => sum + severityScore(record.severity), 0);
  const averageSeverity = records.length ? totalSeverity / records.length : 1;
  const healthScore = Math.max(0, Math.min(100, Math.round(100 - (averageSeverity - 1) * 28 - Math.min(records.length, 12))));
  const status = healthScore >= 85 ? "Excellent" : healthScore >= 70 ? "Good" : healthScore >= 50 ? "Moderate" : "Needs Attention";
  const counts = records.reduce((map, record) => {
    const key = record.symptom?.trim() || "Unspecified symptom";
    map[key] = (map[key] || 0) + 1;
    return map;
  }, {});
  const symptoms = Object.entries(counts).map(([name, count]) => ({ name, count })).sort((a, b) => b.count - a.count).slice(0, 6);
  const trend = records.map((record, index) => ({
    date: new Date(record.created_at || Date.now()).toLocaleDateString(undefined, { month: "short", day: "numeric" }),
    severity: severityScore(record.severity),
    label: titleCase(record.severity || "low"),
    index: index + 1,
  }));
  const taken = doseLogs.filter((log) => (log.status || "").toLowerCase() === "taken").length;
  const missed = doseLogs.filter((log) => (log.status || "").toLowerCase() === "missed").length;
  const pending = doseLogs.length - taken - missed;
  const adherence = doseLogs.length ? Math.round((taken / doseLogs.length) * 100) : 0;
  const dayMap = doseLogs.reduce((map, log) => {
    const day = (log.scheduled_time || log.scheduled_date || "").slice(0, 10);
    if (!day) return map;
    if (!map[day]) map[day] = { date: day, taken: 0, total: 0 };
    map[day].total += 1;
    if ((log.status || "").toLowerCase() === "taken") map[day].taken += 1;
    return map;
  }, {});
  const adherenceTrend = Object.values(dayMap).map((day) => ({ ...day, percentage: Math.round((day.taken / day.total) * 100) })).slice(-14);
  const recurrence = symptoms[0];
  const risk = averageSeverity >= 2.5 ? "High" : averageSeverity >= 1.7 ? "Medium" : "Low";
  const insights = [
    recurrence ? `${recurrence.name} is your most frequently recorded symptom (${recurrence.count} entries).` : "Continue logging symptoms to unlock personalised trends.",
    doseLogs.length ? `Medication adherence is ${adherence}%; ${pending} dose${pending === 1 ? " is" : "s are"} still pending.` : "Add medication reminders to track adherence and streaks.",
    risk === "High" ? "Recent records include higher-severity symptoms. Consider timely clinical advice if symptoms persist or worsen." : "Your recorded symptom severity is currently stable; keep monitoring changes.",
  ];
  return { healthScore, status, symptoms, trend, adherence, taken, missed, pending, adherenceTrend, risk, insights, records };
}

export function calculateStreak(doseLogs = []) {
  const completedDays = new Set(doseLogs.filter((log) => (log.status || "").toLowerCase() === "taken").map((log) => (log.scheduled_time || log.scheduled_date || "").slice(0, 10)));
  let streak = 0;
  const cursor = new Date();
  while (completedDays.has(cursor.toISOString().slice(0, 10))) { streak += 1; cursor.setDate(cursor.getDate() - 1); }
  return streak;
}
