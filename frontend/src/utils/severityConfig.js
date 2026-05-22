export const SEVERITY_CONFIG = {
  Critical: {
    color: "#ff3b3b",
    bg: "rgba(255,59,59,0.12)",
    border: "rgba(255,59,59,0.4)",
    glow: "rgba(255,59,59,0.25)",
    icon: "🚨",
    label: "Critical — Emergency",
    advice: "Call 112 / go to the nearest emergency room IMMEDIATELY.",
    pulse: true,
  },

  High: {
    color: "#ef4444",
    bg: "rgba(239,68,68,0.10)",
    border: "rgba(239,68,68,0.3)",
    glow: "rgba(239,68,68,0.18)",
    icon: "⛔",
    label: "High Severity",
    advice: "Seek immediate medical attention today.",
  },

  Moderate: {
    color: "#f59e0b",
    bg: "rgba(245,158,11,0.10)",
    border: "rgba(245,158,11,0.3)",
    glow: "rgba(245,158,11,0.18)",
    icon: "⚠️",
    label: "Moderate Severity",
    advice: "See a doctor within 1–2 days.",
  },

  Low: {
    color: "#22d3ee",
    bg: "rgba(34,211,238,0.08)",
    border: "rgba(34,211,238,0.25)",
    glow: "rgba(34,211,238,0.12)",
    icon: "✅",
    label: "Low Severity",
    advice: "Rest and monitor symptoms.",
  },
};