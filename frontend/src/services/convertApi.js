import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
});

export const convertApi = {
  // Upload a single image
  uploadImage: async (file, onProgress) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
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

  // Upload multiple images
  uploadImagesBulk: async (files, onProgress) => {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });

    const response = await api.post('/upload/bulk', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
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

  // Convert an image
  convertImage: async (id, format, quality = 85) => {
    const formData = new FormData();
    formData.append('id', id);
    formData.append('format', format);
    formData.append('quality', quality);

    const response = await api.post('/convert', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Get converted image (preview)
  getImage: (imageId) => {
    return `${API_BASE_URL}/api/image/${imageId}`;
  },

  // Download converted image
  downloadImage: (imageId) => {
    return `${API_BASE_URL}/api/download/${imageId}`;
  },

  // List recent conversions
  listImages: async (limit = 20) => {
    const response = await api.get('/images', { params: { limit } });
    return response.data;
  },

  // Delete an image
  deleteImage: async (imageId) => {
    const response = await api.delete(`/image/${imageId}`);
    return response.data;
  },
};

export default convertApi;
