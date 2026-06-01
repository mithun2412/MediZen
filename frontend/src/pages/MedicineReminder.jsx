import { useEffect, useState } from "react";

import { motion } from "framer-motion";
import ReminderCard from "../components/dashboard/ReminderCard";

import {

  Clock3,

  CalendarDays,

  Trash2,

  HeartPulse,

} from "lucide-react";

import {

  useAuth

} from "../context/AuthContext";

import {

  createReminder,

  getReminders,

  updateReminderStatus,

  deleteReminder,

} from "../api/api";


export default function MedicineReminder() {

  const { user } = useAuth();

 const [medicine, setMedicine] = useState("");
const [dosage, setDosage] = useState("");
const [reminderTime, setReminderTime] = useState("");
const [endDate, setEndDate] = useState("");
const [reminders, setReminders] =
  useState([]);
  // ─────────────────────────────
  // FETCH REMINDERS
  // ─────────────────────────────

 useEffect(() => {

  if (user?.id) {

    fetchReminders();

  }

}, [user]);


  const fetchReminders =
    async () => {

      try {

        // USE LOGGED IN USER ID
        const response =
          await getReminders(
            user?.id
          );

        setReminders(
          response.data
        );

      } catch (err) {

        console.log(err);
      }
    };


  // ─────────────────────────────
  // ADD REMINDER
  // ─────────────────────────────

  const handleAddReminder =
    async () => {

      try {

        if (
  !medicine ||
  !dosage ||
  !endDate ||
  !reminderTime
) {

  alert(
    "Please fill all fields"
  );

  return;
}

if (
  new Date(endDate) <
  new Date()
) {
  alert(
    "End date must be in the future"
  );
  return;
}

        await createReminder({

  user_id: user?.id,

  medicine_name: medicine,

  dosage,

  reminder_time: reminderTime,

  end_date: endDate,

  status: "Pending",
});

        // CLEAR INPUTS
       setMedicine("");
setDosage("");

setEndDate("");
setReminderTime("");

        // REFRESH
        fetchReminders();

      } catch (err) {

        console.log(err);
      }
    };


  // ─────────────────────────────
  // UPDATE STATUS
  // ─────────────────────────────

  const handleStatus =
    async (

      reminderId,

      status
    ) => {

      try {

        await updateReminderStatus(

          reminderId,

          status
        );

        // UPDATE UI
        setReminders((prev) =>

          prev.map((reminder) =>

            reminder.id === reminderId

              ? {

                  ...reminder,

                  status,
                }

              : reminder
          )
        );

      } catch (err) {

        console.log(err);
      }
    };


  // ─────────────────────────────
  // DELETE REMINDER
  // ─────────────────────────────

  const handleDelete =
    async (id) => {

      try {

        await deleteReminder(id);

        setReminders((prev) =>

          prev.filter(

            (reminder) =>
              reminder.id !== id
          )
        );

      } catch (err) {

        console.log(err);
      }
    };


  return (

    <div className="min-h-screen bg-black text-white p-8">

      <div className="max-w-7xl mx-auto">

        {/* HEADER */}

        <div className="flex items-center justify-between mb-10">

          <div>

            <h1 className="text-5xl font-black">

              Medicine Reminder

            </h1>

            <p className="text-slate-400 mt-3">

              AI-powered medicine adherence tracking.

            </p>

          </div>

          <div className="flex items-center gap-4">

            <HeartPulse className="text-cyan-400 w-8 h-8" />

            <div>

              <h3 className="font-bold">

                {user?.name}

              </h3>

              <p className="text-slate-400 text-sm">

                Healthcare User

              </p>

            </div>

          </div>

        </div>


        {/* ADD REMINDER */}

        {/* ADD REMINDER */}

<div className="bg-white/5 border border-white/10 rounded-[32px] p-8 mb-10">

  <div className="grid md:grid-cols-2 gap-6">

    {/* MEDICINE NAME */}

    <div>

      <label className="block mb-2 text-cyan-300 font-semibold">
        Medicine Name
      </label>

      <input
        type="text"
        value={medicine}
        onChange={(e) =>
          setMedicine(e.target.value)
        }
        placeholder="Paracetamol"
        className="w-full bg-white/5 border border-white/10 rounded-2xl px-5 py-4"
      />

    </div>

    {/* DOSAGE */}

    <div>

      <label className="block mb-2 text-cyan-300 font-semibold">
        Dosage
      </label>

      <input
        type="text"
        value={dosage}
        onChange={(e) =>
          setDosage(e.target.value)
        }
        placeholder="500mg"
        className="w-full bg-white/5 border border-white/10 rounded-2xl px-5 py-4"
      />

    </div>

    {/* REMINDER DATE TIME */}

    <div>

      <label className="block mb-2 text-cyan-300 font-semibold">
        Reminder Time
      </label>

     <input
  type="time"
  value={reminderTime}
  onChange={(e) =>
    setReminderTime(e.target.value)
  }
  className="
    w-full
    bg-slate-900
    border
    border-slate-700
    rounded-xl
    px-4
    py-3
    text-white
  "
/>

    </div>

    {/* END DATE */}

    <div>

      <label className="block mb-2 text-cyan-300 font-semibold">
        Continue Medicine Till
      </label>

      <input
  type="date"
  value={endDate}
  onChange={(e) =>
    setEndDate(e.target.value)
  }
  className="
    w-full
    bg-slate-900
    border
    border-slate-700
    rounded-xl
    px-4
    py-3
    text-white
  "
/>

    </div>

  </div>

  <button

    onClick={handleAddReminder}

    className="mt-6 w-full bg-cyan-400 hover:bg-cyan-300 text-black font-black py-4 rounded-2xl"

  >

    Add Reminder

  </button>

</div>


        {/* REMINDER LIST */}

        <div className="grid xl:grid-cols-2 gap-8">

          {reminders.map((reminder) => (

  <ReminderCard
    key={reminder.id}
    reminder={reminder}
    onDelete={handleDelete}
    onStatus={handleStatus}
  />

))}

        </div>

      </div>

    </div>
  );
}