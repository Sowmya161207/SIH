import React from 'react';
import { DocumentStatus as StatusType } from '../../types/documents';
import { CheckCircle2, AlertCircle, Loader2, FileUp } from 'lucide-react';

interface DocumentStatusProps {
  status: StatusType;
}

export const DocumentStatus: React.FC<DocumentStatusProps> = ({ status }) => {
  const config: Record<string, { label: string; color: string; bg: string; border: string; icon: any; spin: boolean }> = {
    uploaded: {
      label: 'Uploaded',
      color: '#60a5fa',
      bg: 'rgba(96, 165, 250, 0.08)',
      border: 'rgba(96, 165, 250, 0.15)',
      icon: FileUp,
      spin: false,
    },
    processing: {
      label: 'Processing',
      color: '#fbbf24',
      bg: 'rgba(251, 191, 36, 0.08)',
      border: 'rgba(251, 191, 36, 0.15)',
      icon: Loader2,
      spin: true,
    },
    completed: {
      label: 'Ready',
      color: '#34d399',
      bg: 'rgba(52, 211, 153, 0.08)',
      border: 'rgba(52, 211, 153, 0.15)',
      icon: CheckCircle2,
      spin: false,
    },
    ready: {
      label: 'Ready',
      color: '#34d399',
      bg: 'rgba(52, 211, 153, 0.08)',
      border: 'rgba(52, 211, 153, 0.15)',
      icon: CheckCircle2,
      spin: false,
    },
    failed: {
      label: 'Failed',
      color: '#fb7185',
      bg: 'rgba(251, 113, 133, 0.08)',
      border: 'rgba(251, 113, 133, 0.15)',
      icon: AlertCircle,
      spin: false,
    },
  };

  const current = config[status] || config.uploaded;
  const Icon = current.icon;

  return (
    <span
      className="inline-flex items-center gap-1"
      style={{
        padding: '2px 8px',
        borderRadius: '4px',
        background: current.bg,
        border: `1px solid ${current.border}`,
        fontSize: '9px',
        fontWeight: 700,
        letterSpacing: '0.08em',
        textTransform: 'uppercase',
        color: current.color,
        fontFamily: "'JetBrains Mono', monospace",
      }}
    >
      <Icon className={`h-2.5 w-2.5 ${current.spin ? 'animate-spin' : ''}`} />
      {current.label}
    </span>
  );
};
export default DocumentStatus;
