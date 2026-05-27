import {

  PieChart,

  Pie,

  Cell,

  Tooltip,

  ResponsiveContainer,

  Legend,

} from "recharts";


const COLORS = [

  "#22c55e",

  "#eab308",

  "#ef4444",
];


export default function SeverityChart({

  data = [],
}) {

  return (

    <div className="bg-white/5 border border-white/10 rounded-[32px] p-6 backdrop-blur-2xl">

      <h2 className="text-2xl font-black mb-6">

        Severity Distribution

      </h2>


      <div className="w-full h-[320px]">

        <ResponsiveContainer>

          <PieChart>

            <Pie

              data={data}

              cx="50%"

              cy="50%"

              outerRadius={110}

              dataKey="value"

              nameKey="name"

              label
            >

              {data.map(

                (entry, index) => (

                  <Cell

                    key={index}

                    fill={

                      COLORS[
                        index %
                          COLORS.length
                      ]
                    }
                  />
                )
              )}

            </Pie>

            <Tooltip />

            <Legend />

          </PieChart>

        </ResponsiveContainer>

      </div>

    </div>
  );
}