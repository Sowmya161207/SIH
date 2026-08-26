import React, { useState } from 'react';
import { ReportRecord } from '../types/reports';
import { ReportModal } from '../components/reports/ReportModal';
import { FileText, Trash2, Eye, ClipboardList } from 'lucide-react';

interface ReportsProps {
  history: ReportRecord[];
  onRemove: (id: string) => void;
  onClearAll: () => void;
}

export const Reports: React.FC<ReportsProps> = ({ history, onRemove, onClearAll }) => {
  const [activeReport, setActiveReport] = useState<ReportRecord | null>(null);

  const formatDate = (iso: string) =>
    new Date(iso).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });

  const formatTime = (iso: string) =>
    new Date(iso).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });

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
        <div className="relative flex items-start justify-between">
          <div>
            <h1 style={{ fontSize: '22px', fontWeight: 800, color: '#f1f5f9', letterSpacing: '-0.025em' }}>
              Report History
            </h1>
            <p className="mt-1.5" style={{ fontSize: '13px', color: 'rgba(148, 163, 184, 0.5)' }}>
              Previously generated AI analysis reports — download or re-open at any time.
            </p>
          </div>
          {history.length > 0 && (
            <button
              onClick={onClearAll}
              style={{
                padding: '7px 14px', borderRadius: '8px',
                background: 'transparent',
                border: '1px solid rgba(148, 163, 184, 0.08)',
                color: 'rgba(148, 163, 184, 0.4)',
                fontSize: '12px', fontWeight: 500, cursor: 'pointer',
                transition: 'all 0.15s ease',
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLButtonElement).style.color = '#fb7185';
                (e.currentTarget as HTMLButtonElement).style.borderColor = 'rgba(244,63,94,0.2)';
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLButtonElement).style.color = 'rgba(148, 163, 184, 0.4)';
                (e.currentTarget as HTMLButtonElement).style.borderColor = 'rgba(148, 163, 184, 0.08)';
              }}
            >
              Clear All
            </button>
          )}
        </div>
      </div>

      <div style={{ padding: '32px 48px', maxWidth: '1280px' }}>
        {history.length === 0 ? (
          /* Empty state */
          <div
            className="flex flex-col items-center justify-center text-center"
            style={{
              minHeight: '280px',
              borderRadius: '12px',
              border: '1px dashed rgba(148, 163, 184, 0.08)',
              background: 'rgba(10, 15, 26, 0.3)',
              padding: '48px 24px',
            }}
          >
            <div
              className="h-14 w-14 rounded-2xl flex items-center justify-center mb-4"
              style={{ background: 'rgba(148, 163, 184, 0.04)', border: '1px solid rgba(148, 163, 184, 0.06)' }}
            >
              <ClipboardList className="h-6 w-6" style={{ color: 'rgba(148, 163, 184, 0.2)' }} />
            </div>
            <p className="font-semibold text-sm" style={{ color: 'rgba(148, 163, 184, 0.4)' }}>
              No reports generated yet
            </p>
            <p className="text-xs mt-2 max-w-xs" style={{ color: 'rgba(148, 163, 184, 0.25)', lineHeight: 1.6 }}>
              Go to the AI Assistant, ask a question about your documents, then click{' '}
              <span style={{ color: 'rgba(99, 102, 241, 0.6)' }}>Generate Report</span> on any AI response.
            </p>
          </div>
        ) : (
          <div
            style={{
              background: '#0f172a',
              border: '1px solid rgba(148, 163, 184, 0.08)',
              borderRadius: '12px',
              overflow: 'hidden',
            }}
          >
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid rgba(148, 163, 184, 0.07)', background: 'rgba(10, 15, 26, 0.6)' }}>
                  {['Report Title', 'Type', 'Sources', 'Generated', 'Actions'].map((h, i) => (
                    <th
                      key={h}
                      style={{
                        padding: '12px 16px',
                        textAlign: i < 4 ? 'left' : 'right',
                        fontSize: '9px', fontWeight: 700,
                        letterSpacing: '0.1em', textTransform: 'uppercase',
                        color: 'rgba(148, 163, 184, 0.35)',
                        fontFamily: "'JetBrains Mono', monospace",
                      }}
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {history.map((record, idx) => (
                  <tr
                    key={record.id}
                    style={{
                      borderBottom: idx < history.length - 1 ? '1px solid rgba(148, 163, 184, 0.04)' : 'none',
                      transition: 'background 0.15s ease',
                    }}
                    onMouseEnter={(e) => { (e.currentTarget as HTMLTableRowElement).style.background = 'rgba(148, 163, 184, 0.02)'; }}
                    onMouseLeave={(e) => { (e.currentTarget as HTMLTableRowElement).style.background = 'transparent'; }}
                  >
                    {/* Title */}
                    <td style={{ padding: '14px 16px' }}>
                      <div className="flex items-center gap-3">
                        <div style={{
                          width: '28px', height: '28px', borderRadius: '6px', flexShrink: 0,
                          background: 'rgba(99,102,241,0.08)', border: '1px solid rgba(99,102,241,0.12)',
                          display: 'flex', alignItems: 'center', justifyContent: 'center',
                        }}>
                          <FileText className="h-3.5 w-3.5" style={{ color: '#818cf8' }} />
                        </div>
                        <span style={{ fontSize: '13px', fontWeight: 600, color: '#e2e8f0', letterSpacing: '-0.01em' }}>
                          {record.title}
                        </span>
                      </div>
                    </td>
                    {/* Type */}
                    <td style={{ padding: '14px 16px' }}>
                      <span style={{
                        padding: '2px 8px', borderRadius: '4px',
                        background: 'rgba(99,102,241,0.07)', border: '1px solid rgba(99,102,241,0.12)',
                        fontSize: '10px', fontWeight: 600, color: '#818cf8',
                        fontFamily: "'JetBrains Mono', monospace", letterSpacing: '0.04em',
                      }}>
                        {record.type}
                      </span>
                    </td>
                    {/* Sources */}
                    <td style={{ padding: '14px 16px' }}>
                      <span style={{ fontSize: '12px', color: 'rgba(148,163,184,0.5)', fontFamily: "'JetBrains Mono', monospace" }}>
                        {record.sources.length}
                      </span>
                    </td>
                    {/* Date */}
                    <td style={{ padding: '14px 16px' }}>
                      <div style={{ fontSize: '12px', color: 'rgba(148,163,184,0.6)', fontFamily: "'JetBrains Mono', monospace" }}>
                        {formatDate(record.generatedAt)}
                      </div>
                      <div style={{ fontSize: '10px', color: 'rgba(148,163,184,0.3)', fontFamily: "'JetBrains Mono', monospace", marginTop: '2px' }}>
                        {formatTime(record.generatedAt)}
                      </div>
                    </td>
                    {/* Actions */}
                    <td style={{ padding: '14px 16px', textAlign: 'right' }}>
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => setActiveReport(record)}
                          style={{
                            display: 'flex', alignItems: 'center', gap: '5px',
                            padding: '5px 10px', borderRadius: '6px',
                            background: 'rgba(99,102,241,0.08)', border: '1px solid rgba(99,102,241,0.15)',
                            color: '#818cf8', fontSize: '11px', fontWeight: 500,
                            cursor: 'pointer', transition: 'all 0.15s ease',
                          }}
                          onMouseEnter={(e) => { (e.currentTarget as HTMLButtonElement).style.background = 'rgba(99,102,241,0.15)'; }}
                          onMouseLeave={(e) => { (e.currentTarget as HTMLButtonElement).style.background = 'rgba(99,102,241,0.08)'; }}
                        >
                          <Eye className="h-3 w-3" />
                          <span>Open</span>
                        </button>
                        <button
                          onClick={() => onRemove(record.id)}
                          style={{
                            padding: '5px', borderRadius: '6px',
                            background: 'transparent', border: '1px solid transparent',
                            color: 'rgba(148,163,184,0.25)', cursor: 'pointer',
                            transition: 'all 0.15s ease',
                          }}
                          onMouseEnter={(e) => {
                            (e.currentTarget as HTMLButtonElement).style.color = '#fb7185';
                            (e.currentTarget as HTMLButtonElement).style.borderColor = 'rgba(244,63,94,0.15)';
                          }}
                          onMouseLeave={(e) => {
                            (e.currentTarget as HTMLButtonElement).style.color = 'rgba(148,163,184,0.25)';
                            (e.currentTarget as HTMLButtonElement).style.borderColor = 'transparent';
                          }}
                          title="Delete report"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal */}
      {activeReport && (
        <ReportModal report={activeReport} onClose={() => setActiveReport(null)} />
      )}
    </div>
  );
};

export default Reports;
