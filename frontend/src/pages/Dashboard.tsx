import React from 'react';
import { Database, MessageSquare, ArrowRight, Upload, Play, Eye, Cpu } from 'lucide-react';
import { DocumentResponse } from '../types/documents';
import BackendStatus from '../components/layout/BackendStatus';

interface DashboardProps {
  documents: DocumentResponse[];
  setCurrentTab: (tab: string) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ documents, setCurrentTab }) => {
  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-[#0f172a] to-slate-900 border border-[#1e293b] rounded-2xl p-8 relative overflow-hidden shadow-lg">
        <div className="absolute right-0 top-0 h-full w-1/3 bg-radial-gradient from-indigo-500/10 to-transparent pointer-events-none"></div>
        <div className="max-w-2xl relative z-10">
          <span className="px-3 py-1 text-xs font-semibold text-indigo-400 bg-indigo-500/10 border border-indigo-500/20 rounded-full font-mono uppercase tracking-wider">
            Sovereign Engine Active
          </span>
          <h1 className="text-3xl font-bold text-slate-100 tracking-tight mt-4">
            Welcome to Sovereign AI Workbench
          </h1>
          <p className="text-sm text-slate-400 mt-2 leading-relaxed">
            A secure, on-premise AI platform designed for enterprise operations. Upload critical documents, run analytics, and chat with your files without exposing sensitive data to public cloud models.
          </p>
        </div>
      </div>

      {/* Analytics Overview Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Connection Stat */}
        <div className="bg-[#0f172a] border border-[#1e293b] rounded-xl p-6 shadow-md flex flex-col justify-between h-[150px]">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 tracking-wider uppercase font-mono">System Engine</span>
            <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400">
              <Cpu className="h-5 w-5" />
            </div>
          </div>
          <div>
            <BackendStatus showLabel={false} />
            <div className="mt-2 text-xl font-bold text-slate-200">
              <BackendStatus showLabel={true} />
            </div>
          </div>
        </div>

        {/* Documents Stat */}
        <div className="bg-[#0f172a] border border-[#1e293b] rounded-xl p-6 shadow-md flex flex-col justify-between h-[150px] hover:border-slate-800 transition-colors">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 tracking-wider uppercase font-mono">Knowledge Base</span>
            <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400">
              <Database className="h-5 w-5" />
            </div>
          </div>
          <div>
            <div className="text-3xl font-extrabold text-slate-100">{documents.length}</div>
            <div className="text-xs text-slate-400 font-medium mt-1">Documents in active workspace</div>
          </div>
        </div>

        {/* AI Readiness */}
        <div className="bg-[#0f172a] border border-[#1e293b] rounded-xl p-6 shadow-md flex flex-col justify-between h-[150px] hover:border-indigo-500/30 transition-all cursor-pointer group" onClick={() => setCurrentTab('chat')}>
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 tracking-wider uppercase font-mono">AI Capability</span>
            <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 group-hover:bg-indigo-600 group-hover:text-white transition-all">
              <MessageSquare className="h-5 w-5" />
            </div>
          </div>
          <div className="flex items-end justify-between">
            <div>
              <div className="text-lg font-bold text-slate-200 group-hover:text-indigo-400 transition-colors">Ask Sovereign AI</div>
              <div className="text-xs text-slate-400 font-medium mt-0.5">Start a secure session</div>
            </div>
            <ArrowRight className="h-5 w-5 text-slate-500 group-hover:text-indigo-400 group-hover:translate-x-1 transition-all" />
          </div>
        </div>
      </div>

      {/* Quick Actions Panel */}
      <div className="space-y-4">
        <h3 className="text-sm font-semibold text-slate-400 tracking-wider uppercase font-mono">Quick Actions</h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
          <button
            onClick={() => setCurrentTab('documents')}
            className="flex items-center justify-between p-4 bg-[#090d16] hover:bg-[#0e1422] border border-[#1e293b] rounded-xl text-left transition-colors cursor-pointer group"
          >
            <div className="flex items-center space-x-3 truncate">
              <div className="p-2 rounded bg-indigo-500/10 text-indigo-400">
                <Upload className="h-4.5 w-4.5" />
              </div>
              <span className="text-sm font-semibold text-slate-300">Upload Document</span>
            </div>
            <ArrowRight className="h-4 w-4 text-slate-600 group-hover:text-indigo-400 transition-colors" />
          </button>

          <button
            onClick={() => setCurrentTab('chat')}
            className="flex items-center justify-between p-4 bg-[#090d16] hover:bg-[#0e1422] border border-[#1e293b] rounded-xl text-left transition-colors cursor-pointer group"
          >
            <div className="flex items-center space-x-3 truncate">
              <div className="p-2 rounded bg-indigo-500/10 text-indigo-400">
                <Play className="h-4.5 w-4.5" />
              </div>
              <span className="text-sm font-semibold text-slate-300">Ask AI Assistant</span>
            </div>
            <ArrowRight className="h-4 w-4 text-slate-600 group-hover:text-indigo-400 transition-colors" />
          </button>

          <button
            onClick={() => setCurrentTab('documents')}
            className="flex items-center justify-between p-4 bg-[#090d16] hover:bg-[#0e1422] border border-[#1e293b] rounded-xl text-left transition-colors cursor-pointer group"
          >
            <div className="flex items-center space-x-3 truncate">
              <div className="p-2 rounded bg-indigo-500/10 text-indigo-400">
                <Eye className="h-4.5 w-4.5" />
              </div>
              <span className="text-sm font-semibold text-slate-300">View Documents</span>
            </div>
            <ArrowRight className="h-4 w-4 text-slate-600 group-hover:text-indigo-400 transition-colors" />
          </button>
        </div>
      </div>
    </div>
  );
};
export default Dashboard;
