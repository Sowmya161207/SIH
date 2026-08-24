export type DocumentStatus = 'uploaded' | 'processing' | 'completed' | 'failed';

export interface DocumentResponse {
  document_id: string;
  filename: string;
  status: DocumentStatus;
  size_bytes: number;
  created_at: string;
}
