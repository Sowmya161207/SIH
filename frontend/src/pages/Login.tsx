import React, { useState } from 'react';
import { Shield, Lock, User, ArrowRight, AlertCircle } from 'lucide-react';
import { loginApi, saveSession, mapToUIRole } from '../services/api/auth';

interface LoginProps {
  onLogin: (role: 'admin' | 'employee') => void;
}

export const Login: React.FC<LoginProps> = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (!username.trim() || !password.trim()) {
      setError('Please enter both username and password.');
      return;
    }
    setIsLoading(true);
    try {
      const result = await loginApi({ username: username.trim(), password });
      saveSession(result.access_token, result.user.role, result.user.username);
      const uiRole = mapToUIRole(result.user.role);
      onLogin(uiRole);
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      if (detail) {
        setError(typeof detail === 'string' ? detail : 'Invalid credentials.');
      } else {
        setError('Invalid username or password.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const inputStyle = {
    width: '100%',
    background: 'rgba(6, 8, 16, 0.8)',
    border: '1px solid rgba(148, 163, 184, 0.1)',
    borderRadius: '10px',
    padding: '11px 14px 11px 40px',
    color: '#e2e8f0',
    fontSize: '13.5px',
    outline: 'none',
    transition: 'border-color 0.15s ease, box-shadow 0.15s ease',
    caretColor: '#818cf8',
  };

  return (
    <div
      className="flex h-screen w-screen items-center justify-center"
      style={{ background: '#060810', position: 'relative', overflow: 'hidden' }}
    >
      {/* Background grid */}
      <div className="absolute inset-0 bg-grid opacity-60" style={{ pointerEvents: 'none' }} />

      {/* Glow orbs */}
      <div
        className="absolute"
        style={{
          top: '-200px',
          left: '50%',
          transform: 'translateX(-50%)',
          width: '600px',
          height: '400px',
          background: 'radial-gradient(ellipse at center, rgba(99,102,241,0.08) 0%, transparent 70%)',
          pointerEvents: 'none',
        }}
      />

      {/* Login card */}
      <div
        className="relative w-full"
        style={{
          maxWidth: '400px',
          background: '#0a0f1a',
          border: '1px solid rgba(148, 163, 184, 0.09)',
          borderRadius: '16px',
          padding: '40px',
          boxShadow: '0 32px 80px rgba(0,0,0,0.6), 0 0 0 1px rgba(99, 102, 241, 0.04)',
        }}
      >
        {/* Header */}
        <div className="flex flex-col items-center mb-8">
          <div
            className="h-14 w-14 rounded-2xl flex items-center justify-center mb-5"
            style={{
              background: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)',
              boxShadow: '0 0 32px rgba(99, 102, 241, 0.25), inset 0 1px 0 rgba(255,255,255,0.1)',
            }}
          >
            <Shield className="h-7 w-7 text-white" />
          </div>
          <h1
            style={{
              fontSize: '20px',
              fontWeight: 800,
              color: '#f1f5f9',
              letterSpacing: '-0.025em',
            }}
          >
            Sovereign AI
          </h1>
          <p
            className="mt-1"
            style={{
              fontSize: '10px',
              letterSpacing: '0.15em',
              textTransform: 'uppercase',
              color: 'rgba(148, 163, 184, 0.35)',
              fontFamily: "'JetBrains Mono', monospace",
            }}
          >
            Secure Enclave Access
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div
              className="flex items-start gap-2 animate-fadeIn"
              style={{
                padding: '10px 12px',
                borderRadius: '8px',
                background: 'rgba(244, 63, 94, 0.06)',
                border: '1px solid rgba(244, 63, 94, 0.15)',
              }}
            >
              <AlertCircle className="h-4 w-4 flex-shrink-0 mt-0.5" style={{ color: '#fb7185' }} />
              <span style={{ fontSize: '12px', color: 'rgba(251, 113, 133, 0.8)' }}>{error}</span>
            </div>
          )}

          {/* Username */}
          <div>
            <label
              style={{
                display: 'block',
                fontSize: '10px',
                fontWeight: 600,
                textTransform: 'uppercase',
                letterSpacing: '0.08em',
                color: 'rgba(148, 163, 184, 0.4)',
                marginBottom: '7px',
                fontFamily: "'JetBrains Mono', monospace",
              }}
            >
              Username
            </label>
            <div style={{ position: 'relative' }}>
              <div
                style={{
                  position: 'absolute',
                  left: '13px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  color: 'rgba(148, 163, 184, 0.3)',
                  pointerEvents: 'none',
                }}
              >
                <User className="h-4 w-4" />
              </div>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                style={inputStyle}
                placeholder="Enter username"
                autoComplete="username"
                onFocus={(e) => {
                  (e.target as HTMLInputElement).style.borderColor = 'rgba(99, 102, 241, 0.35)';
                  (e.target as HTMLInputElement).style.boxShadow = '0 0 0 3px rgba(99, 102, 241, 0.08)';
                }}
                onBlur={(e) => {
                  (e.target as HTMLInputElement).style.borderColor = 'rgba(148, 163, 184, 0.1)';
                  (e.target as HTMLInputElement).style.boxShadow = 'none';
                }}
              />
            </div>
          </div>

          {/* Password */}
          <div>
            <label
              style={{
                display: 'block',
                fontSize: '10px',
                fontWeight: 600,
                textTransform: 'uppercase',
                letterSpacing: '0.08em',
                color: 'rgba(148, 163, 184, 0.4)',
                marginBottom: '7px',
                fontFamily: "'JetBrains Mono', monospace",
              }}
            >
              Password
            </label>
            <div style={{ position: 'relative' }}>
              <div
                style={{
                  position: 'absolute',
                  left: '13px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  color: 'rgba(148, 163, 184, 0.3)',
                  pointerEvents: 'none',
                }}
              >
                <Lock className="h-4 w-4" />
              </div>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                style={inputStyle}
                placeholder="Enter password"
                autoComplete="current-password"
                onFocus={(e) => {
                  (e.target as HTMLInputElement).style.borderColor = 'rgba(99, 102, 241, 0.35)';
                  (e.target as HTMLInputElement).style.boxShadow = '0 0 0 3px rgba(99, 102, 241, 0.08)';
                }}
                onBlur={(e) => {
                  (e.target as HTMLInputElement).style.borderColor = 'rgba(148, 163, 184, 0.1)';
                  (e.target as HTMLInputElement).style.boxShadow = 'none';
                }}
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full flex items-center justify-center gap-2 cursor-pointer"
            style={{
              padding: '12px 20px',
              borderRadius: '10px',
              background: 'linear-gradient(135deg, #6366f1 0%, #7c3aed 100%)',
              border: 'none',
              color: '#fff',
              fontSize: '14px',
              fontWeight: 600,
              letterSpacing: '-0.01em',
              boxShadow: '0 4px 16px rgba(99, 102, 241, 0.3)',
              opacity: isLoading ? 0.7 : 1,
              transition: 'all 0.15s ease',
              marginTop: '8px',
            }}
            onMouseEnter={(e) => {
              if (!isLoading) {
                (e.currentTarget as HTMLButtonElement).style.boxShadow = '0 6px 24px rgba(99, 102, 241, 0.4)';
                (e.currentTarget as HTMLButtonElement).style.transform = 'translateY(-1px)';
              }
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLButtonElement).style.boxShadow = '0 4px 16px rgba(99, 102, 241, 0.3)';
              (e.currentTarget as HTMLButtonElement).style.transform = 'translateY(0)';
            }}
          >
            {isLoading ? (
              <span className="flex items-center gap-2">
                <div className="h-4 w-4 rounded-full border-2 border-white border-t-transparent animate-spin" />
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

        {/* Hint */}
        <div className="text-center mt-4">
          <span
            style={{
              fontSize: '10px',
              color: 'rgba(148, 163, 184, 0.25)',
              fontFamily: "'JetBrains Mono', monospace",
              letterSpacing: '0.04em',
            }}
          >
            Use your assigned credentials to sign in
          </span>
        </div>

        {/* Footer */}
        <div className="text-center mt-3">
          <span
            style={{
              fontSize: '10px',
              color: 'rgba(148, 163, 184, 0.2)',
              fontFamily: "'JetBrains Mono', monospace",
              letterSpacing: '0.04em',
            }}
          >
            Sovereign AI · On-Premise · v1.0.0
          </span>
        </div>
      </div>
    </div>
  );
};
export default Login;
