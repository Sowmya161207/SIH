import React, { useState, useRef, useEffect } from 'react';
import { Send, CornerDownLeft } from 'lucide-react';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({ onSend, disabled }) => {
  const [text, setText] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

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

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    textarea.style.height = 'auto';
    textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
  }, [text]);

  return (
    <div className="relative border border-[#1e293b] rounded-xl bg-[#090d16] p-2 flex items-end">
      <textarea
        ref={textareaRef}
        rows={1}
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={disabled ? "Please wait..." : "Ask Sovereign AI Assistant about your documents..."}
        disabled={disabled}
        className="flex-1 bg-transparent text-slate-200 text-sm border-0 focus:ring-0 focus:outline-none resize-none px-3 py-2.5 max-h-[200px] min-h-[40px] pr-12 scrollbar-none"
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
