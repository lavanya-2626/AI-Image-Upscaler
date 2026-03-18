import { useState, useCallback, useRef, useEffect } from 'react';
import { upscaleApi } from '../services/api';

const POLLING_INTERVAL = 2000; // 2 seconds

export const useUpscale = () => {
  const [isUploading, setIsUploading] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [jobStatus, setJobStatus] = useState(null);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const pollingRef = useRef(null);

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
      }
    };
  }, []);

  // Poll job status
  const startPolling = useCallback((jobId) => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
    }

    pollingRef.current = setInterval(async () => {
      try {
        const status = await upscaleApi.getJobStatus(jobId);
        setJobStatus(status);

        if (status.progress) {
          setProgress(status.progress);
        }

        // Stop polling if job is complete or failed
        if (status.status === 'completed' || status.status === 'failed') {
          clearInterval(pollingRef.current);
          setIsProcessing(false);
          setProgress(100);

          if (status.status === 'completed') {
            setResult(status.result || status.results);
          } else if (status.status === 'failed') {
            setError(status.error_message || 'Processing failed');
          }
        }
      } catch (err) {
        console.error('Polling error:', err);
      }
    }, POLLING_INTERVAL);
  }, []);

  // Upscale single image
  const upscaleSingle = useCallback(async (file, scale) => {
    setIsUploading(true);
    setIsProcessing(true);
    setError(null);
    setResult(null);
    setProgress(0);

    try {
      const response = await upscaleApi.upscaleSingle(file, scale, (uploadProgress) => {
        setProgress(uploadProgress * 0.3); // Upload is 30% of total progress
      });

      setIsUploading(false);
      setProgress(30);

      // Start polling for job status
      startPolling(response.job_id);

      return response.job_id;
    } catch (err) {
      setIsUploading(false);
      setIsProcessing(false);
      setError(err.response?.data?.detail || 'Failed to upload image');
      throw err;
    }
  }, [startPolling]);

  // Upscale multiple images
  const upscaleBulk = useCallback(async (files, scale) => {
    setIsUploading(true);
    setIsProcessing(true);
    setError(null);
    setResult(null);
    setProgress(0);

    try {
      const response = await upscaleApi.upscaleBulk(files, scale, (uploadProgress) => {
        setProgress(uploadProgress * 0.3);
      });

      setIsUploading(false);
      setProgress(30);

      // Start polling for job status
      startPolling(response.job_id);

      return response.job_id;
    } catch (err) {
      setIsUploading(false);
      setIsProcessing(false);
      setError(err.response?.data?.detail || 'Failed to upload images');
      throw err;
    }
  }, [startPolling]);

  // Cancel polling
  const cancel = useCallback(() => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
    }
    setIsProcessing(false);
    setIsUploading(false);
  }, []);

  // Reset state
  const reset = useCallback(() => {
    cancel();
    setProgress(0);
    setJobStatus(null);
    setError(null);
    setResult(null);
  }, [cancel]);

  return {
    isUploading,
    isProcessing,
    progress,
    jobStatus,
    error,
    result,
    upscaleSingle,
    upscaleBulk,
    cancel,
    reset,
  };
};
