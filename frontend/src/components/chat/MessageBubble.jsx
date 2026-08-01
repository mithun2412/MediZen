import { motion } from "framer-motion";
import { useState } from "react";
import {
  BrainCircuit,
  User,
  Volume2,
  Download,
  MapPin,
  ShieldAlert,
  HeartPulse,
  Save,
  FileText,
} from "lucide-react";
import ReactMarkdown from "react-markdown";

export default function MessageBubble({
  msg,
  severityConfig,
  speak,
}) {
  const [saving, setSaving] = useState(false);

  // ─────────────────────────────
  // SEVERITY STYLE
  // ─────────────────────────────

  const severityStyle =
    severityConfig?.[msg.severity] ||
    severityConfig?.Low;

  // ─────────────────────────────
  // SAVE HISTORY
  // ─────────────────────────────

  const handleSave = async () => {
    try {
      setSaving(true);
      // Import saveHealthHistory from api
      const { saveHealthHistory } = await import("../../api/api");
      await saveHealthHistory({
        user_id: 1,
        symptom: msg.content,
        severity: msg.severity || "Low",
        report: msg.content,
        pdf_url: msg.pdfUrl || "",
      });
      alert("Healthcare report saved successfully.");
    } catch (err) {
      console.log(err);
      alert("Failed to save healthcare history.");
    } finally {
      setSaving(false);
    }
  };

  // ─────────────────────────────
  // CHECK IF THIS IS A REPORT
  // ─────────────────────────────

  const isReport = msg.is_report || msg.report_ready || (msg.report && msg.report.length > 100);

  // Check if content contains markdown report formatting
  const hasMarkdownReport = msg.content && (
    msg.content.includes("##") || 
    msg.content.includes("|") ||
    msg.content.includes("---") ||
    msg.content.includes("Information Collected")
  );

  const shouldRenderMarkdown = isReport || hasMarkdownReport;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`flex ${
        msg.role === "user" ? "justify-end" : "justify-start"
      }`}
    >
      {/* BUBBLE */}
      <div
        className={`
          max-w-5xl
          rounded-[32px]
          p-6
          border
          shadow-2xl
          backdrop-blur-2xl
          relative
          overflow-hidden
          ${
            msg.role === "user"
              ? "bg-cyan-400 text-black border-cyan-300"
              : isReport
              ? "bg-white/5 border-emerald-500/30"
              : "bg-white/5 border-white/10 text-white"
          }
        `}
      >
        {/* GLOW EFFECT FOR REPORTS */}
        {isReport && (
          <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/10 via-transparent to-cyan-500/10 pointer-events-none" />
        )}

        {/* GLOW EFFECT FOR ASSISTANT */}
        {msg.role === "assistant" && !isReport && (
          <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 via-transparent to-emerald-500/5 pointer-events-none" />
        )}

        {/* HEADER */}
        <div className="flex items-start justify-between gap-4 mb-5 relative z-10">
          {/* LEFT */}
          <div className="flex items-center gap-4">
            {/* AVATAR */}
            <div
              className={`
                w-14
                h-14
                rounded-3xl
                flex
                items-center
                justify-center
                shadow-xl
                ${
                  msg.role === "user"
                    ? "bg-black/10"
                    : isReport
                    ? "bg-emerald-400"
                    : "bg-cyan-400"
                }
              `}
            >
              {msg.role === "user" ? (
                <User className="w-7 h-7" />
              ) : isReport ? (
                <FileText className="text-black w-7 h-7" />
              ) : (
                <BrainCircuit className="text-black w-7 h-7" />
              )}
            </div>

            {/* TITLE */}
            <div>
              <h3 className="font-black text-xl">
                {msg.role === "user"
                  ? "You"
                  : isReport
                  ? "📋 Health Report"
                  : "MediZen AI"}
              </h3>
              <p
                className={`text-sm mt-1 ${
                  msg.role === "user"
                    ? "text-black/70"
                    : isReport
                    ? "text-emerald-400"
                    : "text-slate-400"
                }`}
              >
                {msg.role === "user"
                  ? "Healthcare Query"
                  : isReport
                  ? "AI-generated health assessment"
                  : "AI-generated healthcare analysis"}
              </p>
            </div>
          </div>

          {/* ACTIONS */}
          {msg.role === "assistant" && !isReport && (
            <div className="flex items-center gap-3">
              {/* SPEAK */}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => speak(msg.content)}
                className="w-12 h-12 rounded-2xl bg-white/5 hover:bg-white/10 border border-white/10 flex items-center justify-center transition"
              >
                <Volume2 className="w-5 h-5 text-cyan-300" />
              </motion.button>

              {/* SAVE */}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleSave}
                disabled={saving}
                className="w-12 h-12 rounded-2xl bg-white/5 hover:bg-white/10 border border-white/10 flex items-center justify-center transition disabled:opacity-50"
              >
                <Save className="w-5 h-5 text-emerald-300" />
              </motion.button>
            </div>
          )}
        </div>

        {/* SEVERITY (only for non-report assistant messages) */}
        {msg.severity && !isReport && (
          <div
            className={`
              inline-flex
              items-center
              gap-3
              px-5
              py-3
              rounded-2xl
              text-sm
              font-bold
              mb-6
              border
              border-white/10
              ${severityStyle.bg}
              ${severityStyle.text}
            `}
          >
            <ShieldAlert className="w-5 h-5" />
            <span>{msg.severity} Severity</span>
          </div>
        )}

        {/* IMAGE */}
        {msg.image && (
          <div className="mb-6">
            <img
              src={msg.image}
              alt="medical-upload"
              className="rounded-3xl border border-white/10 max-h-[400px] object-cover shadow-2xl"
            />
          </div>
        )}

        {/* OCR */}
        {msg.extracted_text && (
          <div className="mb-6 bg-black/20 border border-white/10 rounded-3xl p-5">
            <div className="flex items-center gap-3 mb-4">
              <FileText className="text-cyan-300 w-5 h-5" />
              <h3 className="font-bold text-lg">OCR Extracted Text</h3>
            </div>
            <div className="text-slate-300 whitespace-pre-wrap leading-8 text-[15px]">
              {msg.extracted_text}
            </div>
          </div>
        )}

        {/* CONTENT - with Markdown support for reports */}
        {shouldRenderMarkdown ? (
          <div className="prose prose-invert prose-sm max-w-none relative z-10">
            <ReactMarkdown
              components={{
                h1: ({ children }) => (
                  <h1 className="text-2xl font-bold text-cyan-300 mt-6 mb-4 border-b border-white/10 pb-2">{children}</h1>
                ),
                h2: ({ children }) => (
                  <h2 className="text-xl font-bold text-emerald-300 mt-5 mb-3">{children}</h2>
                ),
                h3: ({ children }) => (
                  <h3 className="text-lg font-bold text-cyan-200 mt-4 mb-2">{children}</h3>
                ),
                table: ({ children }) => (
                  <div className="overflow-x-auto my-4">
                    <table className="min-w-full border border-white/20 rounded-lg">{children}</table>
                  </div>
                ),
                th: ({ children }) => (
                  <th className="border border-white/20 px-4 py-2 bg-white/10 text-left font-bold text-cyan-300">
                    {children}
                  </th>
                ),
                td: ({ children }) => (
                  <td className="border border-white/20 px-4 py-2 text-slate-200">{children}</td>
                ),
                ul: ({ children }) => (
                  <ul className="list-disc pl-5 space-y-1">{children}</ul>
                ),
                ol: ({ children }) => (
                  <ol className="list-decimal pl-5 space-y-1">{children}</ol>
                ),
                li: ({ children }) => (
                  <li className="text-slate-200">{children}</li>
                ),
                p: ({ children }) => (
                  <p className="text-slate-200 leading-7 my-2">{children}</p>
                ),
                strong: ({ children }) => (
                  <strong className="text-cyan-300 font-bold">{children}</strong>
                ),
                blockquote: ({ children }) => (
                  <blockquote className="border-l-4 border-cyan-500 pl-4 my-2 text-slate-300">
                    {children}
                  </blockquote>
                ),
                hr: () => (
                  <hr className="border-white/10 my-6" />
                ),
              }}
            >
              {msg.content}
            </ReactMarkdown>
          </div>
        ) : (
          <div
            className={`
              leading-8
              text-[15px]
              relative
              z-10
              ${
                msg.role === "user"
                  ? "text-black"
                  : "text-slate-100"
              }
            `}
            dangerouslySetInnerHTML={{
              __html: msg.content,
            }}
          />
        )}

        {/* HOSPITALS (only for reports) */}
        {isReport && msg.hospitals?.length > 0 && (
          <div className="mt-8 relative z-10">
            <div className="flex items-center gap-3 mb-5">
              <HeartPulse className="text-red-300 w-6 h-6" />
              <h3 className="font-black text-xl text-white">Nearby Hospitals</h3>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              {msg.hospitals.map((hospital, index) => (
                <motion.div
                  key={index}
                  whileHover={{ scale: 1.02 }}
                  className="bg-white/5 border border-white/10 rounded-3xl p-5 backdrop-blur-xl"
                >
                  <h4 className="font-black text-lg text-cyan-300">
                    {hospital.name || "Medical Facility"}
                  </h4>
                  <div className="flex items-start gap-3 mt-4 text-slate-300">
                    <MapPin className="w-5 h-5 mt-1 shrink-0" />
                    <span>{hospital.address || "Address not available"}</span>
                  </div>

                  <a
                    href={hospital.map_link || hospital.google_maps_link || `https://www.google.com/maps/search/${encodeURIComponent(hospital.name || 'hospital')}`}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-3 mt-6 bg-cyan-400 hover:bg-cyan-300 text-black font-black px-5 py-3 rounded-2xl transition"
                  >
                    <MapPin className="w-5 h-5" />
                    Open Maps
                  </a>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* GOOGLE MAPS LINK (for reports) */}
        {isReport && msg.google_maps_link && (
          <div className="mt-6 relative z-10">
            <a
              href={msg.google_maps_link}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-3 px-6 py-3 bg-blue-500/20 hover:bg-blue-500/30 text-blue-300 font-medium rounded-xl transition border border-blue-500/30"
            >
              <MapPin className="w-5 h-5" />
              Find Nearby Hospitals on Google Maps
            </a>
          </div>
        )}

        {/* PDF DOWNLOAD (for reports) */}
        {isReport && msg.pdfUrl && (
          <motion.a
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            href={`http://127.0.0.1:8000${msg.pdfUrl}`}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-4 mt-6 bg-emerald-400 hover:bg-emerald-300 text-black font-black px-6 py-4 rounded-3xl transition shadow-[0_0_30px_rgba(0,255,255,0.25)] relative z-10"
          >
            <Download className="w-6 h-6" />
            Download PDF Report
          </motion.a>
        )}

        {/* PDF DOWNLOAD (for non-report messages with PDF) */}
        {!isReport && msg.pdfUrl && (
          <motion.a
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            href={`http://127.0.0.1:8000${msg.pdfUrl}`}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-4 mt-8 bg-cyan-400 hover:bg-cyan-300 text-black font-black px-6 py-4 rounded-3xl transition shadow-[0_0_30px_rgba(0,255,255,0.25)]"
          >
            <Download className="w-6 h-6" />
            Download AI Healthcare Report
          </motion.a>
        )}
      </div>
    </motion.div>
  );
}