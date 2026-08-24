import React from 'react';
import { DocumentStatus as StatusType } from '../../types/documents';
import { CheckCircle2, AlertCircle, Loader2, FileUp } from 'lucide-react';

interface DocumentStatusProps {
  status: StatusType;
}

export const DocumentStatus: React.FC<DocumentStatusProps> = ({ status }) => {
  const config = {
    uploaded: {
      label: 'Uploading',
      className: 'bg-blue-500/10 text-blue-400 border border-blue-500/20',
      icon: FileUp,
      spin: false,
    },
    processing: {
      label: 'Processing',
      className: 'bg-amber-500/10 text-amber-400 border border-amber-500/20',
      icon: Loader2,
      spin: true,
    },
    completed: {
      label: 'Indexed',
      className: 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20',
      icon: CheckCircle2,
      spin: false,
    },
    failed: {
      label: 'Failed',
      className: 'bg-rose-500/10 text-rose-400 border border-rose-500/20',
      icon: AlertCircle,
      spin: false,
    },
  };

  const current = config[status] || config.uploaded;
  const Icon = current.icon;

  return (
    <span className={`inline-flex items-center space-x-1.5 px-2 py-0.5 rounded text-xs font-medium tracking-wide ${current.className}`}>
      <Icon className={`h-3 w-3 ${current.spin ? 'animate-spin' : ''}`} />
      <span>{current.label}</span>
    </span>
  );
};
export default DocumentStatus;
