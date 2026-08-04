// src/api/api.js

import axios from "axios";

// ─────────────────────────────────────────────
// AXIOS INSTANCE
// ─────────────────────────────────────────────

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
  timeout: 30000, // 30 seconds timeout for large file uploads
});

// ─────────────────────────────────────────────
// TOKEN INTERCEPTOR
// ─────────────────────────────────────────────

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// ─────────────────────────────────────────────
// RESPONSE INTERCEPTOR (for better error handling)
// ─────────────────────────────────────────────

api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle 401 Unauthorized
    if (error.response && error.response.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      // Redirect to login if not already there
      if (!window.location.pathname.includes("/login")) {
        window.location.href = "/login";
      }
    }
    
    // Log errors for debugging
    console.error("API Error:", error.response?.data || error.message);
    
    return Promise.reject(error);
  }
);

// ─────────────────────────────────────────────
// AUTH APIs
// ─────────────────────────────────────────────

export const signupUser = (data) =>
  api.post("/api/auth/signup", data);

export const loginUser = (data) =>
  api.post("/api/auth/login", data);

export const logoutUser = () => {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  window.location.href = "/login";
};

// ─────────────────────────────────────────────
// CHAT API - Regular conversation
// ─────────────────────────────────────────────

export const sendMessage = (data) => {
  return api.post("/api/conversation/chat", {
    user_id: data.user_id,
    message: data.message,
    conversation_id: data.conversation_id || null,
    latitude: data.latitude || null,
    longitude: data.longitude || null
  });
};

// ─────────────────────────────────────────────
// DOCUMENT UPLOAD APIs (UPDATED)
// ─────────────────────────────────────────────

/**
 * Upload and Ask First Question (Combined - with automatic text extraction)
 * This endpoint handles both text extraction AND question answering in one request
 * 
 * @param {FormData} formData - Should contain: file, question, user_id
 * @returns {Promise} - Returns analysis result with vision_enabled flag
 */
export const uploadAndAsk = (formData) => {
  return api.post("/api/uploads/upload-and-ask", formData, {
    headers: { 
      "Content-Type": "multipart/form-data",
    },
  });
};

/**
 * Upload document with client-side extracted text (for optimization)
 * Use this when you already have extracted text from the file on the client
 * 
 * @param {FormData} formData - Should contain: file, question, user_id, extracted_text
 * @returns {Promise} - Returns analysis result
 */
export const uploadAndAskWithText = (formData) => {
  return api.post("/api/uploads/upload-and-ask-with-text", formData, {
    headers: { 
      "Content-Type": "multipart/form-data",
    },
  });
};

// ─────────────────────────────────────────────
// PDF UPLOAD APIs (UPDATED)
// ─────────────────────────────────────────────

/**
 * Upload and parse PDF - extracts all text with OCR for images
 * Returns: total_pages, text_pages, image_pages, has_text flag, etc.
 */
export const uploadPDF = (formData) =>
  api.post("/api/uploads/pdf/parse", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

// ─────────────────────────────────────────────
// IMAGE UPLOAD APIs (UPDATED)
// ─────────────────────────────────────────────

/**
 * Upload and parse Image - OCR to extract text
 * Returns: total_characters, word_count, has_text flag, etc.
 */
export const uploadImage = (formData) =>
  api.post("/api/uploads/image/parse", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

// ─────────────────────────────────────────────
// QUESTION ANSWERING (UPDATED)
// ─────────────────────────────────────────────

/**
 * Ask question about a document
 * Automatically detects if image has text and uses vision if needed
 * 
 * @param {Object} data - { report_id, question, user_id, conversation_id? }
 * @returns {Promise} - Returns answer with vision_enabled flag
 */
export const askQuestion = (data) => {
  const formData = new FormData();
  formData.append("report_id", data.report_id);
  formData.append("question", data.question);
  formData.append("user_id", data.user_id);
  if (data.conversation_id) formData.append("conversation_id", data.conversation_id);
  
  return api.post("/api/uploads/ask", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

// ─────────────────────────────────────────────
// HELPERS FOR VISION ANALYSIS
// ─────────────────────────────────────────────

/**
 * Check if the response used vision analysis
 * @param {Object} response - The API response
 * @returns {boolean} - True if vision was used
 */
export const isVisionAnalysis = (response) => {
  return response?.data?.vision_enabled === true;
};

/**
 * Get the model used for analysis
 * @param {Object} response - The API response
 * @returns {string} - Model name or 'Unknown'
 */
export const getAnalysisModel = (response) => {
  return response?.data?.model_used || 'Unknown';
};

/**
 * Check if the uploaded image contains text
 * @param {Object} response - The API response from upload
 * @returns {boolean} - True if image has text
 */
export const hasTextContent = (response) => {
  return response?.data?.has_text_content === true;
};

// ─────────────────────────────────────────────
// LEGACY ENDPOINTS (for backward compatibility)
// ─────────────────────────────────────────────

// Legacy PDF upload (redirects to /pdf/parse)
export const uploadLegacyPDF = (formData) =>
  api.post("/api/uploads/pdf", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

// Legacy image upload (redirects to /image/parse)
export const uploadLegacyImage = (formData) =>
  api.post("/api/uploads/image", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

// Legacy PDF chat (redirects to /ask)
export const askPDFQuestion = (data) => {
  const formData = new FormData();
  formData.append("report_id", data.report_id);
  formData.append("question", data.question);
  formData.append("user_id", data.user_id);
  if (data.conversation_id) formData.append("conversation_id", data.conversation_id);
  
  return api.post("/api/uploads/pdf/chat", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

// ─────────────────────────────────────────────
// REPORT APIs
// ─────────────────────────────────────────────

export const getReportStatus = (reportId) =>
  api.get(`/api/uploads/report/${reportId}/status`);

export const deleteReport = (reportId, userId) => {
  const formData = new FormData();
  formData.append("user_id", userId);
  return api.delete(`/api/uploads/report/${reportId}`, {
    data: formData,
  });
};

// Get all reports for a user
export const getUserReports = (userId) =>
  api.get(`/api/uploads/reports/${userId}`);

// ─────────────────────────────────────────────
// CONVERSATION APIs
// ─────────────────────────────────────────────

export const getConversation = (conversationId) =>
  api.get(`/api/uploads/conversation/${conversationId}`);

export const getUserConversations = (userId) =>
  api.get(`/api/uploads/conversations/${userId}`);

export const deleteConversation = (conversationId) =>
  api.delete(`/api/uploads/conversation/${conversationId}`);

// ─────────────────────────────────────────────
// REMINDER APIs
// ─────────────────────────────────────────────

export const createReminder = (data) =>
  api.post("/api/reminders/create", data);

export const getReminders = (userId) =>
  api.get(`/api/reminders/${userId}`);

// Kept for older callers; medication logs are the source of truth for tracker
// and analytics, and are scoped to the authenticated user by the backend.
export const getDoseLogs = () =>
  api.get("/api/medications/history");

export const markDoseTaken = (doseLogId) =>
  api.put(`/api/reminders/dose/${doseLogId}/taken`);

export const updateReminderStatus = (reminderId, status) =>
  api.put(`/api/reminders/status/${reminderId}`, { status });

export const deleteReminder = (reminderId) =>
  api.delete(`/api/reminders/${reminderId}`);

// ─────────────────────────────────────────────
// ANALYTICS APIs
// ─────────────────────────────────────────────

export const saveHealthHistory = (data) =>
  api.post("/api/analytics/save", data);

export const getHealthHistory = (userId) =>
  api.get(`/api/analytics/history/${userId}`);

export const getDashboardAnalytics = (userId) =>
  api.get(`/api/analytics/dashboard/${userId}`);

export const getHealthAnalyticsDashboard = () =>
  api.get("/api/analytics/dashboard");

export const markSymptomResolved = (symptomId) =>
  api.patch(`/api/analytics/symptoms/${symptomId}/resolve`);

export const getMedicationStatistics = () =>
  api.get("/api/medications/statistics");

export const getMedicationHistory = () =>
  api.get("/api/medications/history");

export const getMedicationToday = () =>
  api.get("/api/medications/today");

export const updateMedicationLogStatus = (logId, status) =>
  api.patch(`/api/medications/${logId}/status`, { status });

// ─────────────────────────────────────────────
// HEALTH CHECK
// ─────────────────────────────────────────────

export const healthCheck = () =>
  api.get("/api/uploads/health");

// ─────────────────────────────────────────────
// FILE UPLOAD UTILITY FUNCTIONS
// ─────────────────────────────────────────────

/**
 * Prepare FormData for file upload with question
 * @param {File} file - The file to upload
 * @param {string} question - User's question
 * @param {number} userId - User ID
 * @param {string} extractedText - Optional pre-extracted text
 * @returns {FormData} - FormData ready for upload
 */
export const prepareUploadFormData = (file, question, userId, extractedText = null) => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("question", question);
  formData.append("user_id", userId);
  if (extractedText) {
    formData.append("extracted_text", extractedText);
  }
  return formData;
};

/**
 * Get file extension from filename
 * @param {string} filename - The filename
 * @returns {string} - File extension (lowercase, without dot)
 */
export const getFileExtension = (filename) => {
  return filename.split('.').pop().toLowerCase();
};

/**
 * Check if file is an image
 * @param {string} filename - The filename
 * @returns {boolean} - True if image file
 */
export const isImageFile = (filename) => {
  const imageExtensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'];
  return imageExtensions.includes(getFileExtension(filename));
};

/**
 * Check if file is a PDF
 * @param {string} filename - The filename
 * @returns {boolean} - True if PDF file
 */
export const isPDFFile = (filename) => {
  return getFileExtension(filename) === 'pdf';
};

/**
 * Check if file is a document (PDF or image)
 * @param {string} filename - The filename
 * @returns {boolean} - True if document file
 */
export const isDocumentFile = (filename) => {
  const documentExtensions = ['pdf', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'];
  return documentExtensions.includes(getFileExtension(filename));
};

// ─────────────────────────────────────────────
// EXPORT DEFAULT
// ─────────────────────────────────────────────

export default api;
