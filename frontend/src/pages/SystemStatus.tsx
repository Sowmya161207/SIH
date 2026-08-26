import React from 'react';
import BackendStatus from '../components/layout/BackendStatus';
import { ShieldCheck, Cpu, Terminal } from 'lucide-react';

const cardStyle = {
  background: '#0f172a',
  border: '1px solid rgba(148, 163, 184, 0.08)',
  borderRadius: '12px',
  padding: '24px',
};

const rowStyle = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  paddingBottom: '12px',
  borderBottom: '1px solid rgba(148, 163, 184, 0.05)',
  marginBottom: '12px',
};

const labelStyle = { fontSize: '12px', color: 'rgba(148, 163, 184, 0.4)' };
const valueStyle = { fontSize: '12px', color: 'rgba(226, 232, 240, 0.7)', fontFamily: "'JetBrains Mono', monospace", letterSpacing: '0.02em' };

export const SystemStatus: React.FC = () => {
  const routes = [
    { method: 'GET', path: '/api/health', desc: 'Checks live connection state' },
    { method: 'POST', path: '/api/chat', desc: 'Queries model with local context' },
    { method: 'POST', path: '/api/documents', desc: 'Uploads and indexes documents' },
    { method: 'GET', path: '/api/documents/{id}', desc: 'Polls document analyzer state' },
  ];

  return (
    <div className="min-h-full animate-fadeIn">
      {/* Page header */}
      <div
        className="relative overflow-hidden"
        style={{
          background: 'linear-gradient(180deg, #0a0f1a 0%, #080c15 100%)',
          borderBottom: '1px solid rgba(148, 163, 184, 0.06)',
          padding: '32px 48px 28px',
        }}
      >
        <div className="absolute inset-0 bg-grid opacity-40" style={{ pointerEvents: 'none' }} />
        <div className="relative">
          <h1 style={{ fontSize: '22px', fontWeight: 800, color: '#f1f5f9', letterSpacing: '-0.025em' }}>
            System Status
          </h1>
          <p className="mt-1.5" style={{ fontSize: '13px', color: 'rgba(148, 163, 184, 0.5)' }}>
            Diagnostics and endpoint configuration for the Sovereign Enterprise instance.
          </p>
        </div>
      </div>

      <div style={{ padding: '32px 48px', maxWidth: '1000px' }}>
        <div className="grid grid-cols-2 gap-5 mb-5">
          {/* Instance Diagnostics */}
          <div style={cardStyle}>
            <div className="flex items-center gap-2 mb-5">
              <div style={{ color: '#818cf8' }}><Cpu className="h-4 w-4" /></div>
              <span style={{ fontSize: '9px', fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase', color: 'rgba(148, 163, 184, 0.4)', fontFamily: "'JetBrains Mono', monospace" }}>
                Instance Diagnostics
              </span>
            </div>
            <div>
              <div style={rowStyle}>
                <span style={labelStyle}>Backend Status</span>
                <BackendStatus />
              </div>
              <div style={rowStyle}>
                <span style={labelStyle}>API Runtime</span>
                <span style={valueStyle}>FastAPI (Python)</span>
              </div>
              <div style={rowStyle}>
                <span style={labelStyle}>Deployment</span>
                <span style={{ ...valueStyle, color: '#818cf8' }}>On-Premise · Private</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={labelStyle}>AI Orchestration</span>
                <span style={valueStyle}>Backend Managed</span>
              </div>
            </div>
          </div>

          {/* Security Profile */}
          <div style={cardStyle}>
            <div className="flex items-center gap-2 mb-5">
              <div style={{ color: '#34d399' }}><ShieldCheck className="h-4 w-4" /></div>
              <span style={{ fontSize: '9px', fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase', color: 'rgba(148, 163, 184, 0.4)', fontFamily: "'JetBrains Mono', monospace" }}>
                Security Profile
              </span>
            </div>
            <div>
              <div style={rowStyle}>
                <span style={labelStyle}>Data Isolation</span>
                <span style={{ ...valueStyle, color: '#34d399' }}>Strict · 100% Local</span>
              </div>
              <div style={rowStyle}>
                <span style={labelStyle}>Network Policy</span>
                <span style={valueStyle}>No external telemetry</span>
              </div>
              <div style={rowStyle}>
                <span style={labelStyle}>Vector Storage</span>
                <span style={valueStyle}>Chroma / SQLite</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={labelStyle}>LLM Provider</span>
                <span style={valueStyle}>Self-Hosted GGUF</span>
              </div>
            </div>
          </div>
        </div>

        {/* API Endpoint Map */}
        <div style={cardStyle}>
          <div className="flex items-center gap-2 mb-5">
            <div style={{ color: '#818cf8' }}><Terminal className="h-4 w-4" /></div>
            <span style={{ fontSize: '9px', fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase', color: 'rgba(148, 163, 184, 0.4)', fontFamily: "'JetBrains Mono', monospace" }}>
              Backend API Endpoint Map
            </span>
          </div>
          <p style={{ fontSize: '12px', color: 'rgba(148, 163, 184, 0.35)', marginBottom: '16px' }}>
            All inference and indexing routes operate locally. No public cloud APIs are mapped.
          </p>
          <table style={{ width: '100%', borderCollapse: 'collapse' as const }}>
            <thead>
              <tr style={{ borderBottom: '1px solid rgba(148, 163, 184, 0.06)' }}>
                {['Method', 'Endpoint', 'Description'].map((h) => (
                  <th key={h} style={{ padding: '0 0 10px', textAlign: 'left' as const, fontSize: '9px', fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase' as const, color: 'rgba(148, 163, 184, 0.3)', fontFamily: "'JetBrains Mono', monospace" }}>
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {routes.map((route, idx) => (
                <tr
                  key={idx}
                  style={{
                    borderBottom: idx < routes.length - 1 ? '1px solid rgba(148, 163, 184, 0.04)' : 'none',
                    transition: 'background 0.15s ease',
                  }}
                  onMouseEnter={(e) => { (e.currentTarget as HTMLTableRowElement).style.background = 'rgba(148, 163, 184, 0.02)'; }}
                  onMouseLeave={(e) => { (e.currentTarget as HTMLTableRowElement).style.background = 'transparent'; }}
                >
                  <td style={{ padding: '12px 0', width: '80px' }}>
                    <span style={{
                      padding: '2px 8px',
                      borderRadius: '4px',
                      fontSize: '9px',
                      fontWeight: 700,
                      letterSpacing: '0.08em',
                      fontFamily: "'JetBrains Mono', monospace",
                      background: route.method === 'GET' ? 'rgba(52, 211, 153, 0.08)' : 'rgba(99, 102, 241, 0.08)',
                      border: route.method === 'GET' ? '1px solid rgba(52, 211, 153, 0.15)' : '1px solid rgba(99, 102, 241, 0.15)',
                      color: route.method === 'GET' ? '#34d399' : '#818cf8',
                    }}>
                      {route.method}
                    </span>
                  </td>
                  <td style={{ padding: '12px 16px 12px 0', fontFamily: "'JetBrains Mono', monospace", fontSize: '12px', color: 'rgba(226, 232, 240, 0.7)' }}>
                    {route.path}
                  </td>
                  <td style={{ padding: '12px 0', fontSize: '12px', color: 'rgba(148, 163, 184, 0.4)' }}>
                    {route.desc}
                  </td>
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
