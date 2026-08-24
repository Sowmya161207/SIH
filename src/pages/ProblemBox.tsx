import React, { useState } from 'react';
import { AlertOctagon, Send, CheckCircle2 } from 'lucide-react';

export const ProblemBox: React.FC = () => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [location, setLocation] = useState('');
  const [priority, setPriority] = useState('Medium');
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !description.trim()) return;
    
    // Simulate API submission
    setIsSubmitted(true);
    setTitle('');
    setDescription('');
    setLocation('');
    setPriority('Medium');
    
    // Reset success message after 5 seconds
    setTimeout(() => setIsSubmitted(false), 5000);
  };

  const getPriorityColor = (level: string) => {
    switch (level) {
      case 'Low': return 'text-emerald-400';
      case 'Medium': return 'text-amber-400';
      case 'High': return 'text-rose-400';
      case 'Critical': return 'text-red-500 font-bold';
      default: return 'text-slate-300';
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn max-w-2xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 tracking-tight flex items-center">
          <AlertOctagon className="h-6 w-6 mr-3 text-rose-500" />
          Report a Problem
        </h1>
        <p className="text-xs text-slate-400 mt-2 leading-relaxed">
          Found an issue? Report it so the responsible team can take action quickly.
        </p>
      </div>

      <div className="bg-[#0f172a] border border-[#1e293b] rounded-xl p-6 shadow-md">
        {isSubmitted && (
          <div className="mb-6 p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-lg flex items-start space-x-3 text-emerald-400 animate-fadeIn">
            <CheckCircle2 className="h-5 w-5 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-sm">Problem reported successfully.</p>
              <p className="text-xs mt-1 text-emerald-400/80">The responsible team has been notified.</p>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label htmlFor="title" className="block text-sm font-medium text-slate-300 mb-1.5">
              Problem Title <span className="text-rose-500">*</span>
            </label>
            <input
              type="text"
              id="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Brief summary of the issue"
              required
              className="w-full bg-[#090d16] border border-[#1e293b] rounded-lg px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div>
              <label htmlFor="location" className="block text-sm font-medium text-slate-300 mb-1.5">
                Location / Department
              </label>
              <input
                type="text"
                id="location"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="e.g. Server Room A"
                className="w-full bg-[#090d16] border border-[#1e293b] rounded-lg px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
              />
            </div>

            <div>
              <label htmlFor="priority" className="block text-sm font-medium text-slate-300 mb-1.5">
                Priority
              </label>
              <select
                id="priority"
                value={priority}
                onChange={(e) => setPriority(e.target.value)}
                className={`w-full bg-[#090d16] border border-[#1e293b] rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors appearance-none ${getPriorityColor(priority)}`}
              >
                <option value="Low" className="text-emerald-400">Low</option>
                <option value="Medium" className="text-amber-400">Medium</option>
                <option value="High" className="text-rose-400">High</option>
                <option value="Critical" className="text-red-500 font-bold">Critical</option>
              </select>
            </div>
          </div>

          <div>
            <label htmlFor="description" className="block text-sm font-medium text-slate-300 mb-1.5">
              Problem Description <span className="text-rose-500">*</span>
            </label>
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe the problem in detail..."
              required
              rows={5}
              className="w-full bg-[#090d16] border border-[#1e293b] rounded-lg px-4 py-3 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors resize-none"
            />
          </div>

          <div className="pt-2 flex justify-end">
            <button
              type="submit"
              disabled={!title.trim() || !description.trim()}
              className="flex items-center space-x-2 px-6 py-2.5 bg-rose-600 hover:bg-rose-500 disabled:bg-slate-800 disabled:text-slate-500 text-white rounded-lg text-sm font-semibold transition-all shadow-md shadow-rose-600/15 cursor-pointer"
            >
              <Send className="h-4 w-4" />
              <span>Submit Report</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ProblemBox;
