import axios from "axios";


// ─────────────────────────────────────────────
// AXIOS INSTANCE
// ─────────────────────────────────────────────

const api = axios.create({

  baseURL: "http://127.0.0.1:8000",
});


// ─────────────────────────────────────────────
// TOKEN INTERCEPTOR
// ─────────────────────────────────────────────

api.interceptors.request.use(

  (config) => {

    const token = localStorage.getItem(
      "token"
    );

    if (token) {

      config.headers.Authorization =
        `Bearer ${token}`;
    }

    return config;
  }
);


// ─────────────────────────────────────────────
// AUTH APIs
// ─────────────────────────────────────────────

export const signupUser = (data) =>

  api.post(
    "/api/auth/signup",
    data
  );


export const loginUser = (data) =>

  api.post(
    "/api/auth/login",
    data
  );


// ─────────────────────────────────────────────
// CHAT API
// ─────────────────────────────────────────────

export const sendMessage = (data) =>

  api.post(
    "/api/conversation/chat",
    data
  );


// ─────────────────────────────────────────────
// IMAGE OCR API
// ─────────────────────────────────────────────

export const uploadMedicalImage = (
  formData
) =>

  api.post(

    "/api/uploads/image",

    formData,

    {
      headers: {

        "Content-Type":
          "multipart/form-data",
      },
    }
  );



// ─────────────────────────────────────────────
// REMINDER APIs
// ─────────────────────────────────────────────

export const createReminder = (
  data
) =>

  api.post(
    "/api/reminders/create",
    data
  );


export const getReminders = (
  userId
) =>

  api.get(
    `/api/reminders/${userId}`
  );


export const updateReminderStatus = (

  reminderId,

  status

) =>

  api.put(

    `/api/reminders/status/${reminderId}`,

    {

      status,
    }
  );


export const deleteReminder = (
  reminderId
) =>

  api.delete(
    `/api/reminders/${reminderId}`
  );

// ─────────────────────────────────────────────
// PDF UPLOAD API
// ─────────────────────────────────────────────

export const uploadMedicalPDF = (
  formData
) =>

  api.post(

    "/api/uploads/pdf",

    formData,

    {
      headers: {

        "Content-Type":
          "multipart/form-data",
      },
    }
  );


// ─────────────────────────────────────────────
// PDF CHAT API
// ─────────────────────────────────────────────

export const askPDFQuestion = (
  formData
) =>

  api.post(

    "/api/uploads/pdf/chat",

    formData,

    {
      headers: {

        "Content-Type":
          "multipart/form-data",
      },
    }
  );


// ─────────────────────────────────────────────
// ANALYTICS APIs
// ─────────────────────────────────────────────

export const saveHealthHistory = (
  data
) =>

  api.post(
    "/api/analytics/save",
    data
  );


export const getHealthHistory = (
  userId
) =>

  api.get(
    `/api/analytics/history/${userId}`
  );


export const getDashboardAnalytics = (
  userId
) =>

  api.get(
    `/api/analytics/dashboard/${userId}`
  );


// ─────────────────────────────────────────────
// EXPORT DEFAULT
// ─────────────────────────────────────────────

export default api;