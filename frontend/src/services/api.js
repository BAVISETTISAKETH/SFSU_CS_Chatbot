import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('professorToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Chat API
export const chat = async (query, conversationHistory = null, sessionId = null) => {
  const response = await api.post('/chat', {
    query,
    conversation_history: conversationHistory,
    session_id: sessionId
  });
  return response.data;
};

// Professor Auth API
export const professorLogin = async (username, password) => {
  const response = await api.post('/professor/login', { username, password });
  return response.data;
};

export const sendOTP = async (email, name) => {
  const response = await api.post('/professor/send-otp', { email, name });
  return response.data;
};

export const verifyOTP = async (email, otp) => {
  const response = await api.post('/professor/verify-otp', { email, otp });
  return response.data;
};

export const professorRegister = async (professorData) => {
  const response = await api.post('/professor/register', professorData);
  return response.data;
};

export const professorLogout = () => {
  localStorage.removeItem('professorToken');
};

export const isLoggedIn = () => {
  return !!localStorage.getItem('professorToken');
};

// Corrections API
export const flagIncorrect = async (query, response, reason, sessionId) => {
  const res = await api.post('/corrections/flag', {
    query,
    response,
    reason,
    session_id: sessionId
  });
  return res.data;
};

// Feedback API
export const submitFeedback = async (query, response, feedbackType, sessionId = null, messageId = null) => {
  const res = await api.post('/feedback', {
    query,
    response,
    feedback_type: feedbackType,
    session_id: sessionId,
    message_id: messageId
  });
  return res.data;
};

export const getPendingCorrections = async () => {
  const response = await api.get('/professor/corrections/pending');
  return response.data;
};

export const reviewCorrection = async (correctionId, action, correctedResponse = null) => {
  const response = await api.post(`/professor/corrections/${correctionId}/review`, {
    action,
    corrected_response: correctedResponse,
  });
  return response.data;
};

// Stats API
export const getStats = async () => {
  const response = await api.get('/professor/stats');
  return response.data;
};

// Trending Questions API
export const getTrendingQuestions = async (limit = 10, days = 7) => {
  const response = await api.get(`/professor/trending-questions?limit=${limit}&days=${days}`);
  return response.data;
};

// Notifications API
export const getNotifications = async (sessionId) => {
  const response = await api.get(`/notifications/${sessionId}`);
  return response.data;
};

export const markNotificationAsRead = async (notificationId) => {
  const response = await api.post(`/notifications/${notificationId}/mark-read`);
  return response.data;
};

export const markAllNotificationsAsRead = async (sessionId) => {
  const response = await api.post(`/notifications/${sessionId}/mark-all-read`);
  return response.data;
};

// Get correction details (for viewing professor's response)
export const getCorrectionDetails = async (correctionId) => {
  const response = await api.get(`/corrections/${correctionId}`);
  return response.data;
};

export default api;
