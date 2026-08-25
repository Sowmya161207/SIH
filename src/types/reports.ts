import { Source } from './chat';

export type ReportType =
  | 'Equipment Analysis'
  | 'Maintenance Summary'
  | 'Incident Summary'
  | 'Document Analysis'
  | 'Compliance Summary'
  | 'Executive Summary';

export interface ReportRecord {
  id: string;
  title: string;
  type: ReportType;
  generatedAt: string;        // ISO string
  messageContent: string;     // AI response text
  sources: Source[];          // RAG sources
  query: string;              // Original user question
}
