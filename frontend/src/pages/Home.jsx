import Navbar from "../components/home/Navbar";
import HeroSection from "../components/home/HeroSection";
import FeaturesSection from "../components/home/FeaturesSection";
import WorkflowSection from "../components/home/WorkflowSection";
import CTASection from "../components/home/CTASection";
import Footer from "../components/home/Footer";

function Home() {

  return (

    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 text-white overflow-hidden relative">

      {/* BACKGROUND GLOWS */}
      <div className="absolute w-[500px] h-[500px] bg-cyan-500/20 blur-3xl rounded-full top-[-100px] right-[-100px] pointer-events-none animate-pulse"></div>

      <div className="absolute w-[400px] h-[400px] bg-indigo-500/20 blur-3xl rounded-full bottom-[-100px] left-[-100px] pointer-events-none animate-pulse"></div>

      <Navbar />

      <HeroSection />

      <FeaturesSection />

      <WorkflowSection />

      <CTASection />

      <Footer />

    </div>
  );
}

export default Home;