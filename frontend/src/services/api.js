import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/upscale`,
  headers: {
    'Content-Type': 'multipart/form-data',
  },
});

export const upscaleApi = {
  // Upload and upscale a single image
  upscaleSingle: async (file, scale = 2, onProgress) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('scale', scale);

    const response = await api.post('/single', formData, {
      onUploadProgress: (progressEvent) => {
        if (onProgress) {
          const progress = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress(progress);
        }
      },
    });
    return response.data;
  },

  // Upload and upscale multiple images
  upscaleBulk: async (files, scale = 2, onProgress) => {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });
    formData.append('scale', scale);

    const response = await api.post('/bulk', formData, {
      onUploadProgress: (progressEvent) => {
        if (onProgress) {
          const progress = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress(progress);
        }
      },
    });
    return response.data;
  },

  // Get job status
  getJobStatus: async (jobId) => {
    const response = await api.get(`/status/${jobId}`);
    return response.data;
  },

  // Get comparison URLs
  getComparison: async (jobId) => {
    const response = await api.get(`/compare/${jobId}`);
    return response.data;
  },

  // Download original image
  downloadOriginal: (jobId) => {
    return `${API_BASE_URL}/api/upscale/download/original/${jobId}`;
  },

  // Download upscaled image
  downloadResult: (jobId) => {
    return `${API_BASE_URL}/api/upscale/download/result/${jobId}`;
  },

  // List jobs
  listJobs: async (limit = 10, offset = 0, status = null) => {
    const params = { limit, offset };
    if (status) params.status = status;
    const response = await api.get('/jobs', { params });
    return response.data;
  },

  // Delete job
  deleteJob: async (jobId) => {
    const response = await api.delete(`/job/${jobId}`);
    return response.data;
  },

  // Get system status
  getSystemStatus: async () => {
    const response = await api.get('/system-status');
    return response.data;
  },
};

export default api;
