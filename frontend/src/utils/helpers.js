export function now() {
  return new Date().toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function todayLabel() {
  return new Date().toLocaleDateString([], {
    month: "short",
    day: "numeric",
  });
}

export function uid() {
  return Math.random().toString(36).slice(2, 10);
}

export function stripMarkdown(text) {
  if (!text) return "";

  return text
    .replace(/\*\*(.*?)\*\*/g, "$1")
    .replace(/\*(.*?)\*/g, "$1")
    .replace(/#{1,6}\s/g, "")
    .replace(/`{1,3}[^`]*`{1,3}/g, "")
    .trim();
}