import React, { useState, useCallback } from 'react';
import { Upload, Image, History, Zap, Layers } from 'lucide-react';
import Header from './components/Header';
import UploadZone from './components/UploadZone';
import ScaleSelector from './components/ScaleSelector';
import ProgressBar from './components/ProgressBar';
import ImageComparison from './components/ImageComparison';
import BulkResults from './components/BulkResults';
import JobHistory from './components/JobHistory';
import { useUpscale } from './hooks/useUpscale';
import clsx from 'clsx';

function App() {
  const [activeTab, setActiveTab] = useState('single'); // 'single' | 'bulk' | 'history'
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [selectedScale, setSelectedScale] = useState(2);
  const [currentJobId, setCurrentJobId] = useState(null);
  const [showResults, setShowResults] = useState(false);

  const {
    isUploading,
    isProcessing,
    progress,
    jobStatus,
    error,
    result,
    upscaleSingle,
    upscaleBulk,
    reset,
  } = useUpscale();

  const handleFilesSelected = useCallback((files) => {
    setSelectedFiles(files);
  }, []);

  const handleUpscale = async () => {
    if (selectedFiles.length === 0) return;

    try {
      let jobId;
      if (activeTab === 'single') {
        jobId = await upscaleSingle(selectedFiles[0], selectedScale);
      } else {
        jobId = await upscaleBulk(selectedFiles, selectedScale);
      }
      setCurrentJobId(jobId);
      setShowResults(true);
    } catch (err) {
      console.error('Upscale failed:', err);
    }
  };

  const handleReset = () => {
    reset();
    setSelectedFiles([]);
    setCurrentJobId(null);
    setShowResults(false);
  };

  const handleSelectJobFromHistory = (jobId) => {
    setCurrentJobId(jobId);
    setShowResults(true);
    setActiveTab('single');
  };

  const canUpscale = selectedFiles.length > 0 && !isUploading && !isProcessing;

  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="flex-grow container mx-auto px-4 py-8 max-w-6xl">
        {/* Tab Navigation */}
        <div className="flex justify-center mb-8">
          <div className="glass rounded-xl p-1 inline-flex">
            <button
              onClick={() => {
                setActiveTab('single');
                handleReset();
              }}
              className={clsx(
                'flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-all',
                activeTab === 'single'
                  ? 'bg-gradient-to-r from-cyan-500 to-purple-600 text-white'
                  : 'text-gray-400 hover:text-white'
              )}
            >
              <Upload className="w-5 h-5" />
              Single Image
            </button>
            <button
              onClick={() => {
                setActiveTab('bulk');
                handleReset();
              }}
              className={clsx(
                'flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-all',
                activeTab === 'bulk'
                  ? 'bg-gradient-to-r from-cyan-500 to-purple-600 text-white'
                  : 'text-gray-400 hover:text-white'
              )}
            >
              <Image className="w-5 h-5" />
              Bulk Upscale
            </button>
            <button
              onClick={() => {
                setActiveTab('history');
                handleReset();
              }}
              className={clsx(
                'flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-all',
                activeTab === 'history'
                  ? 'bg-gradient-to-r from-cyan-500 to-purple-600 text-white'
                  : 'text-gray-400 hover:text-white'
              )}
            >
              <History className="w-5 h-5" />
              History
            </button>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="glass rounded-2xl p-6 md:p-8">
          {showResults && currentJobId ? (
            // Show Results
            activeTab === 'bulk' && result && Array.isArray(result) ? (
              <BulkResults
                results={result}
                total={jobStatus?.total_files || result.length}
                successful={jobStatus?.processed_files || result.filter(r => r.success).length}
                failed={jobStatus?.failed_files || result.filter(r => !r.success).length}
                onReset={handleReset}
              />
            ) : (
              <ImageComparison
                jobId={currentJobId}
                onReset={handleReset}
              />
            )
          ) : (
            // Show Upload/Process UI
            <>
              {activeTab === 'history' ? (
                <JobHistory onSelectJob={handleSelectJobFromHistory} />
              ) : (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  {/* Left Column - Upload */}
                  <div>
                    <h2 className="text-xl font-semibold text-white mb-4">
                      {activeTab === 'single' ? 'Upload Image' : 'Upload Images'}
                    </h2>
                    <UploadZone
                      onFilesSelected={handleFilesSelected}
                      multiple={activeTab === 'bulk'}
                      disabled={isUploading || isProcessing}
                    />
                    {activeTab === 'bulk' && selectedFiles.length > 0 && (
                      <p className="text-sm text-gray-400 mt-3">
                        {selectedFiles.length} file{selectedFiles.length !== 1 ? 's' : ''} selected
                      </p>
                    )}
                  </div>

                  {/* Right Column - Settings & Action */}
                  <div className="space-y-6">
                    <ScaleSelector
                      selectedScale={selectedScale}
                      onScaleChange={setSelectedScale}
                      disabled={isUploading || isProcessing}
                    />

                    {/* Upscale Button */}
                    <button
                      onClick={handleUpscale}
                      disabled={!canUpscale}
                      className={clsx(
                        'w-full py-4 rounded-xl font-semibold text-lg flex items-center justify-center gap-3 transition-all',
                        canUpscale
                          ? 'btn-primary text-white'
                          : 'bg-gray-700 text-gray-500 cursor-not-allowed'
                      )}
                    >
                      <Zap className="w-6 h-6" />
                      {activeTab === 'single'
                        ? `Upscale to ${selectedScale}x`
                        : `Upscale ${selectedFiles.length || ''} Image${selectedFiles.length !== 1 ? 's' : ''} to ${selectedScale}x`}
                    </button>

                    {/* Progress */}
                    {(isUploading || isProcessing || error) && (
                      <ProgressBar
                        progress={progress}
                        status={jobStatus?.status}
                        isUploading={isUploading}
                        currentStep={jobStatus?.current_step}
                        error={error}
                      />
                    )}

                    {/* Features Info */}
                    <div className="grid grid-cols-2 gap-4 mt-6">
                      <div className="flex items-start gap-3">
                        <div className="w-10 h-10 rounded-lg bg-cyan-500/20 flex items-center justify-center flex-shrink-0">
                          <Layers className="w-5 h-5 text-cyan-400" />
                        </div>
                        <div>
                          <h4 className="font-medium text-white text-sm">RealESRGAN</h4>
                          <p className="text-xs text-gray-400 mt-0.5">
                            AI-powered upscaling with state-of-the-art models
                          </p>
                        </div>
                      </div>
                      <div className="flex items-start gap-3">
                        <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center flex-shrink-0">
                          <Zap className="w-5 h-5 text-purple-400" />
                        </div>
                        <div>
                          <h4 className="font-medium text-white text-sm">Queue Processing</h4>
                          <p className="text-xs text-gray-400 mt-0.5">
                            Background processing with real-time progress
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="py-6 text-center text-sm text-gray-500">
        <p>Powered by RealESRGAN • Built with FastAPI & React</p>
      </footer>
    </div>
  );
}

export default App;
