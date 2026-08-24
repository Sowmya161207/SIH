import React, { useState } from 'react';
import { Shield, Lock, User, ArrowRight, AlertCircle } from 'lucide-react';

interface LoginProps {
  onLogin: () => void;
}

export const Login: React.FC<LoginProps> = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Empty field validation
    if (!username.trim() || !password.trim()) {
      setError('Please enter both username and password.');
      return;
    }

    setIsLoading(true);

    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 800));

    // Minimal frontend-only login validation
    // For this demo, let's accept demo/demo or admin/admin
    if ((username === 'admin' && password === 'admin') || 
        (username === 'demo' && password === 'demo')) {
      onLogin();
    } else {
      setError('Invalid username or password. Try admin/admin');
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen w-screen bg-[#0b0f19] text-slate-100 overflow-hidden items-center justify-center select-none">
      <div className="w-full max-w-md p-8 bg-[#0f172a] border border-[#1e293b] rounded-2xl shadow-2xl relative overflow-hidden">
        {/* Decorative background element */}
        <div className="absolute -right-20 -top-20 h-64 w-64 bg-radial-gradient from-indigo-500/20 to-transparent pointer-events-none rounded-full blur-3xl"></div>
        
        <div className="relative z-10 flex flex-col items-center mb-8">
          <div className="h-16 w-16 rounded-xl bg-indigo-600 flex items-center justify-center text-white shadow-[0_0_20px_rgba(79,70,229,0.4)] mb-4">
            <Shield className="h-8 w-8" />
          </div>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight">Sovereign AI</h1>
          <p className="text-xs text-slate-400 font-mono mt-1 tracking-widest uppercase">Secure Enclave Access</p>
        </div>

        <form onSubmit={handleSubmit} className="relative z-10 space-y-5">
          {error && (
            <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg flex items-start space-x-2 animate-fadeIn">
              <AlertCircle className="h-5 w-5 text-red-400 shrink-0 mt-0.5" />
              <span className="text-sm text-red-300">{error}</span>
            </div>
          )}

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider ml-1">Username / Email</label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-500">
                <User className="h-5 w-5" />
              </div>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full bg-[#090d16] border border-[#1e293b] focus:border-indigo-500/50 rounded-xl py-3 pl-10 pr-4 text-slate-200 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 transition-all"
                placeholder="Enter your username"
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider ml-1">Password</label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-500">
                <Lock className="h-5 w-5" />
              </div>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-[#090d16] border border-[#1e293b] focus:border-indigo-500/50 rounded-xl py-3 pl-10 pr-4 text-slate-200 placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 transition-all"
                placeholder="Enter your password"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full flex items-center justify-center space-x-2 bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 text-white font-medium py-3 px-4 rounded-xl transition-colors mt-2 disabled:opacity-70 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <span className="flex items-center space-x-2">
                <div className="h-4 w-4 rounded-full border-2 border-white border-t-transparent animate-spin"></div>
                <span>Authenticating...</span>
              </span>
            ) : (
              <>
                <span>Access System</span>
                <ArrowRight className="h-4 w-4" />
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;
