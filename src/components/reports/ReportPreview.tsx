import React, { forwardRef } from 'react';
import { ReportRecord } from '../../types/reports';

interface ReportPreviewProps {
  report: ReportRecord;
}

/**
 * The styled report document.
 * This component is rendered in the DOM (inside the modal preview AND offscreen
 * when capturing for PDF/PNG).  It is intentionally written with inline styles
 * so that html2canvas can reliably capture it without Tailwind class resolution.
 */
export const ReportPreview = forwardRef<HTMLDivElement, ReportPreviewProps>(
  ({ report }, ref) => {
    const generatedDate = new Date(report.generatedAt).toLocaleDateString('en-GB', {
      day: '2-digit',
      month: 'long',
      year: 'numeric',
    });
    const generatedTime = new Date(report.generatedAt).toLocaleTimeString('en-GB', {
      hour: '2-digit',
      minute: '2-digit',
    });

    // ---- Parse the AI content into sections ----
    const lines = report.messageContent
      .split('\n')
      .map((l) => l.trim())
      .filter(Boolean);

    // Try to identify bullet points vs. paragraphs
    const bullets: string[] = [];
    const paragraphs: string[] = [];

    lines.forEach((line) => {
      if (/^[-•*]\s/.test(line) || /^\d+\.\s/.test(line)) {
        bullets.push(line.replace(/^[-•*\d.]\s+/, '').trim());
      } else {
        paragraphs.push(line);
      }
    });

    // Build "key findings" from bullets (or first sentences if no bullets)
    const findings =
      bullets.length > 0
        ? bullets
        : paragraphs
            .flatMap((p) => p.split(/\.\s+/))
            .filter((s) => s.length > 20)
            .slice(0, 5)
            .map((s) => (s.endsWith('.') ? s : s + '.'));

    // The full narrative goes into observations
    // (Used in paragraphs mapping below)

    return (
      <div
        ref={ref}
        id="report-preview-root"
        style={{
          fontFamily: "'Inter', 'Segoe UI', system-ui, sans-serif",
          background: '#ffffff',
          color: '#1a1a2e',
          width: '794px',         // A4 width at 96dpi
          minWidth: '794px',
          maxWidth: '794px',
          padding: '0',
          boxSizing: 'border-box',
        }}
      >
        {/* ===== HEADER BANNER ===== */}
        <div
          style={{
            background: 'linear-gradient(135deg, #1e1b4b 0%, #312e81 60%, #4338ca 100%)',
            padding: '36px 48px 28px',
            position: 'relative',
            overflow: 'hidden',
          }}
        >
          {/* decorative grid lines */}
          <div style={{
            position: 'absolute', inset: 0,
            backgroundImage: 'linear-gradient(rgba(255,255,255,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.04) 1px, transparent 1px)',
            backgroundSize: '24px 24px',
            pointerEvents: 'none',
          }} />

          <div style={{ position: 'relative' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
              <div style={{
                width: '36px', height: '36px', borderRadius: '8px',
                background: 'rgba(255,255,255,0.15)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                border: '1px solid rgba(255,255,255,0.2)',
              }}>
                <span style={{ color: '#fff', fontSize: '18px', lineHeight: 1 }}>⬡</span>
              </div>
              <div>
                <div style={{ color: '#c7d2fe', fontSize: '9px', fontWeight: 700, letterSpacing: '0.14em', textTransform: 'uppercase' }}>
                  SOVEREIGN AI
                </div>
                <div style={{ color: 'rgba(199,210,254,0.6)', fontSize: '8px', letterSpacing: '0.08em' }}>
                  Enterprise Intelligence Platform · On-Premise
                </div>
              </div>
            </div>

            <h1 style={{
              color: '#ffffff',
              fontSize: '22px',
              fontWeight: 800,
              letterSpacing: '-0.02em',
              margin: 0,
              lineHeight: 1.25,
            }}>
              {report.title}
            </h1>
            <div style={{ color: '#a5b4fc', fontSize: '12px', marginTop: '6px' }}>
              {report.type}
            </div>
          </div>
        </div>

        {/* ===== META ROW ===== */}
        <div style={{
          display: 'flex',
          alignItems: 'stretch',
          borderBottom: '1px solid #e5e7eb',
          background: '#f8f9ff',
        }}>
          {[
            { label: 'Generated', value: generatedDate },
            { label: 'Time', value: generatedTime },
            { label: 'Analysis Basis', value: 'Document-Based Assessment' },
            { label: 'Sources Cited', value: report.sources.length > 0 ? `${report.sources.length} document${report.sources.length > 1 ? 's' : ''}` : 'No sources' },
          ].map((item, i) => (
            <div key={i} style={{
              flex: 1,
              padding: '14px 20px',
              borderRight: i < 3 ? '1px solid #e5e7eb' : 'none',
            }}>
              <div style={{ fontSize: '9px', color: '#9ca3af', textTransform: 'uppercase', letterSpacing: '0.08em', fontWeight: 600, marginBottom: '4px' }}>
                {item.label}
              </div>
              <div style={{ fontSize: '12px', color: '#374151', fontWeight: 600 }}>
                {item.value}
              </div>
            </div>
          ))}
        </div>

        {/* ===== BODY ===== */}
        <div style={{ padding: '36px 48px' }}>

          {/* Executive Summary */}
          <Section title="Executive Summary" accent="#4338ca">
            <p style={{ fontSize: '13px', color: '#374151', lineHeight: 1.75, margin: 0 }}>
              {paragraphs[0] || report.messageContent.slice(0, 400)}
            </p>
          </Section>

          {/* Key Findings */}
          {findings.length > 0 && (
            <Section title="Key Findings" accent="#4338ca">
              <ul style={{ margin: 0, padding: 0, listStyle: 'none' }}>
                {findings.slice(0, 8).map((f, i) => (
                  <li key={i} style={{
                    display: 'flex', alignItems: 'flex-start', gap: '10px',
                    marginBottom: '10px', fontSize: '13px', color: '#374151', lineHeight: 1.65,
                  }}>
                    <span style={{
                      flexShrink: 0, width: '20px', height: '20px', borderRadius: '50%',
                      background: '#eef2ff', color: '#4338ca', fontSize: '10px', fontWeight: 700,
                      display: 'flex', alignItems: 'center', justifyContent: 'center', marginTop: '1px',
                    }}>
                      {i + 1}
                    </span>
                    <span>{f}</span>
                  </li>
                ))}
              </ul>
            </Section>
          )}

          {/* Observations */}
          {paragraphs.length > 1 && (
            <Section title="Observations & Analysis" accent="#4338ca">
              {paragraphs.slice(1).map((p, i) => (
                <p key={i} style={{ fontSize: '13px', color: '#374151', lineHeight: 1.75, margin: '0 0 10px 0' }}>
                  {p}
                </p>
              ))}
            </Section>
          )}

          {/* Evidence & Sources */}
          {report.sources.length > 0 && (
            <Section title="Evidence & Sources" accent="#4338ca">
              <div style={{
                background: '#f8f9ff',
                border: '1px solid #e0e7ff',
                borderRadius: '8px',
                overflow: 'hidden',
              }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ background: '#eef2ff' }}>
                      <th style={{ padding: '10px 16px', textAlign: 'left', fontSize: '9px', fontWeight: 700, color: '#4338ca', textTransform: 'uppercase', letterSpacing: '0.08em', width: '40px' }}>#</th>
                      <th style={{ padding: '10px 16px', textAlign: 'left', fontSize: '9px', fontWeight: 700, color: '#4338ca', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Source Document</th>
                      <th style={{ padding: '10px 16px', textAlign: 'left', fontSize: '9px', fontWeight: 700, color: '#4338ca', textTransform: 'uppercase', letterSpacing: '0.08em', width: '100px' }}>Reference</th>
                    </tr>
                  </thead>
                  <tbody>
                    {report.sources.map((src, i) => (
                      <tr key={i} style={{ borderTop: '1px solid #e0e7ff', background: i % 2 === 0 ? '#fff' : '#f8f9ff' }}>
                        <td style={{ padding: '10px 16px', fontSize: '12px', color: '#9ca3af', fontWeight: 600 }}>{i + 1}</td>
                        <td style={{ padding: '10px 16px', fontSize: '12px', color: '#374151', fontWeight: 500 }}>{src.document}</td>
                        <td style={{ padding: '10px 16px', fontSize: '11px', color: '#6366f1', fontFamily: 'monospace' }}>Page {src.page}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Section>
          )}

          {/* Assessment Scope */}
          <div style={{
            marginTop: '28px',
            padding: '16px 20px',
            borderRadius: '8px',
            background: '#fffbeb',
            border: '1px solid #fde68a',
          }}>
            <div style={{ fontSize: '9px', fontWeight: 700, color: '#92400e', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '6px' }}>
              Assessment Scope &amp; Disclaimer
            </div>
            <p style={{ fontSize: '11px', color: '#78350f', lineHeight: 1.65, margin: 0 }}>
              This assessment is generated from available organisational documents and knowledge base records.
              It does not represent real-time equipment sensor health unless live sensor data was explicitly included
              in the source documents. All findings are derived from Document-Based Assessment only.
              Verify critical operational decisions against physical inspection records.
            </p>
          </div>
        </div>

        {/* ===== FOOTER ===== */}
        <div style={{
          borderTop: '1px solid #e5e7eb',
          padding: '14px 48px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          background: '#f9fafb',
        }}>
          <span style={{ fontSize: '10px', color: '#9ca3af' }}>
            Sovereign AI · Enterprise Intelligence Platform · On-Premise Enclave
          </span>
          <span style={{ fontSize: '10px', color: '#9ca3af' }}>
            Generated {generatedDate} at {generatedTime}
          </span>
        </div>
      </div>
    );
  }
);

ReportPreview.displayName = 'ReportPreview';
export default ReportPreview;

// ---- Helper sub-component ----
interface SectionProps {
  title: string;
  accent: string;
  children: React.ReactNode;
}

const Section: React.FC<SectionProps> = ({ title, accent, children }) => (
  <div style={{ marginBottom: '28px' }}>
    <div style={{
      display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '14px',
    }}>
      <div style={{ width: '3px', height: '18px', background: accent, borderRadius: '2px', flexShrink: 0 }} />
      <h2 style={{ fontSize: '13px', fontWeight: 700, color: '#1e1b4b', margin: 0, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
        {title}
      </h2>
    </div>
    {children}
  </div>
);
