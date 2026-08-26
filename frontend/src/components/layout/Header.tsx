import React from 'react';
import BackendStatus from './BackendStatus';
import { User, ShieldCheck, LogOut } from 'lucide-react';
import { getSavedUsername } from '../../services/api/auth';

const PAGE_TITLES: Record<string, { title: string; subtitle: string }> = {
  dashboard: { title: 'Command Center', subtitle: 'Operational Overview' },
  documents: { title: 'Knowledge Base', subtitle: 'Document Intelligence' },
  chat: { title: 'AI Assistant', subtitle: 'Sovereign Intelligence Layer' },
  system: { title: 'System Status', subtitle: 'Diagnostics & Configuration' },
};

interface HeaderProps {
  currentTab?: string;
  userRole?: 'admin' | 'employee' | null;
  onLogout?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ currentTab = 'dashboard', userRole, onLogout }) => {
  const username = getSavedUsername();
  const page = PAGE_TITLES[currentTab] || PAGE_TITLES.dashboard;

  return (
    <header
      className="h-14 flex items-center justify-between px-6 flex-shrink-0"
      style={{
        background: 'rgba(6, 8, 16, 0.8)',
        backdropFilter: 'blur(12px)',
        borderBottom: '1px solid rgba(148, 163, 184, 0.06)',
        WebkitBackdropFilter: 'blur(12px)',
      }}
    >
      {/* Left: Page identity */}
      <div className="flex items-center gap-3">
        <div>
          <h2
            className="text-[13px] font-semibold leading-none"
            style={{ color: '#f1f5f9', letterSpacing: '-0.01em' }}
          >
            {page.title}
          </h2>
          <p
            className="text-[10px] mt-1 leading-none"
            style={{
              color: 'rgba(148, 163, 184, 0.45)',
              fontFamily: "'JetBrains Mono', monospace",
              letterSpacing: '0.04em',
            }}
          >
            {page.subtitle}
          </p>
        </div>
      </div>

      {/* Right: Status and Profile */}
      <div className="flex items-center gap-4">
        {/* Backend status pill */}
        <div
          className="flex items-center gap-2 px-3 py-1.5 rounded-full"
          style={{
            background: 'rgba(148, 163, 184, 0.04)',
            border: '1px solid rgba(148, 163, 184, 0.08)',
          }}
        >
          <BackendStatus />
        </div>

        {/* User Profile Badge */}
        {userRole && (
          <div className="flex items-center gap-2">
            <div
              className="flex items-center gap-2 px-3 py-1.5 rounded-full"
              style={{
                background: userRole === 'admin' ? 'rgba(99, 102, 241, 0.1)' : 'rgba(148, 163, 184, 0.06)',
                border: `1px solid ${userRole === 'admin' ? 'rgba(99, 102, 241, 0.2)' : 'rgba(148, 163, 184, 0.1)'}`,
              }}
            >
              {userRole === 'admin' ? (
                <ShieldCheck className="h-3.5 w-3.5" style={{ color: '#818cf8' }} />
              ) : (
                <User className="h-3.5 w-3.5" style={{ color: 'rgba(148, 163, 184, 0.6)' }} />
              )}
              <div className="flex flex-col">
                <span style={{ fontSize: '11px', fontWeight: 600, color: '#f1f5f9', lineHeight: 1 }}>
                  {username || (userRole === 'admin' ? 'Admin' : 'Employee')}
                </span>
              </div>
            </div>
            {onLogout && (
              <button
                onClick={onLogout}
                title="Sign out"
                style={{
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  padding: '6px', borderRadius: '6px',
                  background: 'transparent',
                  border: '1px solid rgba(148,163,184,0.08)',
                  cursor: 'pointer', transition: 'all 0.15s ease',
                }}
                onMouseEnter={(e) => {
                  (e.currentTarget as HTMLButtonElement).style.background = 'rgba(244,63,94,0.06)';
                  (e.currentTarget as HTMLButtonElement).style.borderColor = 'rgba(244,63,94,0.2)';
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget as HTMLButtonElement).style.background = 'transparent';
                  (e.currentTarget as HTMLButtonElement).style.borderColor = 'rgba(148,163,184,0.08)';
                }}
              >
                <LogOut className="h-3.5 w-3.5" style={{ color: 'rgba(148,163,184,0.4)' }} />
              </button>
            )}
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
