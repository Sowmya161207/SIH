import React from 'react';
import { Source } from '../../types/chat';
import { FileText } from 'lucide-react';

interface SourceListProps {
  sources?: Source[];
}

export const SourceList: React.FC<SourceListProps> = ({ sources }) => {
  if (!sources || sources.length === 0) return null;

  return (
    <div className="mt-4 pt-3 border-t border-[#1e293b] text-xs">
      <div className="font-semibold text-slate-400 tracking-wider uppercase text-[10px] mb-2 font-mono">
        Sources
      </div>
      <div className="space-y-1.5">
        {sources.map((source, index) => (
          <div key={index} className="flex items-center space-x-2 text-slate-300 font-mono">
            <FileText className="h-3.5 w-3.5 text-indigo-400 flex-shrink-0" />
            <span className="truncate max-w-[200px] sm:max-w-md md:max-w-lg">{source.document}</span>
            <span className="text-slate-500">—</span>
            <span className="text-slate-400">Page {source.page}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
export default SourceList;
