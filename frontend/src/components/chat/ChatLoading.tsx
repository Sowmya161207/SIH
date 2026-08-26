import React from 'react';
import { Sparkles } from 'lucide-react';

export const ChatLoading: React.FC = () => {
  return (
    <div
      className="flex gap-4 animate-fadeIn"
      style={{ padding: '20px 24px', borderBottom: '1px solid rgba(148, 163, 184, 0.04)' }}
      aria-label="AI is processing your request"
      role="status"
    >
      {/* Avatar */}
      <div className="flex-shrink-0 mt-0.5 relative">
        <div 
          className="absolute inset-0 rounded-md animate-ping" 
          style={{ background: 'rgba(99, 102, 241, 0.2)', animationDuration: '2s' }} 
        />
        <div
          className="relative h-7 w-7 rounded-md flex items-center justify-center flex-shrink-0"
          style={{
            background: 'linear-gradient(135deg, rgba(99,102,241,0.2) 0%, rgba(124,58,237,0.15) 100%)',
            border: '1px solid rgba(99, 102, 241, 0.3)',
            boxShadow: '0 0 12px rgba(99,102,241,0.2)',
          }}
        >
          <Sparkles className="h-3.5 w-3.5 animate-pulse" style={{ color: '#a5b4fc', animationDuration: '2s' }} />
        </div>
      </div>
      
      <div className="flex-1 pt-1 min-w-0">
        <div
          className="text-[10px] font-semibold mb-2.5 tracking-wider uppercase"
          style={{ color: 'rgba(99, 102, 241, 0.6)', fontFamily: "'JetBrains Mono', monospace" }}
        >
          Sovereign AI
        </div>

        <div className="flex items-center gap-2" style={{ marginTop: '2px' }}>
          <Sparkles className="h-3 w-3 animate-pulse" style={{ color: '#a5b4fc', animationDuration: '1.5s' }} />
          <span
            style={{
              fontSize: '13px',
              color: '#a5b4fc',
              fontWeight: 500,
              letterSpacing: '0.01em'
            }}
          >
            AI is analyzing your request
          </span>
          <div className="flex items-center gap-1.5 ml-1 mt-1">
            {[0, 200, 400].map((delay) => (
              <div
                key={delay}
                className="h-1 w-1 rounded-full animate-bounce"
                style={{
                  background: '#818cf8',
                  animationDelay: `${delay}ms`,
                  animationDuration: '1.2s',
                }}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatLoading;
