import React from 'react';
import { Message } from '../../types/chat';
import SourceList from './SourceList';
import { User, Bot } from 'lucide-react';

interface MessageBubbleProps {
  message: Message;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.role === 'user';

  const formatTime = (isoString: string) => {
    try {
      const date = new Date(isoString);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
      return '';
    }
  };

  return (
    <div className={`flex w-full space-x-3 my-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {/* Icon/Avatar for AI */}
      {!isUser && (
        <div className="h-8 w-8 rounded-full bg-indigo-950 border border-indigo-500/20 flex items-center justify-center flex-shrink-0 text-indigo-400">
          <Bot className="h-4 w-4" />
        </div>
      )}

      {/* Message Container */}
      <div
        className={`max-w-[75%] rounded-2xl p-4 shadow-sm flex flex-col justify-between ${
          isUser
            ? 'bg-indigo-600 border border-indigo-500 rounded-tr-none text-white'
            : 'bg-[#0f172a] border border-[#1e293b] rounded-tl-none text-slate-100'
        }`}
      >
        <div className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</div>

        {/* Sources list if present */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <SourceList sources={message.sources} />
        )}

        <span
          className={`text-[9px] font-mono mt-2 self-end ${
            isUser ? 'text-indigo-200/80' : 'text-slate-500'
          }`}
        >
          {formatTime(message.timestamp)}
        </span>
      </div>

      {/* Icon/Avatar for User */}
      {isUser && (
        <div className="h-8 w-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center flex-shrink-0 text-slate-300">
          <User className="h-4 w-4" />
        </div>
      )}
    </div>
  );
};
export default MessageBubble;
