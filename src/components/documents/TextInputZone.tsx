import React, { useState } from 'react';
import { Type, AlertTriangle, CheckCircle2, Loader2 } from 'lucide-react';

interface TextInputZoneProps {
  onSubmitText: (title: string, content: string) => Promise<any>;
  isSubmitting: boolean;
  submitError: string | null;
  submitSuccess: boolean;
  clearSubmitState: () => void;
}

export const TextInputZone: React.FC<TextInputZoneProps> = ({
  onSubmitText,
  isSubmitting,
  submitError,
  submitSuccess,
  clearSubmitState,
}) => {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [validationError, setValidationError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError(null);
    clearSubmitState();

    if (!title.trim()) {
      setValidationError('Please enter a title for this information.');
      return;
    }

    if (!content.trim()) {
      setValidationError('Please enter the text content.');
      return;
    }

    try {
      await onSubmitText(title, content);
      setTitle('');
      setContent('');
    } catch (e) {
      // Error handled by hook state
    }
  };

  return (
    <div className="bg-[#0f172a] border border-[#1e293b] rounded-xl p-6 shadow-md max-w-2xl mx-auto w-full flex flex-col">
      <div className="flex items-center mb-4 text-slate-200">
        <h2 className="text-base font-semibold">Direct Text Input</h2>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col flex-1">
        <div className="space-y-4 flex-1 flex flex-col">
          <div>
            <label htmlFor="textTitle" className="block text-sm font-medium text-slate-300 mb-1.5">
              Title
            </label>
            <input
              type="text"
              id="textTitle"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Employee Handbook Excerpt"
              className="w-full bg-[#090d16] border border-[#1e293b] rounded-lg px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
              disabled={isSubmitting}
            />
          </div>

          <div className="flex-1 flex flex-col min-h-[200px]">
            <label htmlFor="textContent" className="block text-sm font-medium text-slate-300 mb-1.5">
              Text Content
            </label>
            <textarea
              id="textContent"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Type or paste information here..."
              className="w-full flex-1 bg-[#090d16] border border-[#1e293b] rounded-lg px-4 py-3 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors resize-y min-h-[150px]"
              disabled={isSubmitting}
            />
          </div>
        </div>

        {/* Validation or API Errors */}
        {(validationError || submitError) && (
          <div className="mt-4 p-3 bg-rose-500/10 border border-rose-500/20 rounded-lg flex items-start space-x-2 text-rose-400 text-xs animate-fadeIn">
            <AlertTriangle className="h-4 w-4 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="font-semibold">Error processing text</p>
              <p className="mt-0.5">{validationError || submitError}</p>
            </div>
          </div>
        )}

        {/* Success Alert */}
        {submitSuccess && (
          <div className="mt-4 p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-lg flex items-start space-x-2 text-emerald-400 text-xs animate-fadeIn">
            <CheckCircle2 className="h-4 w-4 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold">Text Added</p>
              <p className="mt-0.5">The text has been submitted and is being analyzed.</p>
            </div>
          </div>
        )}

        <div className="mt-5 flex justify-end">
          <button
            type="submit"
            disabled={!title.trim() || !content.trim() || isSubmitting}
            className="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-800/50 disabled:text-slate-500 rounded-lg text-xs font-semibold text-white transition-all flex items-center space-x-1.5 shadow-md shadow-indigo-600/15 cursor-pointer"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
                <span>Processing...</span>
              </>
            ) : (
              <>
                <Type className="h-3.5 w-3.5" />
                <span>Add Text to Knowledge</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default TextInputZone;
