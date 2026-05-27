import { motion } from "framer-motion";


export default function StatCard({

  icon: Icon,

  title,

  value,

  color = "bg-cyan-400",
}) {

  return (

    <motion.div

      whileHover={{

        y: -5,
      }}

      className="bg-white/5 border border-white/10 rounded-[32px] p-8 backdrop-blur-2xl"
    >

      <div

        className={`

          w-16

          h-16

          rounded-3xl

          flex

          items-center

          justify-center

          ${color}
        `}
      >

        <Icon className="text-black w-8 h-8" />

      </div>


      <h3 className="text-slate-400 mt-8">

        {title}

      </h3>


      <h2 className="text-5xl font-black mt-3">

        {value}

      </h2>

    </motion.div>
  );
}