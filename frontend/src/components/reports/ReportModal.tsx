import React, { useRef, useState, useEffect } from 'react';
import { ReportRecord } from '../../types/reports';
import ReportPreview from './ReportPreview';
import { X, Download, Image as ImageIcon, Loader2, AlertTriangle, CheckCircle2 } from 'lucide-react';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

interface ReportModalProps {
  report: ReportRecord;
  onClose: () => void;
}

type DownloadState = 'idle' | 'loading' | 'success' | 'error';

const sanitizeFilename = (title: string): string =>
  title
    .replace(/[^a-zA-Z0-9\s-]/g, '')
    .replace(/\s+/g, '_')
    .slice(0, 60);

export const ReportModal: React.FC<ReportModalProps> = ({ report, onClose }) => {
  const previewRef = useRef<HTMLDivElement>(null);
  const [pdfState, setPdfState] = useState<DownloadState>('idle');
  const [pngState, setPngState] = useState<DownloadState>('idle');
  const [pdfMsg, setPdfMsg] = useState('');
  const [pngMsg, setPngMsg] = useState('');

  const dateStr = new Date(report.generatedAt).toISOString().slice(0, 10).replace(/-/g, '-');
  const baseFilename = `${sanitizeFilename(report.title)}_${dateStr}`;

  // Capture the hidden off-screen preview div (full quality)
  const captureCanvas = async (): Promise<HTMLCanvasElement> => {
    const el = document.getElementById('report-capture-target');
    if (!el) throw new Error('Capture target not found');
    return html2canvas(el, {
      scale: 2,
      useCORS: true,
      backgroundColor: '#ffffff',
      logging: false,
      windowWidth: 794,
    });
  };

  const downloadPDF = async () => {
    setPdfState('loading');
    setPdfMsg('Generating PDF...');
    try {
      const canvas = await captureCanvas();
      const imgData = canvas.toDataURL('image/jpeg', 0.95);

      // A4 at 72dpi: 595.28 x 841.89 pt
      const pdfW = 595.28;
      const pxPerPt = canvas.width / 794; // canvas is 794*2=1588 wide
      const pdfH = (canvas.height / pxPerPt) * (pdfW / 794);

      const pdf = new jsPDF({
        orientation: pdfH > pdfW ? 'portrait' : 'landscape',
        unit: 'pt',
        format: [pdfW, Math.max(pdfH, 841.89)],
      });

      // If report is very long, split into A4 pages
      const pageHeight = 841.89;
      const totalPages = Math.ceil(pdfH / pageHeight);

      for (let page = 0; page < totalPages; page++) {
        if (page > 0) pdf.addPage([pdfW, pageHeight]);
        pdf.addImage(
          imgData,
          'JPEG',
          0,
          -page * pageHeight,
          pdfW,
          pdfH,
          undefined,
          'FAST'
        );
        // Page number
        pdf.setFontSize(8);
        pdf.setTextColor(156, 163, 175);
        pdf.text(`Page ${page + 1} of ${totalPages}`, pdfW - 60, pageHeight - 12);
      }

      pdf.save(`${baseFilename}.pdf`);
      setPdfState('success');
      setPdfMsg('Downloaded!');
      setTimeout(() => setPdfState('idle'), 3000);
    } catch (e) {
      console.error(e);
      setPdfState('error');
      setPdfMsg('Failed to generate PDF.');
      setTimeout(() => setPdfState('idle'), 4000);
    }
  };

  const downloadPNG = async () => {
    setPngState('loading');
    setPngMsg('Generating image...');
    try {
      const canvas = await captureCanvas();
      const link = document.createElement('a');
      link.download = `${baseFilename}.png`;
      link.href = canvas.toDataURL('image/png');
      link.click();
      setPngState('success');
      setPngMsg('Downloaded!');
      setTimeout(() => setPngState('idle'), 3000);
    } catch (e) {
      console.error(e);
      setPngState('error');
      setPngMsg('Failed to generate image.');
      setTimeout(() => setPngState('idle'), 4000);
    }
  };

  // Close on Escape
  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [onClose]);

  const BtnIcon = (state: DownloadState) => {
    if (state === 'loading') return <Loader2 className="h-3.5 w-3.5 animate-spin" />;
    if (state === 'success') return <CheckCircle2 className="h-3.5 w-3.5" />;
    if (state === 'error') return <AlertTriangle className="h-3.5 w-3.5" />;
    return null;
  };

  return (
    <>
      {/* Backdrop */}
      <div
        onClick={onClose}
        style={{
          position: 'fixed', inset: 0,
          background: 'rgba(0,0,0,0.75)',
          backdropFilter: 'blur(4px)',
          zIndex: 1000,
        }}
      />

      {/* Modal */}
      <div
        style={{
          position: 'fixed',
          inset: '32px',
          zIndex: 1001,
          display: 'flex',
          flexDirection: 'column',
          background: '#0a0f1a',
          border: '1px solid rgba(148,163,184,0.1)',
          borderRadius: '16px',
          overflow: 'hidden',
          boxShadow: '0 32px 80px rgba(0,0,0,0.8)',
        }}
      >
        {/* Modal Header */}
        <div
          style={{
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
            padding: '16px 24px',
            borderBottom: '1px solid rgba(148,163,184,0.08)',
            background: '#080c15',
            flexShrink: 0,
          }}
        >
          <div>
            <div style={{ fontSize: '15px', fontWeight: 700, color: '#f1f5f9', letterSpacing: '-0.015em' }}>
              {report.title}
            </div>
            <div style={{
              fontSize: '10px', color: 'rgba(148,163,184,0.45)', marginTop: '3px',
              fontFamily: "'JetBrains Mono', monospace", letterSpacing: '0.04em',
            }}>
              {report.type} · {report.sources.length} source{report.sources.length !== 1 ? 's' : ''}
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            {/* PDF download — primary */}
            <button
              onClick={downloadPDF}
              disabled={pdfState === 'loading'}
              style={{
                display: 'flex', alignItems: 'center', gap: '6px',
                padding: '8px 16px',
                borderRadius: '8px',
                background: pdfState === 'success' ? 'linear-gradient(135deg,#059669,#047857)' :
                            pdfState === 'error'   ? 'rgba(244,63,94,0.15)' :
                            'linear-gradient(135deg,#6366f1,#7c3aed)',
                border: pdfState === 'error' ? '1px solid rgba(244,63,94,0.3)' : 'none',
                color: '#fff',
                fontSize: '12px', fontWeight: 600,
                cursor: pdfState === 'loading' ? 'not-allowed' : 'pointer',
                boxShadow: pdfState === 'idle' ? '0 2px 12px rgba(99,102,241,0.3)' : 'none',
                transition: 'all 0.15s ease',
                opacity: pdfState === 'loading' ? 0.8 : 1,
              }}
            >
              {BtnIcon(pdfState) || <Download className="h-3.5 w-3.5" />}
              <span>{pdfState === 'success' ? pdfMsg : pdfState === 'error' ? 'Retry PDF' : pdfState === 'loading' ? 'Generating...' : 'Download PDF'}</span>
            </button>

            {/* PNG — secondary */}
            <button
              onClick={downloadPNG}
              disabled={pngState === 'loading'}
              style={{
                display: 'flex', alignItems: 'center', gap: '6px',
                padding: '8px 14px',
                borderRadius: '8px',
                background: 'transparent',
                border: `1px solid ${pngState === 'success' ? 'rgba(16,185,129,0.3)' : pngState === 'error' ? 'rgba(244,63,94,0.3)' : 'rgba(148,163,184,0.12)'}`,
                color: pngState === 'success' ? '#34d399' : pngState === 'error' ? '#fb7185' : 'rgba(148,163,184,0.6)',
                fontSize: '12px', fontWeight: 500,
                cursor: pngState === 'loading' ? 'not-allowed' : 'pointer',
                transition: 'all 0.15s ease',
                opacity: pngState === 'loading' ? 0.8 : 1,
              }}
              onMouseEnter={(e) => {
                if (pngState === 'idle') {
                  (e.currentTarget as HTMLButtonElement).style.borderColor = 'rgba(148,163,184,0.25)';
                  (e.currentTarget as HTMLButtonElement).style.color = 'rgba(148,163,184,0.85)';
                }
              }}
              onMouseLeave={(e) => {
                if (pngState === 'idle') {
                  (e.currentTarget as HTMLButtonElement).style.borderColor = 'rgba(148,163,184,0.12)';
                  (e.currentTarget as HTMLButtonElement).style.color = 'rgba(148,163,184,0.6)';
                }
              }}
            >
              {BtnIcon(pngState) || <ImageIcon className="h-3.5 w-3.5" />}
              <span>{pngState === 'success' ? pngMsg : pngState === 'error' ? 'Retry PNG' : pngState === 'loading' ? 'Generating...' : 'Download PNG'}</span>
            </button>

            {/* Close */}
            <button
              onClick={onClose}
              style={{
                padding: '8px', borderRadius: '8px',
                background: 'transparent', border: '1px solid rgba(148,163,184,0.08)',
                color: 'rgba(148,163,184,0.4)', cursor: 'pointer',
                transition: 'all 0.15s ease',
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLButtonElement).style.color = '#fb7185';
                (e.currentTarget as HTMLButtonElement).style.borderColor = 'rgba(244,63,94,0.2)';
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLButtonElement).style.color = 'rgba(148,163,184,0.4)';
                (e.currentTarget as HTMLButtonElement).style.borderColor = 'rgba(148,163,184,0.08)';
              }}
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Preview area */}
        <div
          style={{
            flex: 1, overflowY: 'auto', overflowX: 'auto',
            padding: '24px',
            background: '#0d1420',
          }}
        >
          {/* Visual wrapper to make it look "floating" */}
          <div style={{ display: 'flex', justifyContent: 'center' }}>
            <div
              style={{
                boxShadow: '0 8px 48px rgba(0,0,0,0.5)',
                borderRadius: '4px',
                overflow: 'hidden',
              }}
            >
              <ReportPreview ref={previewRef} report={report} />
            </div>
          </div>
        </div>
      </div>

      {/* Off-screen capture target (same content, not in scrollable area) */}
      <div
        style={{
          position: 'fixed',
          top: '-99999px',
          left: '-99999px',
          pointerEvents: 'none',
          zIndex: -1,
        }}
      >
        <div id="report-capture-target">
          <ReportPreview report={report} />
        </div>
      </div>
    </>
  );
};

export default ReportModal;
