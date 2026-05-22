import { motion } from "framer-motion";

export default function HealthScoreCard({
  score,
  risk
}) {

  return (

    <motion.div

      initial={{ opacity: 0, y: 20 }}

      animate={{ opacity: 1, y: 0 }}

      className="
        bg-white
        rounded-2xl
        p-6
        shadow-lg
      "
    >

      <h2 className="text-xl font-bold mb-4">
        Health Score
      </h2>

      <div className="text-5xl font-bold text-blue-600">
        {score}%
      </div>

      <p className="mt-2 text-gray-600">
        Risk Level: {risk}
      </p>

    </motion.div>
  );
}