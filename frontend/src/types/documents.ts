export type DocumentStatus = 'uploaded' | 'processing' | 'completed' | 'ready' | 'failed';

export interface DocumentResponse {
  document_id: string;
  filename: string;
  status: DocumentStatus;
  size_bytes: number;
  created_at: string;
  chunks_indexed?: number | null;
  rag_status?: string | null;
}
