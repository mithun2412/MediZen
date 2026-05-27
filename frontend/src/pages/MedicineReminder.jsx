import { useEffect, useState } from "react";

import { motion } from "framer-motion";

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

  const [medicine, setMedicine] =
    useState("");

  const [dosage, setDosage] =
    useState("");

  const [datetime, setDatetime] =
    useState("");

  const [reminders, setReminders] =
    useState([]);


  // ─────────────────────────────
  // FETCH REMINDERS
  // ─────────────────────────────

  useEffect(() => {

    fetchReminders();

  }, []);


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
          !datetime
        ) {

          alert(
            "Please fill all fields"
          );

          return;
        }

        await createReminder({

          user_id: user?.id,

          medicine_name:
            medicine,

          dosage,

          reminder_time:
            datetime,

          // DEFAULT STATUS
          status: "Pending",
        });

        // CLEAR INPUTS
        setMedicine("");

        setDosage("");

        setDatetime("");

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

        <div className="bg-white/5 border border-white/10 rounded-[32px] p-8 mb-10">

          <div className="grid md:grid-cols-4 gap-5">

            <input

              type="text"

              placeholder="Medicine Name"

              value={medicine}

              onChange={(e) =>
                setMedicine(
                  e.target.value
                )
              }

              className="bg-white/5 border border-white/10 rounded-2xl px-5 py-4"
            />

            <input

              type="text"

              placeholder="Dosage"

              value={dosage}

              onChange={(e) =>
                setDosage(
                  e.target.value
                )
              }

              className="bg-white/5 border border-white/10 rounded-2xl px-5 py-4"
            />

            <input

              type="datetime-local"

              value={datetime}

              onChange={(e) =>
                setDatetime(
                  e.target.value
                )
              }

              className="bg-white/5 border border-white/10 rounded-2xl px-5 py-4 color-scheme-dark"
            />

            <button

              onClick={
                handleAddReminder
              }

              className="bg-cyan-400 hover:bg-cyan-300 text-black font-black rounded-2xl"
            >

              Add Reminder

            </button>

          </div>

        </div>


        {/* REMINDER LIST */}

        <div className="grid xl:grid-cols-2 gap-8">

          {reminders.map(

            (reminder) => (

              <motion.div

                key={reminder.id}

                whileHover={{

                  y: -4,
                }}

                className="bg-white/5 border border-white/10 rounded-[32px] p-8"
              >

                {/* TOP */}

                <div className="flex justify-between">

                  <div>

                    <h2 className="text-3xl font-black">

                      {
                        reminder.medicine_name
                      }

                    </h2>

                    <p className="text-slate-400 mt-2">

                      {reminder.dosage}

                    </p>

                  </div>


                  {/* DELETE */}

                  <button

                    onClick={() =>
                      handleDelete(
                        reminder.id
                      )
                    }

                    className="w-12 h-12 rounded-2xl bg-red-500/10 hover:bg-red-500/20 transition"
                  >

                    <Trash2 className="text-red-300 w-5 h-5 mx-auto" />

                  </button>

                </div>


                {/* TIME */}

                <div className="flex items-center gap-3 mt-8">

                  <Clock3 className="text-cyan-300 w-5 h-5" />

                  <span>

                    {new Date(
                      reminder.reminder_time
                    ).toLocaleString()}

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
                        reminder.status ===
                        "Taken"

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


                {/* ACTION BUTTONS */}

                {
                  reminder.status ===
                    "Pending" && (

                    <div className="flex gap-4 mt-8">

                      {/* TAKEN */}

                      <button

                        onClick={() =>
                          handleStatus(

                            reminder.id,

                            "Taken"
                          )
                        }

                        className="flex-1 py-4 rounded-2xl bg-emerald-500 hover:bg-emerald-400 text-black font-black transition"
                      >

                        Taken

                      </button>


                      {/* MISSED */}

                      <button

                        onClick={() =>
                          handleStatus(

                            reminder.id,

                            "Missed"
                          )
                        }

                        className="flex-1 py-4 rounded-2xl bg-red-500 hover:bg-red-400 text-white font-black transition"
                      >

                        Missed

                      </button>

                    </div>
                  )
                }

              </motion.div>
            )
          )}

        </div>

      </div>

    </div>
  );
}