import { useState, useCallback } from 'react';
import { convertApi } from '../services/convertApi';

export const useConvert = () => {
  const [isUploading, setIsUploading] = useState(false);
  const [isConverting, setIsConverting] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [uploadedImage, setUploadedImage] = useState(null);

  // Upload image
  const uploadImage = useCallback(async (file, onProgress) => {
    setIsUploading(true);
    setError(null);
    setProgress(0);

    try {
      const response = await convertApi.uploadImage(file, (uploadProgress) => {
        setProgress(uploadProgress);
        if (onProgress) onProgress(uploadProgress);
      });

      setIsUploading(false);
      setUploadedImage(response);
      return response;
    } catch (err) {
      setIsUploading(false);
      setError(err.response?.data?.detail || 'Failed to upload image');
      throw err;
    }
  }, []);

  // Upload multiple images
  const uploadImagesBulk = useCallback(async (files, onProgress) => {
    setIsUploading(true);
    setError(null);
    setProgress(0);

    try {
      const response = await convertApi.uploadImagesBulk(files, (uploadProgress) => {
        setProgress(uploadProgress);
        if (onProgress) onProgress(uploadProgress);
      });

      setIsUploading(false);
      return response;
    } catch (err) {
      setIsUploading(false);
      setError(err.response?.data?.detail || 'Failed to upload images');
      throw err;
    }
  }, []);

  // Convert image
  const convertImage = useCallback(async (id, format, quality = 85) => {
    setIsConverting(true);
    setError(null);
    setProgress(0);

    try {
      const response = await convertApi.convertImage(id, format, quality);
      setIsConverting(false);
      setResult(response);
      return response;
    } catch (err) {
      setIsConverting(false);
      setError(err.response?.data?.detail || 'Failed to convert image');
      throw err;
    }
  }, []);

  // Reset state
  const reset = useCallback(() => {
    setIsUploading(false);
    setIsConverting(false);
    setProgress(0);
    setError(null);
    setResult(null);
    setUploadedImage(null);
  }, []);

  return {
    isUploading,
    isConverting,
    progress,
    error,
    result,
    uploadedImage,
    uploadImage,
    uploadImagesBulk,
    convertImage,
    reset,
  };
};
