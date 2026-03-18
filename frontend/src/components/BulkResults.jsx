import React from 'react';
import { Download, CheckCircle, XCircle, Image as ImageIcon, Archive } from 'lucide-react';
import { upscaleApi } from '../services/api';

const BulkResults = ({ results, total, successful, failed, onReset }) => {
  const handleDownload = (jobId) => {
    const url = upscaleApi.downloadResult(jobId);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'upscaled';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleDownloadAll = () => {
    results.forEach((result, index) => {
      if (result.success) {
        setTimeout(() => {
          handleDownload(result.job_id);
        }, index * 500);
      }
    });
  };

  const formatDimensions = (size) => {
    if (!size || !Array.isArray(size)) return 'Unknown';
    return `${size[0]} × ${size[1]}`;
  };

  return (
    <div className="w-full">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
        <div>
          <h3 className="text-xl font-bold text-white">Bulk Upscale Results</h3>
          <p className="text-sm text-gray-400 mt-1">
            {successful} successful, {failed} failed out of {total} images
          </p>
        </div>

        <div className="flex items-center gap-3">
          {successful > 0 && (
            <button
              onClick={handleDownloadAll}
              className="flex items-center gap-2 px-4 py-2 rounded-lg btn-primary text-white font-medium"
            >
              <Archive className="w-4 h-4" />
              Download All
            </button>
          )}
          <button
            onClick={onReset}
            className="px-4 py-2 rounded-lg glass text-gray-300 hover:text-white transition-colors"
          >
            Upscale More
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="glass rounded-xl p-4 text-center">
          <p className="text-2xl font-bold text-white">{total}</p>
          <p className="text-sm text-gray-400">Total Files</p>
        </div>
        <div className="glass rounded-xl p-4 text-center">
          <p className="text-2xl font-bold text-green-400">{successful}</p>
          <p className="text-sm text-gray-400">Successful</p>
        </div>
        <div className="glass rounded-xl p-4 text-center">
          <p className="text-2xl font-bold text-red-400">{failed}</p>
          <p className="text-sm text-gray-400">Failed</p>
        </div>
      </div>

      {/* Results List */}
      <div className="space-y-3">
        {results.map((result, index) => (
          <div
            key={index}
            className={`glass rounded-xl p-4 flex items-center gap-4 ${
              result.success ? 'border-l-4 border-l-green-500' : 'border-l-4 border-l-red-500'
            }`}
          >
            {/* Status Icon */}
            <div className="flex-shrink-0">
              {result.success ? (
                <CheckCircle className="w-6 h-6 text-green-400" />
              ) : (
                <XCircle className="w-6 h-6 text-red-400" />
              )}
            </div>

            {/* File Info */}
            <div className="flex-grow min-w-0">
              <p className="font-medium text-white truncate">
                {result.input_path?.split('/').pop() || `Image ${index + 1}`}
              </p>
              {result.success ? (
                <div className="flex items-center gap-4 text-sm text-gray-400 mt-1">
                  <span>{formatDimensions(result.original_size)} → {formatDimensions(result.upscaled_size)}</span>
                </div>
              ) : (
                <p className="text-sm text-red-400 mt-1">{result.error || 'Processing failed'}</p>
              )}
            </div>

            {/* Download Button */}
            {result.success && result.output_path && (
              <button
                onClick={() => handleDownload(result.job_id || result.output_path)}
                className="flex-shrink-0 flex items-center gap-2 px-3 py-2 rounded-lg bg-cyan-500/20 text-cyan-400 hover:bg-cyan-500/30 transition-colors"
              >
                <Download className="w-4 h-4" />
                <span className="hidden sm:inline">Download</span>
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default BulkResults;
