import React, { useState, useRef, useEffect } from 'react';
import { Send, CornerDownLeft, Plus, FileText, Image as ImageIcon, Presentation, Type, File as FileIcon } from 'lucide-react';

interface ChatInputProps {
  onSend: (message: string) => void;
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

  const handleSend = () => {
    if (text.trim() && !disabled) {
      onSend(text);
      setText('');
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
    setTimeout(() => {
      fileInputRef.current?.click();
    }, 0);
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && onUploadFile) {
      try {
        await onUploadFile(file);
      } catch (err) {
        // Error handled in useDocuments
      }
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    textarea.style.height = 'auto';
    textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
  }, [text]);

  return (
    <div className="relative border border-[#1e293b] rounded-xl bg-[#090d16] p-2 flex items-end">
      {/* Hidden file input */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        accept={acceptType}
        className="hidden"
      />

      {/* Attachment Button */}
      <div className="relative mr-2 mb-1.5 flex-shrink-0">
        <button
          onClick={() => setShowMenu(!showMenu)}
          disabled={disabled || isUploading}
          className="p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition-colors cursor-pointer"
          title="Add to knowledge base"
        >
          <Plus className="h-5 w-5" />
        </button>

        {/* Popover Menu */}
        {showMenu && (
          <div className="absolute bottom-full left-0 mb-2 w-56 bg-[#0f172a] border border-[#1e293b] rounded-xl shadow-xl overflow-hidden animate-fadeIn z-50">
            <div className="px-3 py-2 border-b border-[#1e293b]">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Add to knowledge base</span>
            </div>
            <div className="py-1">
              <button onClick={() => handleUploadClick('.pdf,application/pdf')} className="w-full flex items-center space-x-3 px-4 py-2 hover:bg-slate-800 transition-colors cursor-pointer">
                <FileText className="h-4 w-4 text-rose-400" />
                <span className="text-sm text-slate-300">PDF</span>
              </button>
              <button onClick={() => handleUploadClick('image/png,image/jpeg,image/jpg')} className="w-full flex items-center space-x-3 px-4 py-2 hover:bg-slate-800 transition-colors cursor-pointer">
                <ImageIcon className="h-4 w-4 text-emerald-400" />
                <span className="text-sm text-slate-300">Image</span>
              </button>
              <button onClick={() => handleUploadClick('.ppt,.pptx,application/vnd.ms-powerpoint,application/vnd.openxmlformats-officedocument.presentationml.presentation')} className="w-full flex items-center space-x-3 px-4 py-2 hover:bg-slate-800 transition-colors cursor-pointer">
                <Presentation className="h-4 w-4 text-amber-400" />
                <span className="text-sm text-slate-300">PowerPoint</span>
              </button>
              <button onClick={() => handleUploadClick('.txt,text/plain')} className="w-full flex items-center space-x-3 px-4 py-2 hover:bg-slate-800 transition-colors cursor-pointer">
                <Type className="h-4 w-4 text-slate-400" />
                <span className="text-sm text-slate-300">Text</span>
              </button>
              <button onClick={() => handleUploadClick('.doc,.docx,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document')} className="w-full flex items-center space-x-3 px-4 py-2 hover:bg-slate-800 transition-colors cursor-pointer">
                <FileIcon className="h-4 w-4 text-indigo-400" />
                <span className="text-sm text-slate-300">Word Document</span>
              </button>
            </div>
          </div>
        )}
      </div>

      <textarea
        ref={textareaRef}
        rows={1}
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={disabled ? "Please wait..." : "Ask Sovereign AI Assistant about your documents..."}
        disabled={disabled}
        className="flex-1 bg-transparent text-slate-200 text-sm border-0 focus:ring-0 focus:outline-none resize-none px-1 py-2.5 max-h-[200px] min-h-[40px] pr-12 scrollbar-none"
      />
      <div className="flex items-center space-x-2 mr-1 mb-1.5 flex-shrink-0">
        <span className="hidden sm:inline-flex items-center space-x-1 text-[10px] text-slate-500 font-mono select-none mr-2">
          <span>Enter</span>
          <CornerDownLeft className="h-2.5 w-2.5" />
        </span>
        <button
          onClick={handleSend}
          disabled={!text.trim() || disabled}
          className="p-2 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 disabled:text-slate-500 text-white rounded-lg transition-colors shadow-md shadow-indigo-600/10 cursor-pointer"
        >
          <Send className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
};
export default ChatInput;
