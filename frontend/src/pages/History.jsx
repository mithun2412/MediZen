import { useEffect, useState } from "react";
import api from "../api/api";
import Navbar from "../components/Home/Navbar";

function History() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchHistory = async () => {
    try {
      const remindersRes = await api.get("/reminders");

      const reminders = remindersRes.data;

      let allHistory = [];

      for (const reminder of reminders) {
        try {
          const res = await api.get(
            `/reminders/history/${reminder.id}`
          );

          const formatted = res.data.map((log) => ({
            ...log,
            medicine_name: reminder.medicine_name,
            dosage: reminder.dosage,
          }));

          allHistory = [...allHistory, ...formatted];

        } catch (err) {
          console.error(err);
        }
      }

      allHistory.sort(
        (a, b) =>
          new Date(b.logged_at) -
          new Date(a.logged_at)
      );

      setHistory(allHistory);

    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const getStatusColor = (status) => {
    switch (status) {
      case "taken":
        return "bg-emerald-100 text-emerald-700";

      case "missed":
        return "bg-red-100 text-red-700";

      case "snoozed":
        return "bg-amber-100 text-amber-700";

      default:
        return "bg-gray-100 text-gray-700";
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">

      <div className="p-6 max-w-6xl mx-auto">

        <Navbar />

        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-800">
            📋 Medicine History
          </h1>

          <p className="text-gray-500 mt-1">
            Track all your medicine logs
          </p>
        </div>

        {loading ? (
          <div className="text-center py-20">
            <p className="text-gray-500">
              Loading history...
            </p>
          </div>
        ) : history.length === 0 ? (
          <div className="bg-white rounded-3xl shadow p-10 text-center">
            <div className="text-6xl mb-4">
              💊
            </div>

            <h2 className="text-2xl font-bold text-gray-700">
              No History Found
            </h2>

            <p className="text-gray-500 mt-2">
              Your medicine logs will appear here
            </p>
          </div>
        ) : (
          <div className="space-y-4">

            {history.map((item, index) => (
              <div
                key={index}
                className="bg-white rounded-3xl shadow p-5 flex flex-col md:flex-row md:items-center md:justify-between"
              >

                <div>
                  <h2 className="text-xl font-bold text-gray-800">
                    {item.medicine_name}
                  </h2>

                  <p className="text-gray-500 text-sm mt-1">
                    💊 {item.dosage}
                  </p>

                  <p className="text-gray-400 text-sm mt-1">
                    🕒{" "}
                    {new Date(
                      item.logged_at
                    ).toLocaleString()}
                  </p>
                </div>

                <div className="mt-4 md:mt-0">

                  <span
                    className={`px-4 py-2 rounded-2xl text-sm font-bold ${getStatusColor(
                      item.status
                    )}`}
                  >
                    {item.status.toUpperCase()}
                  </span>

                </div>

              </div>
            ))}

          </div>
        )}

      </div>
    </div>
  );
}

export default History;