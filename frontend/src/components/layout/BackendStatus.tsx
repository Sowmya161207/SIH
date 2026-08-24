import React, { useState, useEffect } from 'react';
import { checkHealth } from '../../services/api/health';

interface BackendStatusProps {
  showLabel?: boolean;
}

export const BackendStatus: React.FC<BackendStatusProps> = ({ showLabel = true }) => {
  const [isConnected, setIsConnected] = useState<boolean | null>(null);

  const verifyHealth = async () => {
    const health = await checkHealth();
    setIsConnected(health.status === 'ok');
  };

  useEffect(() => {
    verifyHealth();
    const interval = setInterval(verifyHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  if (isConnected === null) {
    return (
      <div className="flex items-center space-x-2 text-xs text-slate-400">
        <span className="h-2 w-2 rounded-full bg-slate-500 animate-pulse"></span>
        {showLabel && <span>Checking Connection...</span>}
      </div>
    );
  }

  return (
    <div className="flex items-center space-x-2 text-xs">
      <span
        className={`h-2 w-2 rounded-full transition-colors duration-500 ${
          isConnected
            ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]'
            : 'bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.5)] animate-pulse'
        }`}
      ></span>
      {showLabel && (
        <span className={isConnected ? 'text-emerald-400 font-medium' : 'text-rose-400 font-medium'}>
          {isConnected ? 'Backend Connected' : 'Backend Offline'}
        </span>
      )}
    </div>
  );
};
export default BackendStatus;
