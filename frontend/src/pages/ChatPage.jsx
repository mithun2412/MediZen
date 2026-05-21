import { useState } from "react";
import axios from "axios";

function ChatPage() {
  const [symptom, setSymptom] = useState("");
  const [response, setResponse] = useState(null);

  const sendSymptoms = async () => {
    try {
      const res = await axios.post(
        "http://127.0.0.1:8000/analyze",
        {
          symptom: symptom,
        }
      );

      setResponse(res.data);
    } catch (error) {
      console.log(error);
    }
  };

  return (
    <div className="p-10">
      <h1 className="text-3xl font-bold mb-5">
        MediVoice AI
      </h1>

      <textarea
        className="border p-3 w-full"
        rows="4"
        placeholder="Describe your symptoms..."
        value={symptom}
        onChange={(e) => setSymptom(e.target.value)}
      />

      <button
        onClick={sendSymptoms}
        className="bg-blue-500 text-white px-5 py-2 mt-3 rounded"
      >
        Analyze Symptoms
      </button>

      {response && (
        <div className="mt-5 border p-5 rounded">
          <h2 className="text-xl font-bold">
            AI Response
          </h2>

          <p>{response.analysis}</p>

          <div
            className={`mt-3 p-2 rounded text-white ${
              response.severity === "High"
                ? "bg-red-500"
                : response.severity === "Moderate"
                ? "bg-yellow-500"
                : "bg-green-500"
            }`}
          >
            Severity: {response.severity}
          </div>
        </div>
      )}
    </div>
  );
}

export default ChatPage;