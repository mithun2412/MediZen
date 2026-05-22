function WorkflowSection() {

  const steps = [
    {
      title: "Describe Symptoms",
      icon: "🩺",
    },

    {
      title: "AI Follow-Up Questions",
      icon: "🧠",
    },

    {
      title: "Disease Prediction",
      icon: "📊",
    },

    {
      title: "Health Insights",
      icon: "📈",
    },

    {
      title: "Personalized Guidance",
      icon: "💡",
    },
  ];

  return (

    <section
      id="ai"
      className="relative z-20 max-w-7xl mx-auto px-8 py-24"
    >

      <div className="text-center mb-16">

        <h2 className="text-5xl font-black mb-4 tracking-tight">
          How MediZen AI Works
        </h2>

        <p className="text-slate-400 text-xl">
          Intelligent healthcare assistance powered by AI
        </p>

      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 items-center">

        {steps.map((step, index) => (

          <div
            key={index}
            className="relative bg-white/5 border border-white/10 rounded-[30px] p-6 text-center hover:border-cyan-500/30 transition-all duration-300"
          >

            <div className="text-5xl mb-5">
              {step.icon}
            </div>

            <h3 className="text-xl font-black text-white leading-snug">
              {step.title}
            </h3>

          </div>
        ))}
      </div>

    </section>
  );
}

export default WorkflowSection;