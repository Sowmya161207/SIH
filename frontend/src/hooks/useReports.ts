import { useState, useCallback } from 'react';
import { ReportRecord, ReportType } from '../types/reports';
import { Source } from '../types/chat';

const STORAGE_KEY = 'sovereign_report_history';

const loadHistory = (): ReportRecord[] => {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
};

const saveHistory = (records: ReportRecord[]) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(records));
};

/** Derives a sensible report title from the user's query. */
export const deriveReportTitle = (query: string): string => {
  const q = query.trim();
  // Strip common question words for a clean title
  const cleaned = q
    .replace(/^(how is|how are|what is the status of|tell me about|give me|show me|analyze|explain)/i, '')
    .trim()
    .replace(/[?!.]+$/, '')
    .trim();
  if (!cleaned) return 'AI Analysis Report';
  // Capitalise first letter of each word up to ~60 chars
  const title = cleaned.length > 60 ? cleaned.slice(0, 57) + '...' : cleaned;
  return title
    .split(' ')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ');
};

/** Derives the most appropriate report type from the query. */
export const deriveReportType = (query: string): ReportType => {
  const q = query.toLowerCase();
  if (/maintenance|service|repair|overhaul/.test(q)) return 'Maintenance Summary';
  if (/incident|fault|failure|accident|breakdown/.test(q)) return 'Incident Summary';
  if (/compliance|regulation|standard|audit|policy/.test(q)) return 'Compliance Summary';
  if (/summary|overview|brief|executive/.test(q)) return 'Executive Summary';
  if (/equipment|pump|valve|motor|compressor|vessel|p-\d|e-\d|v-\d|t-\d/.test(q)) return 'Equipment Analysis';
  return 'Document Analysis';
};

export const useReports = () => {
  const [history, setHistory] = useState<ReportRecord[]>(loadHistory);

  const addReport = useCallback(
    (params: {
      query: string;
      messageContent: string;
      sources: Source[];
    }): ReportRecord => {
      const record: ReportRecord = {
        id: crypto.randomUUID(),
        title: deriveReportTitle(params.query),
        type: deriveReportType(params.query),
        generatedAt: new Date().toISOString(),
        messageContent: params.messageContent,
        sources: params.sources,
        query: params.query,
      };
      setHistory((prev) => {
        const next = [record, ...prev].slice(0, 50); // keep last 50
        saveHistory(next);
        return next;
      });
      return record;
    },
    []
  );

  const removeReport = useCallback((id: string) => {
    setHistory((prev) => {
      const next = prev.filter((r) => r.id !== id);
      saveHistory(next);
      return next;
    });
  }, []);

  const clearHistory = useCallback(() => {
    setHistory([]);
    localStorage.removeItem(STORAGE_KEY);
  }, []);

  return { history, addReport, removeReport, clearHistory };
};
