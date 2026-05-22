import { motion } from "framer-motion";

function FeaturesSection() {

  const features = [

    {
      title: "Conversational AI",
      desc: "Natural healthcare conversations powered by advanced AI.",
      icon: "🧠",
    },

    {
      title: "Disease Prediction",
      desc: "AI-powered disease prediction using machine learning.",
      icon: "📊",
    },

    {
      title: "CNN Vision AI",
      desc: "Medical image analysis using deep learning.",
      icon: "👁️",
    },

    {
      title: "Medicine Reminders",
      desc: "Smart medicine reminders with adherence tracking.",
      icon: "💊",
    },

    {
      title: "Health Analytics",
      desc: "Track symptoms, health trends, and recovery.",
      icon: "📈",
    },

    {
      title: "Personalized Memory",
      desc: "AI remembers recurring symptoms and medical history.",
      icon: "⚡",
    },
  ];

  return (

    <section
      id="features"
      className="relative z-10 max-w-7xl mx-auto px-8 pb-24"
    >

      <div className="text-center mb-16">

        <h2 className="text-5xl font-black mb-4 tracking-tight">
          Powerful AI Features
        </h2>

        <p className="text-slate-400 text-xl">
          Advanced AI-powered healthcare ecosystem
        </p>

      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

        {features.map((feature, index) => (

          <motion.div
            key={index}
            whileHover={{ y: -8 }}
            className="bg-white/5 border border-white/10 rounded-[30px] p-6 hover:border-cyan-500/30 transition-all duration-300"
          >

            <div className="text-5xl mb-5">
              {feature.icon}
            </div>

            <h3 className="text-2xl font-black mb-3">
              {feature.title}
            </h3>

            <p className="text-slate-400 leading-relaxed">
              {feature.desc}
            </p>

          </motion.div>
        ))}
      </div>

    </section>
  );
}

export default FeaturesSection;