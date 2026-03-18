import React from 'react';
import clsx from 'clsx';

const ScaleSelector = ({ selectedScale, onScaleChange, disabled = false }) => {
  const scales = [
    {
      value: 2,
      label: '2x',
      description: 'Double the resolution',
      recommended: true,
    },
    {
      value: 4,
      label: '4x',
      description: 'Quadruple the resolution',
      recommended: false,
    },
  ];

  return (
    <div className="w-full">
      <h3 className="text-lg font-semibold text-white mb-4">Select Upscaling Factor</h3>
      <div className="grid grid-cols-2 gap-4">
        {scales.map((scale) => {
          const Icon = scale.icon;
          const isSelected = selectedScale === scale.value;

          return (
            <button
              key={scale.value}
              onClick={() => !disabled && onScaleChange(scale.value)}
              disabled={disabled}
              className={clsx(
                'relative p-6 rounded-xl border-2 transition-all duration-300 text-left',
                isSelected
                  ? 'border-cyan-500 bg-cyan-500/10'
                  : 'border-white/10 bg-white/5 hover:border-white/20',
                disabled && 'opacity-50 cursor-not-allowed'
              )}
            >
              {scale.recommended && (
                <span className="absolute -top-3 left-4 px-2 py-0.5 bg-gradient-to-r from-cyan-500 to-purple-500 text-xs font-medium text-white rounded-full">
                  Recommended
                </span>
              )}

              <div className="flex items-start gap-4">
                <div
                  className={clsx(
                    'w-12 h-12 rounded-lg flex items-center justify-center transition-colors',
                    isSelected
                      ? 'bg-cyan-500 text-white'
                      : 'bg-white/10 text-gray-400'
                  )}
                >
                  <span className="text-xl font-bold">{scale.label}</span>
                </div>

                <div>
                  <h4 className={clsx(
                    'font-semibold',
                    isSelected ? 'text-cyan-400' : 'text-white'
                  )}>
                    {scale.label} Upscale
                  </h4>
                  <p className="text-sm text-gray-400 mt-1">{scale.description}</p>
                </div>
              </div>

              {isSelected && (
                <div className="absolute bottom-4 right-4">
                  <div className="w-6 h-6 rounded-full bg-cyan-500 flex items-center justify-center">
                    <svg
                      className="w-4 h-4 text-white"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                  </div>
                </div>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default ScaleSelector;
