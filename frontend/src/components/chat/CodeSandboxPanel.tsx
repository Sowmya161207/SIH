import React, { useState } from 'react';
import { Play, Code, CheckCircle, AlertTriangle, Loader2 } from 'lucide-react';
import { runSandboxCode } from '../../services/api/export';

export const CodeSandboxPanel: React.FC = () => {
  const [code, setCode] = useState<string>(
    '# Isolated Python Execution Sandbox\n# Try writing math or data logic\n\nimport math\n\ndef calculate_pressure_delta(inlet, outlet):\n    return round(math.sqrt(inlet**2 - outlet**2), 2)\n\nprint("Calculated Pressure Delta:", calculate_pressure_delta(15.0, 9.0), "bar")\n'
  );
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<{
    success: boolean;
    output: string;
    error?: string;
    execution_time_ms: number;
  } | null>(null);

  const handleRun = async () => {
    setLoading(true);
    try {
      const res = await runSandboxCode(code);
      setResult(res);
    } catch (err: any) {
      setResult({
        success: false,
        output: '',
        error: err.message || 'Sandbox execution failed',
        execution_time_ms: 0,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-[#0f172a] border border-slate-800 rounded-xl p-5 shadow-lg my-4">
      <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2">
          <div className="p-1.5 bg-indigo-950 border border-indigo-500/30 rounded-lg text-indigo-400">
            <Code className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-100">Air-Gapped Code Execution Sandbox</h3>
            <p className="text-xs text-slate-400">Run Python calculations safely on local CPU/GPU</p>
          </div>
        </div>

        <button
          onClick={handleRun}
          disabled={loading}
          className="inline-flex items-center space-x-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold px-4 py-2 rounded-lg transition-colors shadow-md disabled:opacity-50 cursor-pointer"
        >
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4 fill-white" />}
          <span>Run Code</span>
        </button>
      </div>

      <div className="space-y-4">
        <textarea
          value={code}
          onChange={(e) => setCode(e.target.value)}
          rows={7}
          className="w-full bg-[#020617] border border-slate-800 rounded-lg p-3 text-xs font-mono text-emerald-400 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 leading-relaxed resize-y"
          placeholder="Type Python code here..."
        />

        {result && (
          <div className={`p-4 rounded-lg border text-xs font-mono ${
            result.success ? 'bg-slate-950/80 border-emerald-500/30 text-slate-200' : 'bg-red-950/30 border-red-500/30 text-red-300'
          }`}>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                {result.success ? (
                  <span className="flex items-center text-emerald-400 font-semibold space-x-1">
                    <CheckCircle className="h-3.5 w-3.5" />
                    <span>Execution Succeeded</span>
                  </span>
                ) : (
                  <span className="flex items-center text-red-400 font-semibold space-x-1">
                    <AlertTriangle className="h-3.5 w-3.5" />
                    <span>Execution Failed</span>
                  </span>
                )}
              </div>
              <span className="text-[10px] text-slate-500">{result.execution_time_ms} ms</span>
            </div>

            {result.output && (
              <div className="bg-[#020617] p-2.5 rounded border border-slate-800 text-emerald-400 whitespace-pre-wrap">
                {result.output}
              </div>
            )}

            {result.error && (
              <div className="bg-red-950/50 p-2.5 rounded border border-red-800/40 text-red-300 whitespace-pre-wrap mt-2">
                {result.error}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default CodeSandboxPanel;
