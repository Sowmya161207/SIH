import React from 'react';
import BackendStatus from '../components/layout/BackendStatus';
import NetworkMonitor from '../components/layout/NetworkMonitor';
import CodeSandboxPanel from '../components/chat/CodeSandboxPanel';
import { ShieldCheck, Cpu, Terminal } from 'lucide-react';

export const SystemStatus: React.FC = () => {
  const routes = [
    { method: 'GET', path: '/api/health', desc: 'Checks live connection state' },
    { method: 'POST', path: '/api/chat', desc: 'Queries models with local context history' },
    { method: 'POST', path: '/api/documents', desc: 'Uploads and indexes PDF documents' },
    { method: 'POST', path: '/api/generate/approval-note', desc: 'Exports Word (.docx) approval notes' },
    { method: 'POST', path: '/api/sandbox/run', desc: 'Runs Python code in isolated sandbox' },
    { method: 'GET', path: '/api/telemetry/network-calls', desc: 'Verifies 0-external-call air-gap audit' },
  ];

  return (
    <div className="space-y-8 animate-fadeIn max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 tracking-tight">System Status & Sovereign Auditing</h1>
        <p className="text-xs text-slate-400 mt-1">
          Real-time diagnostics, local sandbox execution, and network sovereignty proof.
        </p>
      </div>

      {/* Network Sovereignty Audit Monitor */}
      <NetworkMonitor />

      {/* Interactive Code Execution Sandbox */}
      <CodeSandboxPanel />

      {/* Main Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-[#0f172a] border border-[#1e293b] rounded-xl p-6 shadow-md space-y-4">
          <div className="flex items-center space-x-3 text-slate-300">
            <Cpu className="h-5 w-5 text-indigo-400" />
            <h3 className="text-sm font-semibold">Instance Diagnostics</h3>
          </div>

          <div className="space-y-3 pt-2 text-xs">
            <div className="flex items-center justify-between border-b border-[#1e293b]/40 pb-2">
              <span className="text-slate-500">Backend Status</span>
              <BackendStatus />
            </div>
            <div className="flex items-center justify-between border-b border-[#1e293b]/40 pb-2">
              <span className="text-slate-500">API Runtime</span>
              <span className="text-slate-300 font-medium">FastAPI (Python)</span>
            </div>
            <div className="flex items-center justify-between border-b border-[#1e293b]/40 pb-2">
              <span className="text-slate-500">Deployment Environment</span>
              <span className="text-indigo-400 font-semibold font-mono">On-Premise (Private Enclave)</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-500">AI Services Orchestration</span>
              <span className="text-slate-300 font-medium">Managed by Backend</span>
            </div>
          </div>
        </div>

        <div className="bg-[#0f172a] border border-[#1e293b] rounded-xl p-6 shadow-md space-y-4">
          <div className="flex items-center space-x-3 text-slate-300">
            <ShieldCheck className="h-5 w-5 text-emerald-400" />
            <h3 className="text-sm font-semibold">Security Profile</h3>
          </div>

          <div className="space-y-3 pt-2 text-xs">
            <div className="flex items-center justify-between border-b border-[#1e293b]/40 pb-2">
              <span className="text-slate-500">Data Isolation</span>
              <span className="text-emerald-400 font-semibold">Strict / 100% Local</span>
            </div>
            <div className="flex items-center justify-between border-b border-[#1e293b]/40 pb-2">
              <span className="text-slate-500">Network Bound</span>
              <span className="text-slate-300">No external telemetry allowed</span>
            </div>
            <div className="flex items-center justify-between border-b border-[#1e293b]/40 pb-2">
              <span className="text-slate-500">Vector Storage</span>
              <span className="text-slate-300 font-mono">Chroma / SQLite local</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-500">LLM Provider</span>
              <span className="text-slate-300">Self-Hosted / Local GGUF</span>
            </div>
          </div>
        </div>
      </div>

      {/* API Mapping Diagnostics */}
      <div className="bg-[#0f172a] border border-[#1e293b] rounded-xl p-6 shadow-md space-y-4">
        <div className="flex items-center space-x-3 text-slate-300">
          <Terminal className="h-5 w-5 text-indigo-400" />
          <h3 className="text-sm font-semibold">Backend API Endpoint Map</h3>
        </div>
        <p className="text-xs text-slate-500">
          This Sovereign workspace relies on the following backend routers for indexing and inference. No public cloud APIs are mapped.
        </p>

        <div className="overflow-x-auto pt-2">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="border-b border-[#1e293b] text-slate-500">
                <th className="pb-3 font-semibold w-24">Method</th>
                <th className="pb-3 font-semibold font-mono">Endpoint Path</th>
                <th className="pb-3 font-semibold text-right">Description</th>
              </tr>
            </thead>
            <tbody>
              {routes.map((route, idx) => (
                <tr key={idx} className="border-b border-[#1e293b]/30 last:border-0 hover:bg-[#090d16]/30">
                  <td className="py-3 font-bold">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] ${
                        route.method === 'GET'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          : 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20'
                      }`}
                    >
                      {route.method}
                    </span>
                  </td>
                  <td className="py-3 font-mono text-slate-300">{route.path}</td>
                  <td className="py-3 text-slate-400 text-right">{route.desc}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
export default SystemStatus;
