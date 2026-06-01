import { motion } from "framer-motion";
import {
  Clock3,
  CalendarDays,
  Trash2,
} from "lucide-react";

export default function ReminderCard({
  reminder,
  onDelete,
  onStatus,
}) {
  return (
    <motion.div
      whileHover={{ y: -4 }}
      className="bg-white/5 border border-white/10 rounded-[32px] p-8"
    >
      {/* TOP */}

      <div className="flex justify-between">

        <div>

          <h2 className="text-3xl font-black">
            {reminder.medicine_name}
          </h2>

          <p className="text-slate-400 mt-2">
            {reminder.dosage}
          </p>

        </div>

        <button
          onClick={() =>
            onDelete(reminder.id)
          }
          className="w-12 h-12 rounded-2xl bg-red-500/10 hover:bg-red-500/20 transition"
        >
          <Trash2 className="text-red-300 w-5 h-5 mx-auto" />
        </button>

      </div>

      {/* REMINDER TIME */}

      <div className="flex items-center gap-3 mt-8">

        <Clock3 className="text-cyan-300 w-5 h-5" />

        <span>
          {new Date(
            reminder.reminder_time
          ).toLocaleString()}
        </span>

      </div>

      {/* END DATE */}

      <div className="flex items-center gap-3 mt-4">

        <CalendarDays className="text-cyan-300 w-5 h-5" />

        <span>

          Continue till:

          {" "}

          <span className="text-cyan-400 font-bold">

            {reminder.end_date
              ? new Date(
                  reminder.end_date
                ).toLocaleDateString()
              : "Not Set"}

          </span>

        </span>

      </div>

      {/* STATUS */}

      <div className="flex items-center gap-3 mt-4">

        <CalendarDays className="text-cyan-300 w-5 h-5" />

        <span>

          Status:

          {" "}

          <span
            className={
              reminder.status === "Taken"
                ? "text-emerald-400 font-bold"
                : reminder.status ===
                  "Missed"
                ? "text-red-400 font-bold"
                : "text-yellow-400 font-bold"
            }
          >

            {reminder.status}

          </span>

        </span>

      </div>

      {/* ACTIONS */}

      {reminder.status ===
        "Pending" && (

        <div className="flex gap-4 mt-8">

          <button
            onClick={() =>
              onStatus(
                reminder.id,
                "Taken"
              )
            }
            className="flex-1 py-4 rounded-2xl bg-emerald-500 hover:bg-emerald-400 text-black font-black transition"
          >
            Taken
          </button>

          <button
            onClick={() =>
              onStatus(
                reminder.id,
                "Missed"
              )
            }
            className="flex-1 py-4 rounded-2xl bg-red-500 hover:bg-red-400 text-white font-black transition"
          >
            Missed
          </button>

        </div>

      )}

    </motion.div>
  );
}