import React from 'react';
import { Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import clsx from 'clsx';

const ProgressBar = ({ 
  progress, 
  status, 
  isUploading, 
  currentStep,
  error 
}) => {
  const getStatusIcon = () => {
    if (error) return <AlertCircle className="w-5 h-5 text-red-400" />;
    if (progress >= 100) return <CheckCircle className="w-5 h-5 text-green-400" />;
    return <Loader2 className="w-5 h-5 text-cyan-400 animate-spin" />;
  };

  const getStatusText = () => {
    if (error) return 'Error occurred';
    if (isUploading) return `Uploading... ${Math.round(progress)}%`;
    if (progress >= 100) return 'Completed!';
    if (currentStep) return currentStep;
    return `Processing... ${Math.round(progress)}%`;
  };

  return (
    <div className="w-full glass rounded-xl p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          {getStatusIcon()}
          <span className={clsx(
            'font-medium',
            error ? 'text-red-400' : 'text-white'
          )}>
            {getStatusText()}
          </span>
        </div>
        <span className="text-sm text-gray-400">
          {Math.round(progress)}%
        </span>
      </div>

      <div className="progress-bar">
        <div
          className={clsx(
            'progress-bar-fill',
            error && 'bg-red-500'
          )}
          style={{ width: `${progress}%` }}
        />
      </div>

      {error && (
        <div className="mt-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
          <p className="text-sm text-red-400">{error}</p>
        </div>
      )}
    </div>
  );
};

export default ProgressBar;
