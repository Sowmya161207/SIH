import React from 'react';
import BackendStatus from './BackendStatus';

export const Header: React.FC = () => {
  return (
    <header className="h-16 bg-[#0d131f] border-b border-[#1e293b] flex items-center justify-between px-8">
      <div className="flex items-center space-x-3">
        <h2 className="text-lg font-semibold text-slate-100 tracking-tight">Sovereign AI Workbench</h2>
        <span className="px-2 py-0.5 text-[10px] font-semibold text-indigo-400 bg-indigo-500/10 border border-indigo-500/20 rounded-full font-mono">
          ENTERPRISE
        </span>
      </div>
      <div>
        <BackendStatus />
      </div>
    </header>
  );
};
export default Header;
