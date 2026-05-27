import { motion } from "framer-motion";

import {

  HeartPulse

} from "lucide-react";


export default function HealthScoreCard({

  analytics,
}) {

  // ─────────────────────────────
  // DYNAMIC SCORE CALCULATION
  // ─────────────────────────────

  const calculateHealthScore =
    () => {

      if (!analytics) return 75;

      let score = 100;

      // HIGH SEVERITY PENALTY
      score -=
        (analytics.high_severity_cases || 0) * 8;

      // MISSED MEDICINE PENALTY
      score -=
        (100 -

          (analytics.adherence_score || 80)

        ) * 0.3;

      // STRESS PENALTY
      if (

        analytics.stress_level ===
        "High"

      ) {

        score -= 15;
      }

      if (

        analytics.stress_level ===
        "Moderate"

      ) {

        score -= 7;
      }

      // LOWER LIMIT
      if (score < 25) {

        score = 25;
      }

      return Math.round(score);
    };


  const score =
    calculateHealthScore();


  // ─────────────────────────────
  // COLOR LOGIC
  // ─────────────────────────────

  const getColor = () => {

    if (score >= 80) {

      return "bg-emerald-400";
    }

    if (score >= 60) {

      return "bg-yellow-400";
    }

    return "bg-red-400";
  };


  const getStatus = () => {

    if (score >= 80) {

      return "Excellent";
    }

    if (score >= 60) {

      return "Moderate";
    }

    return "Critical";
  };


  return (

    <motion.div

      whileHover={{

        y: -5,
      }}

      className="bg-white/5 border border-white/10 rounded-[32px] p-8 backdrop-blur-2xl"
    >

      <div className="flex items-center gap-5">

        {/* ICON */}

        <div

          className={`

            w-16

            h-16

            rounded-3xl

            flex

            items-center

            justify-center

            ${getColor()}
          `}
        >

          <HeartPulse className="text-black w-8 h-8" />

        </div>


        {/* CONTENT */}

        <div>

          <h3 className="text-slate-400">

            Health Score

          </h3>

          <h2 className="text-5xl font-black mt-2">

            {score}%

          </h2>

          <p className="text-slate-400 mt-2">

            {getStatus()} Health Condition

          </p>

        </div>

      </div>

    </motion.div>
  );
}