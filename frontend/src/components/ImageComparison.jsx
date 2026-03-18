import React, { useState, useEffect } from 'react';
import { ReactCompareSlider, ReactCompareSliderImage } from 'react-compare-slider';
import { Download, Maximize2, Minimize2, ArrowLeftRight } from 'lucide-react';
import { upscaleApi } from '../services/api';

const ImageComparison = ({ jobId, onReset }) => {
  const [comparison, setComparison] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchComparison = async () => {
      try {
        setIsLoading(true);
        const data = await upscaleApi.getComparison(jobId);
        setComparison(data);
      } catch (err) {
        setError('Failed to load comparison');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchComparison();
  }, [jobId]);

  const formatFileSize = (bytes) => {
    if (!bytes) return 'Unknown';
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleDownload = (type) => {
    const url = type === 'original' 
      ? upscaleApi.downloadOriginal(jobId)
      : upscaleApi.downloadResult(jobId);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = type === 'original' ? 'original' : 'upscaled';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (isLoading) {
    return (
      <div className="w-full h-96 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-cyan-500"></div>
      </div>
    );
  }

  if (error || !comparison) {
    return (
      <div className="w-full p-8 text-center">
        <p className="text-red-400">{error || 'Failed to load comparison'}</p>
        <button
          onClick={onReset}
          className="mt-4 btn-primary px-6 py-2 rounded-lg text-white font-medium"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className={`w-full ${isFullscreen ? 'fixed inset-0 z-50 bg-black p-4' : ''}`}>
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
        <div>
          <h3 className="text-xl font-bold text-white">Before & After Comparison</h3>
          <p className="text-sm text-gray-400 flex items-center gap-2 mt-1">
            <ArrowLeftRight className="w-4 h-4" />
            Drag slider to compare
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            className="flex items-center gap-2 px-4 py-2 rounded-lg glass text-gray-300 hover:text-white transition-colors"
          >
            {isFullscreen ? (
              <>
                <Minimize2 className="w-4 h-4" />
                Exit Fullscreen
              </>
            ) : (
              <>
                <Maximize2 className="w-4 h-4" />
                Fullscreen
              </>
            )}
          </button>

          <button
            onClick={() => handleDownload('result')}
            className="flex items-center gap-2 px-4 py-2 rounded-lg btn-primary text-white font-medium"
          >
            <Download className="w-4 h-4" />
            Download HD
          </button>

          {!isFullscreen && (
            <button
              onClick={onReset}
              className="px-4 py-2 rounded-lg glass text-gray-300 hover:text-white transition-colors"
            >
              Upscale Another
            </button>
          )}
        </div>
      </div>

      {/* Comparison Slider */}
      <div className={`relative rounded-xl overflow-hidden ${isFullscreen ? 'h-[calc(100vh-200px)]' : ''}`}>
        <ReactCompareSlider
          itemOne={
            <ReactCompareSliderImage
              src={comparison.original_url}
              alt="Original"
              style={{ objectFit: 'contain' }}
            />
          }
          itemTwo={
            <ReactCompareSliderImage
              src={comparison.upscaled_url}
              alt="Upscaled"
              style={{ objectFit: 'contain' }}
            />
          }
          className={isFullscreen ? 'h-full' : 'h-[500px]'}
          style={{ width: '100%' }}
          position={50}
        />

        {/* Labels */}
        <div className="absolute top-4 left-4 px-3 py-1 bg-black/70 rounded-full text-sm text-white">
          Original • {comparison.original_dimensions.width}×{comparison.original_dimensions.height}
        </div>
        <div className="absolute top-4 right-4 px-3 py-1 bg-cyan-500/90 rounded-full text-sm text-white">
          Upscaled {comparison.scale}x • {comparison.upscaled_dimensions.width}×{comparison.upscaled_dimensions.height}
        </div>
      </div>

      {/* Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
        <div className="glass rounded-xl p-4">
          <p className="text-sm text-gray-400">Original Dimensions</p>
          <p className="text-lg font-semibold text-white">
            {comparison.original_dimensions.width} × {comparison.original_dimensions.height}
          </p>
          <p className="text-sm text-gray-500 mt-1">
            {formatFileSize(comparison.original_size)}
          </p>
        </div>

        <div className="glass rounded-xl p-4">
          <p className="text-sm text-gray-400">Upscaled Dimensions</p>
          <p className="text-lg font-semibold text-cyan-400">
            {comparison.upscaled_dimensions.width} × {comparison.upscaled_dimensions.height}
          </p>
          <p className="text-sm text-gray-500 mt-1">
            {formatFileSize(comparison.upscaled_size)}
          </p>
        </div>

        <div className="glass rounded-xl p-4">
          <p className="text-sm text-gray-400">Upscaling Factor</p>
          <p className="text-lg font-semibold text-white">{comparison.scale}x</p>
          <p className="text-sm text-gray-500 mt-1">
            {(comparison.upscaled_dimensions.width * comparison.upscaled_dimensions.height / 
              (comparison.original_dimensions.width * comparison.original_dimensions.height)).toFixed(1)}x pixel increase
          </p>
        </div>
      </div>
    </div>
  );
};

export default ImageComparison;
