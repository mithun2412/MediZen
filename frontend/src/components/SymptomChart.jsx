import {

  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer

} from "recharts";

export default function SymptomChart({
  data
}) {

  const formatted = Object.entries(data).map(
    ([name, value]) => ({
      name,
      value
    })
  );

  return (

    <div className="
      bg-white
      rounded-2xl
      p-6
      shadow-lg
      h-[350px]
    ">

      <h2 className="text-xl font-bold mb-4">
        Symptom Frequency
      </h2>

      <ResponsiveContainer
        width="100%"
        height="100%"
      >

        <BarChart data={formatted}>

          <XAxis dataKey="name" />

          <YAxis />

          <Tooltip />

          <Bar dataKey="value" />

        </BarChart>

      </ResponsiveContainer>

    </div>
  );
}