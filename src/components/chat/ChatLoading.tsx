import React from 'react';
import { Loader2 } from 'lucide-react';

export const ChatLoading: React.FC = () => {
  return (
    <div className="flex justify-start items-start space-x-3 max-w-[85%]">
      <div className="h-8 w-8 rounded-full bg-slate-800 border border-[#1e293b] flex items-center justify-center flex-shrink-0 text-indigo-400">
        <Loader2 className="h-4 w-4 animate-spin" />
      </div>
      <div className="bg-[#0f172a] border border-[#1e293b] rounded-2xl rounded-tl-none px-4 py-3 text-sm text-slate-400">
        <div className="flex items-center space-x-2">
          <div className="h-1.5 w-1.5 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
          <div className="h-1.5 w-1.5 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
          <div className="h-1.5 w-1.5 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
          <span className="text-xs text-slate-500 font-mono ml-1">Sovereign AI is analyzing...</span>
        </div>
      </div>
    </div>
  );
};
export default ChatLoading;
