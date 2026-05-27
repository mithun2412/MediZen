import {

  BarChart,

  Bar,

  XAxis,

  YAxis,

  Tooltip,

  ResponsiveContainer,

  CartesianGrid,

} from "recharts";


export default function SymptomChart({

  data = [],
}) {

  return (

    <div className="bg-white/5 border border-white/10 rounded-[32px] p-6 backdrop-blur-2xl">

      <h2 className="text-2xl font-black mb-6">

        Symptom Frequency

      </h2>


      <div className="w-full h-[320px]">

        <ResponsiveContainer>

          <BarChart data={data}>

            <CartesianGrid strokeDasharray="3 3" />

            <XAxis dataKey="name" />

            <YAxis />

            <Tooltip />

            <Bar

              dataKey="count"

              radius={[10, 10, 0, 0]}
            />

          </BarChart>

        </ResponsiveContainer>

      </div>

    </div>
  );
}