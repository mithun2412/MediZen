import { useState, useEffect } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line, Legend
} from "recharts";
import api from "./api";

const SEVERITY_COLORS = {
  Critical: "#ef4444",
  High:     "#f97316",
  Moderate: "#eab308",
  Low:      "#22c55e",
};

// ─── Stat Card ────────────────────────────────────────────────────────────────
function StatCard({ icon, label, value, color }) {
  return (
    <div className="bg-white rounded-2xl shadow p-5 flex items-center gap-4">
      <div className={`text-3xl w-14 h-14 flex items-center justify-center rounded-xl ${color}`}>
        {icon}
      </div>
      <div>
        <p className="text-gray-400 text-xs">{label}</p>
        <p className="text-2xl font-bold text-gray-800">{value}</p>
      </div>
    </div>
  );
}

// ─── Dashboard ────────────────────────────────────────────────────────────────
export default function Dashboard() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState("");

  useEffect(() => {
    api.get("/history")
      .then(res => setHistory(res.data))
      .catch(() => setError("Failed to load data."))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="text-center text-gray-400 py-20">
      <p className="text-4xl mb-3 animate-spin">⏳</p>
      <p>Loading dashboard...</p>
    </div>
  );

  if (error) return (
    <div className="text-center text-red-400 py-20">
      <p className="text-4xl mb-3">⚠️</p><p>{error}</p>
    </div>
  );

  if (history.length === 0) return (
    <div className="text-center text-gray-400 py-20">
      <p className="text-5xl mb-4">📊</p>
      <p className="font-semibold text-gray-500">No data yet</p>
      <p className="text-sm mt-1">Analyze some symptoms to see your dashboard.</p>
    </div>
  );

  // ── Derived data ────────────────────────────────────────────────────────────

  // 1. Severity distribution for Pie chart
  const severityCount = history.reduce((acc, item) => {
    acc[item.severity] = (acc[item.severity] || 0) + 1;
    return acc;
  }, {});
  const pieData = Object.entries(severityCount).map(([name, value]) => ({ name, value }));

  // 2. Analyses per day for Line chart
  const perDay = history.reduce((acc, item) => {
    const date = new Date(item.created_at).toLocaleDateString("en-IN", {
      day: "2-digit", month: "short"
    });
    acc[date] = (acc[date] || 0) + 1;
    return acc;
  }, {});
  const lineData = Object.entries(perDay)
    .map(([date, count]) => ({ date, count }))
    .slice(-7); // last 7 days

  // 3. Severity over time for Bar chart
  const barData = history.slice(0, 10).reverse().map((item, i) => ({
    name: `#${i + 1}`,
    severity:
      item.severity === "Critical" ? 4 :
      item.severity === "High"     ? 3 :
      item.severity === "Moderate" ? 2 : 1,
    label: item.severity,
    symptom: item.symptom.slice(0, 20) + "..."
  }));

  // 4. Stats
  const total      = history.length;
  const emergencies = history.filter(h => h.severity === "Critical").length;
  const highRisk   = history.filter(h => h.severity === "High" || h.severity === "Critical").length;
  const lastDate   = new Date(history[0]?.created_at).toLocaleDateString("en-IN", {
    day: "2-digit", month: "short"
  });

  // 5. Health Score (simple formula)
  const riskScore = history.slice(0, 5).reduce((sum, h) => {
    return sum + (
      h.severity === "Critical" ? 40 :
      h.severity === "High"     ? 25 :
      h.severity === "Moderate" ? 10 : 5
    );
  }, 0);
  const healthScore = Math.max(0, Math.min(100, 100 - riskScore));
  const healthColor =
    healthScore >= 80 ? "text-green-500" :
    healthScore >= 60 ? "text-yellow-500" :
    healthScore >= 40 ? "text-orange-500" : "text-red-500";

  return (
    <div className="space-y-6">

      {/* ── Stat Cards ── */}
      <div className="grid grid-cols-2 gap-4">
        <StatCard icon="📋" label="Total Analyses"   value={total}      color="bg-indigo-50" />
        <StatCard icon="🚨" label="Emergencies"      value={emergencies} color="bg-red-50" />
        <StatCard icon="⚠️" label="High Risk"        value={highRisk}   color="bg-orange-50" />
        <StatCard icon="📅" label="Last Analysis"    value={lastDate}   color="bg-blue-50" />
      </div>

      {/* ── Health Score ── */}
      <div className="bg-white rounded-2xl shadow p-6 text-center">
        <p className="text-gray-500 text-sm mb-2">💯 Your Health Score</p>
        <p className={`text-6xl font-bold ${healthColor}`}>{healthScore}</p>
        <p className="text-gray-400 text-xs mt-1">out of 100 — based on last 5 analyses</p>
        <div className="mt-4 bg-gray-100 rounded-full h-3">
          <div
            className={`h-3 rounded-full transition-all duration-700 ${
              healthScore >= 80 ? "bg-green-400" :
              healthScore >= 60 ? "bg-yellow-400" :
              healthScore >= 40 ? "bg-orange-400" : "bg-red-400"
            }`}
            style={{ width: `${healthScore}%` }}
          />
        </div>
        <p className="text-xs mt-2 font-semibold">
          {healthScore >= 80 ? "✅ Good — keep it up!" :
           healthScore >= 60 ? "💛 Fair — monitor your health" :
           healthScore >= 40 ? "⚠️ Concerning — see a doctor soon" :
                               "🚨 Poor — seek medical attention"}
        </p>
      </div>

      {/* ── Severity Distribution Pie ── */}
      <div className="bg-white rounded-2xl shadow p-6">
        <h3 className="font-bold text-gray-700 mb-4">🥧 Severity Distribution</h3>
        <ResponsiveContainer width="100%" height={220}>
          <PieChart>
            <Pie
              data={pieData}
              cx="50%" cy="50%"
              outerRadius={80}
              dataKey="value"
              label={({ name, value }) => `${name}: ${value}`}
            >
              {pieData.map((entry, i) => (
                <Cell key={i} fill={SEVERITY_COLORS[entry.name] || "#6366f1"} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
        {/* Legend */}
        <div className="flex flex-wrap gap-3 justify-center mt-2">
          {pieData.map((entry, i) => (
            <div key={i} className="flex items-center gap-1 text-xs text-gray-600">
              <span className="w-3 h-3 rounded-full inline-block"
                style={{ background: SEVERITY_COLORS[entry.name] || "#6366f1" }}></span>
              {entry.name}
            </div>
          ))}
        </div>
      </div>

      {/* ── Analyses Per Day Line ── */}
      <div className="bg-white rounded-2xl shadow p-6">
        <h3 className="font-bold text-gray-700 mb-4">📈 Analyses Per Day (Last 7 Days)</h3>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={lineData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="date" tick={{ fontSize: 11 }} />
            <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
            <Tooltip />
            <Line
              type="monotone" dataKey="count"
              stroke="#6366f1" strokeWidth={2}
              dot={{ fill: "#6366f1", r: 4 }}
              name="Analyses"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* ── Severity Over Time Bar ── */}
      <div className="bg-white rounded-2xl shadow p-6">
        <h3 className="font-bold text-gray-700 mb-1">📊 Severity Trend (Last 10)</h3>
        <p className="text-xs text-gray-400 mb-4">1=Low · 2=Moderate · 3=High · 4=Critical</p>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={barData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="name" tick={{ fontSize: 11 }} />
            <YAxis domain={[0, 4]} ticks={[1, 2, 3, 4]} tick={{ fontSize: 11 }} />
            <Tooltip
              formatter={(value, name, props) => [props.payload.label, "Severity"]}
            />
            <Bar dataKey="severity" radius={[6, 6, 0, 0]}>
              {barData.map((entry, i) => (
                <Cell key={i} fill={SEVERITY_COLORS[entry.label] || "#6366f1"} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* ── Recent Symptoms Table ── */}
      <div className="bg-white rounded-2xl shadow p-6">
        <h3 className="font-bold text-gray-700 mb-4">🕐 Recent Symptoms</h3>
        <div className="space-y-2">
          {history.slice(0, 5).map(item => (
            <div key={item.id} className="flex justify-between items-center py-2 border-b border-gray-50 last:border-0">
              <p className="text-sm text-gray-600 truncate flex-1 mr-3">
                {item.symptom.slice(0, 40)}{item.symptom.length > 40 ? "..." : ""}
              </p>
              <span className="text-xs font-bold px-2 py-1 rounded-full flex-shrink-0"
                style={{
                  background: SEVERITY_COLORS[item.severity] + "20",
                  color: SEVERITY_COLORS[item.severity]
                }}>
                {item.severity}
              </span>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
}