import React, { useState, useRef, useEffect } from 'react';
import { Send, FileText, Image as ImageIcon, Presentation, Type, File as FileIcon, Paperclip, X, Loader2 } from 'lucide-react';

interface ChatInputProps {
  onSend: (message: string, documentId?: string, attachedFilename?: string) => void;
  disabled: boolean;
  onUploadFile?: (file: File) => Promise<any>;
  isUploading?: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({ onSend, disabled, onUploadFile, isUploading }) => {
  const [text, setText] = useState('');
  const [showMenu, setShowMenu] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [acceptType, setAcceptType] = useState<string>('*/*');
  const [focused, setFocused] = useState(false);
  const [attachedFile, setAttachedFile] = useState<{ id: string; name: string } | null>(null);

  const handleSend = () => {
    if ((text.trim() || attachedFile) && !disabled) {
      const msgToSend = text.trim() || `Analyze the attached query file: ${attachedFile?.name}`;
      onSend(msgToSend, attachedFile?.id, attachedFile?.name);
      setText('');
      setAttachedFile(null);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleUploadClick = (accept: string) => {
    setAcceptType(accept);
    setShowMenu(false);
    setTimeout(() => { fileInputRef.current?.click(); }, 0);
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && onUploadFile) {
      try {
        const res = await onUploadFile(file);
        if (res && res.document_id) {
          setAttachedFile({ id: res.document_id, name: res.filename || file.name });
        }
      } catch (err) { /* handled in hook */ }
    }
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;
    textarea.style.height = 'auto';
    textarea.style.height = `${Math.min(textarea.scrollHeight, 160)}px`;
  }, [text]);

  const canSend = (text.trim() || attachedFile) && !disabled;

  const uploadOptions = [
    { label: 'PDF Document', accept: '.pdf,application/pdf', icon: FileText, color: '#fb7185' },
    { label: 'Image', accept: 'image/png,image/jpeg,image/jpg', icon: ImageIcon, color: '#34d399' },
    { label: 'PowerPoint', accept: '.ppt,.pptx', icon: Presentation, color: '#fbbf24' },
    { label: 'Text File', accept: '.txt,text/plain', icon: Type, color: '#94a3b8' },
    { label: 'Word Document', accept: '.doc,.docx', icon: FileIcon, color: '#818cf8' },
  ];

  return (
    <div className="relative">
      {/* Hidden file input */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        accept={acceptType}
        className="hidden"
      />

      {/* Upload popover */}
      {showMenu && (
        <div
          className="absolute bottom-full left-0 mb-2 w-52 animate-fadeInFast overflow-hidden"
          style={{
            background: '#0f172a',
            border: '1px solid rgba(148, 163, 184, 0.1)',
            borderRadius: '10px',
            boxShadow: '0 16px 48px rgba(0,0,0,0.5)',
            zIndex: 50,
          }}
        >
          <div
            className="px-3 py-2"
            style={{ borderBottom: '1px solid rgba(148, 163, 184, 0.07)' }}
          >
            <span
              style={{
                fontSize: '9px',
                fontWeight: 700,
                letterSpacing: '0.12em',
                textTransform: 'uppercase',
                color: 'rgba(148, 163, 184, 0.4)',
                fontFamily: "'JetBrains Mono', monospace",
              }}
            >
              Add to Knowledge Base
            </span>
          </div>
          {uploadOptions.map(({ label, accept, icon: Icon, color }) => (
            <button
              key={label}
              onClick={() => handleUploadClick(accept)}
              className="w-full flex items-center gap-3 cursor-pointer"
              style={{
                padding: '9px 14px',
                background: 'transparent',
                transition: 'background 0.1s ease',
                border: 'none',
                color: 'rgba(148, 163, 184, 0.7)',
                fontSize: '12px',
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLButtonElement).style.background = 'rgba(148, 163, 184, 0.05)';
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLButtonElement).style.background = 'transparent';
              }}
            >
              <Icon className="h-3.5 w-3.5 flex-shrink-0" style={{ color }} />
              <span>{label}</span>
            </button>
          ))}
        </div>
      )}

      {/* Attached Document Pill */}
      {attachedFile && (
        <div
          className="mb-2 inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs animate-fadeIn"
          style={{
            background: 'rgba(99, 102, 241, 0.12)',
            border: '1px solid rgba(99, 102, 241, 0.25)',
            color: '#a5b4fc',
          }}
        >
          <FileText className="h-3.5 w-3.5 flex-shrink-0 text-indigo-400" />
          <span className="font-mono text-[11px] truncate max-w-[240px]">
            Attached context: <strong>{attachedFile.name}</strong>
          </span>
          <button
            onClick={() => setAttachedFile(null)}
            className="hover:text-rose-400 cursor-pointer ml-1 p-0.5 rounded"
            title="Remove attachment"
          >
            <X className="h-3 w-3" />
          </button>
        </div>
      )}

      {/* Input container */}
      <div
        style={{
          background: '#131c2e',
          border: `1px solid ${focused ? 'rgba(99, 102, 241, 0.3)' : 'rgba(148, 163, 184, 0.1)'}`,
          borderRadius: '12px',
          boxShadow: focused ? '0 0 0 3px rgba(99, 102, 241, 0.06)' : 'none',
          transition: 'all 0.15s ease',
          padding: '10px 12px',
          display: 'flex',
          alignItems: 'flex-end',
          gap: '8px',
        }}
      >
        {/* Attach button */}
        {onUploadFile && (
          <button
            onClick={() => setShowMenu(!showMenu)}
            disabled={disabled || isUploading}
            title="Add to knowledge base"
            className="flex-shrink-0 cursor-pointer"
            style={{
              padding: '6px',
              borderRadius: '7px',
              background: showMenu ? 'rgba(99, 102, 241, 0.1)' : 'transparent',
              border: '1px solid transparent',
              color: 'rgba(148, 163, 184, 0.4)',
              transition: 'all 0.15s ease',
              marginBottom: '1px',
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLButtonElement).style.background = 'rgba(148, 163, 184, 0.06)';
              (e.currentTarget as HTMLButtonElement).style.color = 'rgba(148, 163, 184, 0.7)';
            }}
            onMouseLeave={(e) => {
              if (!showMenu) {
                (e.currentTarget as HTMLButtonElement).style.background = 'transparent';
              }
              (e.currentTarget as HTMLButtonElement).style.color = 'rgba(148, 163, 184, 0.4)';
            }}
          >
            <Paperclip className="h-4 w-4" />
          </button>
        )}

        {/* Textarea */}
        <textarea
          ref={textareaRef}
          rows={1}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          placeholder={disabled ? 'Processing...' : 'Ask Sovereign AI about your documents...'}
          disabled={disabled}
          className="flex-1 bg-transparent resize-none scrollbar-none"
          style={{
            border: 'none',
            outline: 'none',
            color: '#e2e8f0',
            fontSize: '13.5px',
            lineHeight: 1.6,
            padding: '4px 0',
            maxHeight: '160px',
            minHeight: '28px',
            caretColor: '#818cf8',
          }}
        />

        {/* Send button */}
        <button
          onClick={handleSend}
          disabled={!canSend}
          className="flex-shrink-0 cursor-pointer"
          style={{
            padding: '7px',
            borderRadius: '8px',
            background: canSend
              ? 'linear-gradient(135deg, #6366f1 0%, #7c3aed 100%)'
              : 'rgba(148, 163, 184, 0.06)',
            border: 'none',
            color: canSend ? '#fff' : 'rgba(148, 163, 184, 0.2)',
            boxShadow: canSend ? '0 2px 12px rgba(99, 102, 241, 0.3)' : 'none',
            transition: 'all 0.15s ease',
            marginBottom: '1px',
          }}
          onMouseEnter={(e) => {
            if (canSend) {
              (e.currentTarget as HTMLButtonElement).style.boxShadow = '0 4px 16px rgba(99, 102, 241, 0.4)';
              (e.currentTarget as HTMLButtonElement).style.transform = 'translateY(-1px)';
            }
          }}
          onMouseLeave={(e) => {
            if (canSend) {
              (e.currentTarget as HTMLButtonElement).style.boxShadow = '0 2px 12px rgba(99, 102, 241, 0.3)';
              (e.currentTarget as HTMLButtonElement).style.transform = 'translateY(0)';
            }
          }}
        >
          <Send className="h-3.5 w-3.5" />
        </button>
      </div>

      {/* Hint */}
      <div
        className="text-center mt-2"
        style={{
          fontSize: '10px',
          color: 'rgba(148, 163, 184, 0.2)',
          fontFamily: "'JetBrains Mono', monospace",
        }}
      >
        Enter to send · Shift+Enter for new line
      </div>
    </div>
  );
};
export default ChatInput;
