export interface Source {
  document: string;
  page: number;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string | null;
  document_id?: string | null;
  attached_filename?: string | null;
}

export interface ChatResponse {
  answer: string;
  conversation_id: string;
  sources: Source[];
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  sources?: Source[];
  attached_filename?: string;
  document_id?: string;
}
