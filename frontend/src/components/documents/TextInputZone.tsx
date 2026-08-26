import React, { useState } from 'react';
import { Type, AlertTriangle, CheckCircle2, Loader2 } from 'lucide-react';

interface TextInputZoneProps {
  onSubmitText: (title: string, content: string) => Promise<any>;
  isSubmitting: boolean;
  submitError: string | null;
  submitSuccess: boolean;
  clearSubmitState: () => void;
}

export const TextInputZone: React.FC<TextInputZoneProps> = ({
  onSubmitText,
  isSubmitting,
  submitError,
  submitSuccess,
  clearSubmitState,
}) => {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [validationError, setValidationError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError(null);
    clearSubmitState();
    if (!title.trim()) { setValidationError('Please enter a title.'); return; }
    if (!content.trim()) { setValidationError('Please enter the text content.'); return; }
    try {
      await onSubmitText(title, content);
      setTitle('');
      setContent('');
    } catch (e) { /* handled by hook */ }
  };

  const inputStyle = {
    width: '100%',
    background: 'rgba(10, 15, 26, 0.6)',
    border: '1px solid rgba(148, 163, 184, 0.08)',
    borderRadius: '8px',
    padding: '9px 12px',
    color: '#e2e8f0',
    fontSize: '13px',
    outline: 'none',
    transition: 'border-color 0.15s ease, box-shadow 0.15s ease',
    fontFamily: 'Inter, sans-serif',
  };

  return (
    <div
      style={{
        background: '#0f172a',
        border: '1px solid rgba(148, 163, 184, 0.08)',
        borderRadius: '12px',
        padding: '24px',
        display: 'flex',
        flexDirection: 'column' as const,
      }}
    >
      <div
        className="mb-4"
        style={{
          fontSize: '9px',
          fontWeight: 700,
          letterSpacing: '0.12em',
          textTransform: 'uppercase' as const,
          color: 'rgba(148, 163, 184, 0.4)',
          fontFamily: "'JetBrains Mono', monospace",
        }}
      >
        Direct Text Input
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col flex-1 space-y-3">
        <div>
          <label
            htmlFor="textTitle"
            style={{
              display: 'block',
              fontSize: '10px',
              fontWeight: 600,
              textTransform: 'uppercase' as const,
              letterSpacing: '0.08em',
              color: 'rgba(148, 163, 184, 0.4)',
              marginBottom: '6px',
              fontFamily: "'JetBrains Mono', monospace",
            }}
          >
            Title
          </label>
          <input
            type="text"
            id="textTitle"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g. Safety Procedures - Section 3"
            style={inputStyle}
            disabled={isSubmitting}
            onFocus={(e) => {
              (e.target as HTMLInputElement).style.borderColor = 'rgba(99, 102, 241, 0.3)';
              (e.target as HTMLInputElement).style.boxShadow = '0 0 0 3px rgba(99, 102, 241, 0.07)';
            }}
            onBlur={(e) => {
              (e.target as HTMLInputElement).style.borderColor = 'rgba(148, 163, 184, 0.08)';
              (e.target as HTMLInputElement).style.boxShadow = 'none';
            }}
          />
        </div>

        <div className="flex-1 flex flex-col">
          <label
            htmlFor="textContent"
            style={{
              display: 'block',
              fontSize: '10px',
              fontWeight: 600,
              textTransform: 'uppercase' as const,
              letterSpacing: '0.08em',
              color: 'rgba(148, 163, 184, 0.4)',
              marginBottom: '6px',
              fontFamily: "'JetBrains Mono', monospace",
            }}
          >
            Content
          </label>
          <textarea
            id="textContent"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Paste or type document content here..."
            style={{
              ...inputStyle,
              minHeight: '120px',
              resize: 'vertical' as const,
              lineHeight: 1.6,
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: '12px',
            }}
            disabled={isSubmitting}
            onFocus={(e) => {
              (e.target as HTMLTextAreaElement).style.borderColor = 'rgba(99, 102, 241, 0.3)';
              (e.target as HTMLTextAreaElement).style.boxShadow = '0 0 0 3px rgba(99, 102, 241, 0.07)';
            }}
            onBlur={(e) => {
              (e.target as HTMLTextAreaElement).style.borderColor = 'rgba(148, 163, 184, 0.08)';
              (e.target as HTMLTextAreaElement).style.boxShadow = 'none';
            }}
          />
        </div>

        {(validationError || submitError) && (
          <div
            className="flex items-start gap-2 animate-fadeIn"
            style={{
              padding: '10px 12px',
              borderRadius: '8px',
              background: 'rgba(244, 63, 94, 0.06)',
              border: '1px solid rgba(244, 63, 94, 0.12)',
            }}
          >
            <AlertTriangle className="h-3.5 w-3.5 flex-shrink-0 mt-0.5" style={{ color: '#fb7185' }} />
            <p className="text-xs" style={{ color: 'rgba(251, 113, 133, 0.8)' }}>{validationError || submitError}</p>
          </div>
        )}

        {submitSuccess && (
          <div
            className="flex items-start gap-2 animate-fadeIn"
            style={{
              padding: '10px 12px',
              borderRadius: '8px',
              background: 'rgba(16, 185, 129, 0.06)',
              border: '1px solid rgba(16, 185, 129, 0.12)',
            }}
          >
            <CheckCircle2 className="h-3.5 w-3.5 flex-shrink-0 mt-0.5" style={{ color: '#34d399' }} />
            <p className="text-xs" style={{ color: 'rgba(52, 211, 153, 0.8)' }}>Text indexed successfully.</p>
          </div>
        )}

        <div className="flex justify-end pt-1">
          <button
            type="submit"
            disabled={!title.trim() || !content.trim() || isSubmitting}
            className="cursor-pointer flex items-center gap-1.5"
            style={{
              padding: '7px 16px',
              borderRadius: '7px',
              background: 'linear-gradient(135deg, #6366f1 0%, #7c3aed 100%)',
              border: 'none',
              color: '#fff',
              fontSize: '12px',
              fontWeight: 600,
              boxShadow: '0 2px 12px rgba(99, 102, 241, 0.25)',
              opacity: (!title.trim() || !content.trim() || isSubmitting) ? 0.5 : 1,
              transition: 'opacity 0.15s ease',
            }}
          >
            {isSubmitting ? (
              <><Loader2 className="h-3.5 w-3.5 animate-spin" /><span>Processing...</span></>
            ) : (
              <><Type className="h-3.5 w-3.5" /><span>Add to Knowledge</span></>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
export default TextInputZone;
