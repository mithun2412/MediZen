import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";

export function generatePDFReport(user, history) {
  const doc = new jsPDF();
  const date = new Date().toLocaleDateString("en-IN", {
    day: "2-digit", month: "long", year: "numeric"
  });

  // ── Colors ──
  const indigo  = [99, 102, 241];
  const red     = [239, 68, 68];
  const orange  = [249, 115, 22];
  const yellow  = [234, 179, 8];
  const green   = [34, 197, 94];
  const gray    = [107, 114, 128];
  const lightBg = [248, 250, 252];

  // ── Header ──
  doc.setFillColor(...indigo);
  doc.rect(0, 0, 210, 40, "F");

  doc.setTextColor(255, 255, 255);
  doc.setFontSize(22);
  doc.setFont("helvetica", "bold");
  doc.text("🏥 MediVoice AI", 15, 18);

  doc.setFontSize(11);
  doc.setFont("helvetica", "normal");
  doc.text("AI-Powered Health Report", 15, 27);
  doc.text(`Generated: ${date}`, 15, 35);

  // Patient info on right
  doc.setFontSize(10);
  doc.text(`Patient: ${user}`, 140, 20);
  doc.text(`Total Records: ${history.length}`, 140, 28);
  doc.text(`Report Date: ${date}`, 140, 36);

  // ── Health Score ──
  doc.setTextColor(0, 0, 0);
  doc.setFillColor(...lightBg);
  doc.roundedRect(15, 48, 180, 30, 4, 4, "F");

  const riskScore = history.slice(0, 5).reduce((sum, h) => {
    return sum + (
      h.severity === "Critical" ? 40 :
      h.severity === "High"     ? 25 :
      h.severity === "Moderate" ? 10 : 5
    );
  }, 0);
  const healthScore = Math.max(0, Math.min(100, 100 - riskScore));
  const scoreColor  =
    healthScore >= 80 ? green :
    healthScore >= 60 ? yellow :
    healthScore >= 40 ? orange : red;

  doc.setFontSize(12);
  doc.setFont("helvetica", "bold");
  doc.setTextColor(...indigo);
  doc.text("Health Score", 20, 60);

  doc.setFontSize(24);
  doc.setTextColor(...scoreColor);
  doc.text(`${healthScore}/100`, 20, 73);

  const scoreLabel =
    healthScore >= 80 ? "Good — Keep it up!" :
    healthScore >= 60 ? "Fair — Monitor your health" :
    healthScore >= 40 ? "Concerning — See a doctor soon" :
                        "Poor — Seek medical attention";

  doc.setFontSize(10);
  doc.setFont("helvetica", "normal");
  doc.setTextColor(...gray);
  doc.text(scoreLabel, 80, 66);

  // Score bar background
  doc.setFillColor(220, 220, 220);
  doc.roundedRect(80, 68, 100, 6, 3, 3, "F");
  // Score bar fill
  doc.setFillColor(...scoreColor);
  doc.roundedRect(80, 68, healthScore, 6, 3, 3, "F");

  // ── Summary Stats ──
  doc.setTextColor(0, 0, 0);
  doc.setFontSize(13);
  doc.setFont("helvetica", "bold");
  doc.text("Summary", 15, 92);

  const total      = history.length;
  const critical   = history.filter(h => h.severity === "Critical").length;
  const high       = history.filter(h => h.severity === "High").length;
  const moderate   = history.filter(h => h.severity === "Moderate").length;
  const low        = history.filter(h => h.severity === "Low").length;

  const stats = [
    ["Total Analyses", total, "Critical", critical],
    ["High Severity",  high,  "Moderate", moderate],
    ["Low Severity",   low,   "Emergencies", critical],
  ];

  let sx = 15;
  stats.forEach(([l1, v1, l2, v2]) => {
    doc.setFillColor(...lightBg);
    doc.roundedRect(sx, 96, 56, 22, 3, 3, "F");
    doc.setFontSize(16);
    doc.setFont("helvetica", "bold");
    doc.setTextColor(...indigo);
    doc.text(String(v1), sx + 5, 108);
    doc.setFontSize(8);
    doc.setFont("helvetica", "normal");
    doc.setTextColor(...gray);
    doc.text(l1, sx + 5, 114);

    doc.setFillColor(...lightBg);
    doc.roundedRect(sx + 60, 96, 56, 22, 3, 3, "F");
    doc.setFontSize(16);
    doc.setFont("helvetica", "bold");
    doc.setTextColor(...red);
    doc.text(String(v2), sx + 65, 108);
    doc.setFontSize(8);
    doc.setFont("helvetica", "normal");
    doc.setTextColor(...gray);
    doc.text(l2, sx + 65, 114);

    sx += 0; // single row
    return;
  });

  // Just do a clean 4-box row
  const boxes = [
    { label: "Total",    value: total,    color: indigo },
    { label: "Critical", value: critical, color: red },
    { label: "High",     value: high,     color: orange },
    { label: "Low",      value: low,      color: green },
  ];
  let bx = 15;
  boxes.forEach(({ label, value, color }) => {
    doc.setFillColor(...lightBg);
    doc.roundedRect(bx, 96, 42, 22, 3, 3, "F");
    doc.setFontSize(18);
    doc.setFont("helvetica", "bold");
    doc.setTextColor(...color);
    doc.text(String(value), bx + 8, 109);
    doc.setFontSize(8);
    doc.setFont("helvetica", "normal");
    doc.setTextColor(...gray);
    doc.text(label, bx + 8, 115);
    bx += 46;
  });

  // ── History Table ──
  doc.setTextColor(0, 0, 0);
  doc.setFontSize(13);
  doc.setFont("helvetica", "bold");
  doc.text("Symptom History", 15, 132);

  const tableRows = history.map((item, i) => [
    i + 1,
    item.symptom.length > 35 ? item.symptom.slice(0, 35) + "..." : item.symptom,
    item.severity,
    item.analysis.length > 60 ? item.analysis.slice(0, 60) + "..." : item.analysis,
    new Date(item.created_at).toLocaleDateString("en-IN"),
  ]);

  autoTable(doc, {
    startY: 136,
    head: [["#", "Symptom", "Severity", "Analysis Summary", "Date"]],
    body: tableRows,
    styles: {
      fontSize: 8,
      cellPadding: 3,
      overflow: "linebreak",
    },
    headStyles: {
      fillColor: indigo,
      textColor: [255, 255, 255],
      fontStyle: "bold",
    },
    columnStyles: {
      0: { cellWidth: 8 },
      1: { cellWidth: 40 },
      2: { cellWidth: 22 },
      3: { cellWidth: 90 },
      4: { cellWidth: 25 },
    },
    didParseCell: (data) => {
      if (data.section === "body" && data.column.index === 2) {
        const val = data.cell.raw;
        data.cell.styles.textColor =
          val === "Critical" ? red :
          val === "High"     ? orange :
          val === "Moderate" ? yellow : green;
        data.cell.styles.fontStyle = "bold";
      }
    },
    alternateRowStyles: { fillColor: [250, 250, 255] },
  });

  // ── Footer ──
  const pageCount = doc.internal.getNumberOfPages();
  for (let i = 1; i <= pageCount; i++) {
    doc.setPage(i);
    doc.setFillColor(...indigo);
    doc.rect(0, 285, 210, 15, "F");
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(8);
    doc.text("⚠️ MediVoice AI is for informational purposes only. Not a substitute for professional medical advice.", 15, 293);
    doc.text(`Page ${i} of ${pageCount}`, 185, 293);
  }

  // ── Save ──
  doc.save(`MediVoice_Report_${user}_${date.replace(/ /g, "_")}.pdf`);
}