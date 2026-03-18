import React from 'react';
import { RefreshCw, Trash2, Image as ImageIcon, Clock, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { useJobHistory } from '../hooks/useJobHistory';

const JobHistory = ({ onSelectJob }) => {
  const { jobs, isLoading, error, deleteJob, refresh } = useJobHistory(10);

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-400" />;
      case 'processing':
        return <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />;
      case 'failed':
        return <AlertCircle className="w-4 h-4 text-red-400" />;
      default:
        return <Clock className="w-4 h-4 text-yellow-400" />;
    }
  };

  const getStatusClass = (status) => {
    switch (status) {
      case 'completed':
        return 'badge-completed';
      case 'processing':
        return 'badge-processing';
      case 'failed':
        return 'badge-failed';
      default:
        return 'badge-pending';
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown';
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const handleDelete = async (e, jobId) => {
    e.stopPropagation();
    if (window.confirm('Are you sure you want to delete this job?')) {
      await deleteJob(jobId);
    }
  };

  if (isLoading) {
    return (
      <div className="glass rounded-xl p-8 text-center">
        <Loader2 className="w-8 h-8 text-cyan-400 animate-spin mx-auto mb-4" />
        <p className="text-gray-400">Loading job history...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass rounded-xl p-8 text-center">
        <AlertCircle className="w-8 h-8 text-red-400 mx-auto mb-4" />
        <p className="text-red-400">{error}</p>
        <button
          onClick={refresh}
          className="mt-4 text-cyan-400 hover:text-cyan-300 transition-colors"
        >
          Try again
        </button>
      </div>
    );
  }

  if (jobs.length === 0) {
    return (
      <div className="glass rounded-xl p-8 text-center">
        <ImageIcon className="w-12 h-12 text-gray-600 mx-auto mb-4" />
        <p className="text-gray-400">No jobs yet. Start by uploading an image!</p>
      </div>
    );
  }

  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">Recent Jobs</h3>
        <button
          onClick={refresh}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg glass text-sm text-gray-300 hover:text-white transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>

      <div className="space-y-3">
        {jobs.map((job) => (
          <div
            key={job.job_id}
            onClick={() => job.status === 'completed' && onSelectJob(job.job_id)}
            className={`glass rounded-xl p-4 flex items-center gap-4 transition-all ${
              job.status === 'completed'
                ? 'cursor-pointer hover:bg-white/10'
                : ''
            }`}
          >
            {/* Status */}
            <div className="flex-shrink-0">
              {getStatusIcon(job.status)}
            </div>

            {/* Job Info */}
            <div className="flex-grow min-w-0">
              <div className="flex items-center gap-2">
                <p className="font-medium text-white truncate">
                  {job.original_filename || 'Untitled'}
                </p>
                <span className={`badge ${getStatusClass(job.status)}`}>
                  {job.status}
                </span>
              </div>
              <div className="flex items-center gap-4 text-sm text-gray-400 mt-1">
                <span>{job.job_type === 'bulk' ? 'Bulk' : 'Single'}</span>
                <span>•</span>
                <span>{job.scale}x upscale</span>
                <span>•</span>
                <span>{formatDate(job.created_at)}</span>
              </div>
            </div>

            {/* Actions */}
            <button
              onClick={(e) => handleDelete(e, job.job_id)}
              className="flex-shrink-0 p-2 rounded-lg text-gray-400 hover:text-red-400 hover:bg-red-500/10 transition-colors"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default JobHistory;
