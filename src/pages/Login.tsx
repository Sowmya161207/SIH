import React, { useState } from 'react';
import { Shield, Loader2 } from 'lucide-react';

interface LoginProps {
  onLogin: () => void;
}

export const Login: React.FC<LoginProps> = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!username.trim() || !password.trim()) {
      setError('Username and password are required.');
      return;
    }

    setIsLoading(true);

    // Simulate authentication
    setTimeout(() => {
      if (username === 'admin' && password === 'admin') {
        localStorage.setItem('isAuthenticated', 'true');
        onLogin();
      } else {
        setError('Invalid username or password. Try admin/admin.');
        setIsLoading(false);
      }
    }, 1000);
  };

  return (
    <div className="flex h-screen w-screen bg-[#0b0f19] text-slate-100 items-center justify-center p-4">
      <div className="w-full max-w-md bg-[#0f172a] border border-[#1e293b] rounded-2xl p-8 shadow-xl">
        <div className="flex flex-col items-center mb-8">
          <div className="h-12 w-12 rounded-xl bg-indigo-600 flex items-center justify-center text-white shadow-[0_0_15px_rgba(79,70,229,0.4)] mb-4">
            <Shield className="h-6 w-6" />
          </div>
          <h1 className="text-2xl font-bold tracking-wide text-slate-100 uppercase">Sovereign AI</h1>
          <p className="text-xs text-slate-400 font-mono mt-1">SECURE ENCLAVE LOGIN</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5" htmlFor="username">
              Username
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full bg-[#090d16] border border-[#1e293b] rounded-lg px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all"
              placeholder="Enter your username"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5" htmlFor="password">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-[#090d16] border border-[#1e293b] rounded-lg px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all"
              placeholder="Enter your password"
            />
          </div>

          {error && (
            <div className="p-3 bg-rose-500/10 border border-rose-500/20 rounded-lg text-rose-400 text-xs">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="w-full mt-6 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-800/50 disabled:text-slate-500 rounded-lg py-2.5 text-sm font-semibold text-white transition-all flex items-center justify-center space-x-2 shadow-md shadow-indigo-600/20"
          >
            {isLoading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Authenticating...</span>
              </>
            ) : (
              <span>Access Secure Enclave</span>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;
