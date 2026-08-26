import React from 'react';
import { Source } from '../../types/chat';
import { FileText } from 'lucide-react';

interface SourceListProps {
  sources?: Source[];
}

export const SourceList: React.FC<SourceListProps> = ({ sources }) => {
  if (!sources || sources.length === 0) return null;

  return (
    <div
      className="mt-4 pt-3"
      style={{ borderTop: '1px solid rgba(148, 163, 184, 0.07)' }}
    >
      <div
        className="text-[9px] font-semibold uppercase tracking-[0.12em] mb-2"
        style={{ color: 'rgba(148, 163, 184, 0.35)', fontFamily: "'JetBrains Mono', monospace" }}
      >
        Referenced Sources
      </div>
      <div className="flex flex-wrap gap-2">
        {sources.map((source, index) => (
          <div
            key={index}
            className="flex items-center gap-1.5"
            style={{
              padding: '4px 10px',
              borderRadius: '4px',
              background: 'rgba(99, 102, 241, 0.06)',
              border: '1px solid rgba(99, 102, 241, 0.12)',
              fontSize: '10px',
              color: 'rgba(148, 163, 184, 0.6)',
              fontFamily: "'JetBrains Mono', monospace",
            }}
          >
            <FileText className="h-3 w-3 flex-shrink-0" style={{ color: '#818cf8' }} />
            <span className="truncate max-w-[200px]">{source.document}</span>
            <span style={{ color: 'rgba(148, 163, 184, 0.3)' }}>p.{source.page}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
export default SourceList;
