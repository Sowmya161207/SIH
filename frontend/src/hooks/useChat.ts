import { useState, useEffect } from 'react';
import { Message, ChatRequest } from '../types/chat';
import { sendChatMessage } from '../services/api/chat';

export const useChat = () => {
  const [conversationId, setConversationId] = useState<string | null>(() => {
    return localStorage.getItem('sovereign_conversation_id');
  });

  const [messages, setMessages] = useState<Message[]>(() => {
    const saved = localStorage.getItem('sovereign_messages');
    return saved ? JSON.parse(saved) : [];
  });

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Sync conversation ID and messages to localStorage
  useEffect(() => {
    if (conversationId) {
      localStorage.setItem('sovereign_conversation_id', conversationId);
    } else {
      localStorage.removeItem('sovereign_conversation_id');
    }
  }, [conversationId]);

  useEffect(() => {
    localStorage.setItem('sovereign_messages', JSON.stringify(messages));
  }, [messages]);

  const sendMessage = async (content: string) => {
    if (!content.trim()) return;

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: content.trim(),
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    const request: ChatRequest = {
      message: userMessage.content,
      conversation_id: conversationId || undefined,
    };

    try {
      const response = await sendChatMessage(request);
      
      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: response.answer,
        timestamp: new Date().toISOString(),
        sources: response.sources || [],
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setConversationId(response.conversation_id);
      return response;
    } catch (err: any) {
      setError(err.message || 'Unable to process your request. Please try again.');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const clearConversation = () => {
    setMessages([]);
    setConversationId(null);
    setError(null);
    localStorage.removeItem('sovereign_conversation_id');
    localStorage.removeItem('sovereign_messages');
  };

  return {
    messages,
    conversationId,
    isLoading,
    error,
    sendMessage,
    clearConversation,
  };
};
