import React from 'react';
import { Sparkles, Github, Info } from 'lucide-react';

const Header = () => {
  return (
    <header className="w-full py-6 px-4">
      <div className="max-w-6xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-400 to-purple-600 flex items-center justify-center">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold gradient-text">Image Upscaler</h1>
            <p className="text-sm text-gray-400">AI-Powered Enhancement</p>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          <a
            href="/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-4 py-2 rounded-lg glass text-sm text-gray-300 hover:text-white transition-colors"
          >
            <Info className="w-4 h-4" />
            API Docs
          </a>
          <a
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-4 py-2 rounded-lg glass text-sm text-gray-300 hover:text-white transition-colors"
          >
            <Github className="w-4 h-4" />
            GitHub
          </a>
        </div>
      </div>
    </header>
  );
};

export default Header;
