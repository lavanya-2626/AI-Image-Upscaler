import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, X, Image as ImageIcon } from 'lucide-react';
import clsx from 'clsx';

const UploadZone = ({ onFilesSelected, multiple = false, disabled = false }) => {
  const [previewFiles, setPreviewFiles] = useState([]);

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length === 0) return;

    // Create previews
    const newPreviews = acceptedFiles.map((file) => ({
      file,
      preview: URL.createObjectURL(file),
      name: file.name,
      size: file.size,
    }));

    if (multiple) {
      setPreviewFiles((prev) => [...prev, ...newPreviews]);
      onFilesSelected([...previewFiles.map((p) => p.file), ...acceptedFiles]);
    } else {
      // Clean up old previews
      previewFiles.forEach((p) => URL.revokeObjectURL(p.preview));
      setPreviewFiles(newPreviews);
      onFilesSelected(acceptedFiles);
    }
  }, [multiple, onFilesSelected, previewFiles]);

  const removeFile = (index) => {
    setPreviewFiles((prev) => {
      const newPreviews = [...prev];
      URL.revokeObjectURL(newPreviews[index].preview);
      newPreviews.splice(index, 1);
      onFilesSelected(newPreviews.map((p) => p.file));
      return newPreviews;
    });
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.webp', '.bmp'],
    },
    multiple,
    disabled,
    maxSize: 50 * 1024 * 1024, // 50MB
  });

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={clsx(
          'drop-zone rounded-2xl p-8 text-center cursor-pointer transition-all duration-300',
          isDragActive && 'drag-over',
          disabled && 'opacity-50 cursor-not-allowed',
          previewFiles.length === 0 && 'py-16'
        )}
      >
        <input {...getInputProps()} />
        
        {previewFiles.length === 0 ? (
          <div className="flex flex-col items-center gap-4">
            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-cyan-500/20 to-purple-500/20 flex items-center justify-center">
              <Upload className="w-8 h-8 text-cyan-400" />
            </div>
            <div>
              <p className="text-lg font-medium text-white mb-1">
                {isDragActive ? 'Drop images here' : 'Drag & drop images here'}
              </p>
              <p className="text-sm text-gray-400">
                or click to browse from your computer
              </p>
              <p className="text-xs text-gray-500 mt-2">
                Supports: JPG, PNG, WebP, BMP (Max 50MB)
                {multiple && ' • Up to 20 files'}
              </p>
            </div>
          </div>
        ) : (
          <div className="text-left">
            <p className="text-sm text-gray-400 mb-4">
              {isDragActive ? 'Drop to add more images' : 'Drag more images or click to browse'}
            </p>
          </div>
        )}

        {previewFiles.length > 0 && (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4 mt-4">
            {previewFiles.map((file, index) => (
              <div
                key={index}
                className="relative group bg-gray-800/50 rounded-lg overflow-hidden"
              >
                <img
                  src={file.preview}
                  alt={file.name}
                  className="w-full h-32 object-cover"
                />
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    removeFile(index);
                  }}
                  className="absolute top-2 right-2 w-6 h-6 bg-red-500/80 hover:bg-red-500 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <X className="w-4 h-4 text-white" />
                </button>
                <div className="absolute bottom-0 left-0 right-0 bg-black/70 p-2">
                  <p className="text-xs text-white truncate">{file.name}</p>
                  <p className="text-xs text-gray-400">{formatFileSize(file.size)}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default UploadZone;
