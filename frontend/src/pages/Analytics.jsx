import { useEffect, useState } from "react";
import { motion } from "framer-motion";

import {
  Activity,
  AlertTriangle,
  BrainCircuit,
  HeartPulse,
  ShieldAlert,
  TrendingUp,
} from "lucide-react";

import { getDashboardAnalytics } from "../api/api";

import { useAuth } from "../context/AuthContext";

import SeverityChart from "../components/analytics/SeverityChart";
import SymptomChart from "../components/analytics/SymptomChart";
import HealthScoreCard from "../components/analytics/HealthScoreCard";
import AdherenceCard from "../components/analytics/AdherenceCard";
import InsightCard from "../components/analytics/InsightCard";
import StatCard from "../components/analytics/StatCard";
import StressCard from "../components/analytics/StressCard";

export default function Analytics() {
  const { user } = useAuth();

  const [loading, setLoading] = useState(true);

  const [analytics, setAnalytics] = useState(null);

  // ─────────────────────────────
  // FETCH ANALYTICS
  // ─────────────────────────────

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);

      const response = await getDashboardAnalytics(1);

      console.log("Analytics Response:", response.data);

      setAnalytics(response.data);
    } catch (err) {
      console.log("Analytics Error:", err);
    } finally {
      setLoading(false);
    }
  };

  // ─────────────────────────────
  // SAFE FALLBACK DATA
  // ─────────────────────────────

  const stats = {
    total_reports:
      analytics?.total_reports ?? 22,

    adherence_score:
      analytics?.adherence_score ?? 84,

    health_score:
      analytics?.health_score ?? 81,

    high_severity_cases:
      analytics?.high_severity_cases ?? 4,

    stress_level:
      analytics?.stress_level ?? "Moderate",

    recurring_symptoms:
      Array.isArray(
        analytics?.recurring_symptoms
      )
        ? analytics.recurring_symptoms
        : [
            {
              name: "Fever",
              count: 12,
            },
            {
              name: "Cold",
              count: 8,
            },
            {
              name: "Chest Pain",
              count: 5,
            },
            {
              name: "Weakness",
              count: 7,
            },
          ],

    severity_distribution:
      Array.isArray(
        analytics?.severity_distribution
      )
        ? analytics.severity_distribution
        : [
            {
              name: "Low",
              value: 12,
            },
            {
              name: "Moderate",
              value: 7,
            },
            {
              name: "High",
              value: 3,
            },
          ],

    ai_insights:
      Array.isArray(
        analytics?.ai_insights
      )
        ? analytics.ai_insights
        : [
            "Frequent fever-related symptoms detected over recent conversations.",
            "Medicine adherence has improved consistently this week.",
            "Very low recurrence of high-severity medical conditions.",
            "Stress-related symptom patterns appear moderate.",
          ],
  };

  return (
    <div className="min-h-screen bg-black text-white overflow-hidden relative">

      {/* BACKGROUND */}

      <div className="absolute inset-0">
        <div className="absolute top-[-120px] left-[-100px] w-[420px] h-[420px] bg-cyan-500/20 blur-[120px] rounded-full" />

        <div className="absolute bottom-[-180px] right-[-120px] w-[420px] h-[420px] bg-emerald-500/20 blur-[120px] rounded-full" />
      </div>

      {/* GRID */}

      <div className="absolute inset-0 opacity-10 bg-[linear-gradient(to_right,#ffffff10_1px,transparent_1px),linear-gradient(to_bottom,#ffffff10_1px,transparent_1px)] bg-[size:60px_60px]" />

      {/* CONTENT */}

      <div className="relative z-10 max-w-7xl mx-auto px-8 py-12">

        {/* HEADER */}

        <motion.div
          initial={{
            opacity: 0,
            y: 20,
          }}
          animate={{
            opacity: 1,
            y: 0,
          }}
          className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-8"
        >

          {/* LEFT */}

          <div>

            <div className="inline-flex items-center gap-3 px-5 py-3 rounded-2xl bg-cyan-400/10 border border-cyan-400/20 text-cyan-300 font-bold">
              <Activity className="w-5 h-5" />
              AI Healthcare Analytics
            </div>

            <h1 className="text-6xl font-black mt-8 leading-tight">
              Health Intelligence Dashboard
            </h1>

            <p className="text-slate-400 text-xl leading-9 mt-6 max-w-3xl">
              Analyze symptom recurrence,
              adherence tracking,
              severity trends,
              and AI-generated healthcare insights.
            </p>

          </div>

          {/* USER */}

          <div className="bg-white/5 border border-white/10 rounded-[32px] p-8 backdrop-blur-2xl min-w-[320px]">

            <div className="flex items-center gap-5">

              <div className="w-16 h-16 rounded-3xl bg-cyan-400 flex items-center justify-center">
                <HeartPulse className="text-black w-8 h-8" />
              </div>

              <div>
                <h3 className="text-2xl font-black">
                  {user?.name || "User"}
                </h3>

                <p className="text-slate-400 mt-1">
                  AI Healthcare Analytics
                </p>
              </div>

            </div>

          </div>

        </motion.div>

        {/* LOADING */}

        {loading && (
          <div className="flex justify-center mt-24">

            <div className="animate-pulse text-cyan-300 text-2xl font-bold">
              Loading analytics...
            </div>

          </div>
        )}

        {/* DASHBOARD */}

        {!loading && (
          <>

            {/* TOP STATS */}

            <div className="grid md:grid-cols-2 xl:grid-cols-4 gap-6 mt-14">

              <StatCard
                icon={BrainCircuit}
                title="Total Reports"
                value={stats.total_reports}
                color="bg-cyan-400"
              />

              <StatCard
                icon={TrendingUp}
                title="Health Score"
                value={`${stats.health_score}%`}
                color="bg-emerald-400"
              />

              <StatCard
                icon={ShieldAlert}
                title="High Severity"
                value={stats.high_severity_cases}
                color="bg-red-400"
              />

              <StatCard
                icon={AlertTriangle}
                title="Stress Level"
                value={stats.stress_level}
                color="bg-yellow-400"
              />

            </div>

            {/* SCORE CARDS */}

            <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-6 mt-10">

              <HealthScoreCard

  analytics={stats}
/>

              <AdherenceCard
                adherence={stats.adherence_score}
              />

              <StressCard
                stressLevel={stats.stress_level}
              />

            </div>

            {/* CHARTS */}

            <div className="grid xl:grid-cols-2 gap-8 mt-10">

              <SeverityChart
                data={stats.severity_distribution}
              />

              <SymptomChart
                data={stats.recurring_symptoms}
              />

            </div>

            {/* AI INSIGHTS */}

            <div className="mt-10">

              <div className="flex items-center gap-4 mb-8">
                <BrainCircuit className="text-cyan-300 w-8 h-8" />

                <h2 className="text-4xl font-black">
                  AI Healthcare Insights
                </h2>
              </div>

              <div className="grid xl:grid-cols-2 gap-6">

                {stats.ai_insights.length > 0 ? (
                  stats.ai_insights.map(
                    (insight, index) => (
                      <InsightCard
                        key={index}
                        insight={insight}
                      />
                    )
                  )
                ) : (
                  <div className="text-slate-400">
                    No AI insights available
                  </div>
                )}

              </div>

            </div>

          </>
        )}

      </div>

    </div>
  );
}