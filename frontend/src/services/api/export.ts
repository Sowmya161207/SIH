import { API_BASE_URL } from '../../config/api';

export const exportApprovalNote = async (content: str, title: string = 'Approval Note') => {
  const response = await fetch(`${API_BASE_URL}/generate/approval-note`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      title,
      content,
      findings: ['Grounded verification completed on-premises'],
    }),
  });

  if (!response.ok) {
    throw new Error('Failed to generate Word document');
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `Approval_Note_${Date.now()}.docx`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
};

export const runSandboxCode = async (code: str): Promise<{ success: bool; output: str; error?: str; execution_time_ms: number }> => {
  const response = await fetch(`${API_BASE_URL}/sandbox/run`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ code }),
  });

  if (!response.ok) {
    throw new Error('Sandbox execution failed');
  }

  return response.json();
};

export const getNetworkAudit = async () => {
  const response = await fetch(`${API_BASE_URL}/telemetry/network-calls`);
  if (!response.ok) {
    throw new Error('Failed to fetch network telemetry');
  }
  return response.json();
};
