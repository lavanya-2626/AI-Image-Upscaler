import { useState, useCallback, useEffect } from 'react';
import { upscaleApi } from '../services/api';

export const useJobHistory = (limit = 10) => {
  const [jobs, setJobs] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [total, setTotal] = useState(0);

  const fetchJobs = useCallback(async (offset = 0, status = null) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await upscaleApi.listJobs(limit, offset, status);
      setJobs(response.jobs);
      setTotal(response.total);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch jobs');
    } finally {
      setIsLoading(false);
    }
  }, [limit]);

  const deleteJob = useCallback(async (jobId) => {
    try {
      await upscaleApi.deleteJob(jobId);
      setJobs((prev) => prev.filter((job) => job.job_id !== jobId));
      setTotal((prev) => prev - 1);
      return true;
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete job');
      return false;
    }
  }, []);

  const refresh = useCallback(() => {
    fetchJobs();
  }, [fetchJobs]);

  useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  return {
    jobs,
    isLoading,
    error,
    total,
    fetchJobs,
    deleteJob,
    refresh,
  };
};
