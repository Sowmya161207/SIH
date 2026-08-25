import React from 'react';
import { History, Search, Download } from 'lucide-react';

export const AuditLogs: React.FC = () => {
  return (
    <div className="min-h-full animate-fadeIn flex flex-col">
      {/* Page header */}
      <div
        className="relative overflow-hidden flex-shrink-0"
        style={{
          background: 'linear-gradient(180deg, #0a0f1a 0%, #080c15 100%)',
          borderBottom: '1px solid rgba(148, 163, 184, 0.06)',
          padding: '32px 48px 28px',
        }}
      >
        <div className="absolute inset-0 bg-grid opacity-40" style={{ pointerEvents: 'none' }} />
        <div className="relative flex items-start justify-between">
          <div>
            <h1 style={{ fontSize: '22px', fontWeight: 800, color: '#f1f5f9', letterSpacing: '-0.025em' }}>
              Audit Logs
            </h1>
            <p className="mt-1.5" style={{ fontSize: '13px', color: 'rgba(148, 163, 184, 0.5)' }}>
              Monitor activity across the Sovereign AI Workbench
            </p>
          </div>
          
          {/* Action buttons (Disabled visually as there's no data) */}
          <div className="flex items-center gap-3">
            <div
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg"
              style={{
                background: 'rgba(6, 8, 16, 0.5)',
                border: '1px solid rgba(148, 163, 184, 0.08)',
              }}
            >
              <Search className="h-3.5 w-3.5" style={{ color: 'rgba(148, 163, 184, 0.3)' }} />
              <span style={{ fontSize: '12px', color: 'rgba(148, 163, 184, 0.3)' }}>Search...</span>
            </div>
            <button
              disabled
              style={{
                display: 'flex', alignItems: 'center', gap: '6px',
                padding: '6px 12px', borderRadius: '8px',
                background: 'transparent',
                border: '1px solid rgba(148, 163, 184, 0.08)',
                color: 'rgba(148, 163, 184, 0.3)',
                fontSize: '12px', fontWeight: 500, cursor: 'not-allowed',
              }}
            >
              <Download className="h-3.5 w-3.5" />
              <span>Export CSV</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div style={{ padding: '32px 48px', maxWidth: '1280px', flex: 1, display: 'flex', flexDirection: 'column' }}>
        
        {/* Table structure frame */}
        <div
          className="flex flex-col flex-1"
          style={{
            background: '#0f172a',
            border: '1px solid rgba(148, 163, 184, 0.08)',
            borderRadius: '12px',
            overflow: 'hidden',
          }}
        >
          {/* Table Header Row (mock) */}
          <div
            className="flex items-center"
            style={{
              borderBottom: '1px solid rgba(148, 163, 184, 0.07)',
              background: 'rgba(10, 15, 26, 0.6)',
            }}
          >
            {['Time', 'User', 'Role', 'Action', 'Resource', 'Status'].map((h, i) => (
              <div
                key={h}
                style={{
                  flex: i === 3 ? 2 : 1, // Make Action column wider
                  padding: '12px 16px',
                  fontSize: '9px', fontWeight: 700,
                  letterSpacing: '0.1em', textTransform: 'uppercase',
                  color: 'rgba(148, 163, 184, 0.35)',
                  fontFamily: "'JetBrains Mono', monospace",
                }}
              >
                {h}
              </div>
            ))}
          </div>

          {/* Empty State */}
          <div className="flex-1 flex flex-col items-center justify-center py-24">
            <div
              className="h-14 w-14 rounded-2xl flex items-center justify-center mb-4"
              style={{ background: 'rgba(148, 163, 184, 0.04)', border: '1px solid rgba(148, 163, 184, 0.06)' }}
            >
              <History className="h-6 w-6" style={{ color: 'rgba(148, 163, 184, 0.2)' }} />
            </div>
            <p className="font-semibold text-sm" style={{ color: 'rgba(148, 163, 184, 0.4)' }}>
              No audit activity available yet
            </p>
            <p className="text-xs mt-2 max-w-sm text-center" style={{ color: 'rgba(148, 163, 184, 0.25)', lineHeight: 1.6 }}>
              Audit activity will appear here when available. All system events, access requests, and configuration changes are tracked automatically.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuditLogs;
