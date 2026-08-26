import React from 'react';
import { LayoutDashboard, FileText, MessageSquare, Shield, Activity, ChevronRight, ClipboardList, History } from 'lucide-react';

interface SidebarProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
  userRole?: 'admin' | 'employee' | null;
}

const navItems = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: LayoutDashboard,
    description: 'Overview',
  },
  {
    id: 'documents',
    label: 'Knowledge Base',
    icon: FileText,
    description: 'Documents',
  },
  {
    id: 'chat',
    label: 'AI Assistant',
    icon: MessageSquare,
    description: 'Intelligence',
  },
  {
    id: 'reports',
    label: 'Reports',
    icon: ClipboardList,
    description: 'Generated',
  },
  {
    id: 'audit-logs',
    label: 'Audit Logs',
    icon: History,
    description: 'System Activity',
  },
];

export const Sidebar: React.FC<SidebarProps> = ({ currentTab, setCurrentTab, userRole }) => {
  const visibleNavItems = navItems.filter((item) => {
    if (userRole === 'employee' && item.id === 'audit-logs') {
      return false;
    }
    return true;
  });

  return (
    <aside
      className="w-60 flex flex-col h-full flex-shrink-0"
      style={{
        background: 'linear-gradient(180deg, #0a0f1a 0%, #080c15 100%)',
        borderRight: '1px solid rgba(148, 163, 184, 0.06)',
      }}
    >
      {/* Brand */}
      <div className="px-5 pt-6 pb-5" style={{ borderBottom: '1px solid rgba(148, 163, 184, 0.05)' }}>
        <div className="flex items-center gap-3">
          <div
            className="h-8 w-8 rounded-lg flex items-center justify-center flex-shrink-0"
            style={{
              background: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)',
              boxShadow: '0 0 20px rgba(99, 102, 241, 0.2), inset 0 1px 0 rgba(255,255,255,0.1)',
            }}
          >
            <Shield className="h-4 w-4 text-white" />
          </div>
          <div>
            <h1 style={{ fontSize: '14px', fontWeight: 700, color: '#f1f5f9', letterSpacing: '-0.02em', lineHeight: 1.1 }}>
              Sovereign AI
            </h1>
            <p style={{ fontSize: '9px', color: 'rgba(148, 163, 184, 0.4)', fontFamily: "'JetBrains Mono', monospace", marginTop: '2px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Secure Enclave
            </p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto scrollbar-none">
        <div
          className="text-[9px] font-semibold tracking-[0.12em] uppercase px-3 mb-2"
          style={{ color: 'rgba(148, 163, 184, 0.35)', fontFamily: "'JetBrains Mono', monospace" }}
        >
          Workspace
        </div>

        {visibleNavItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;

          return (
            <button
              key={item.id}
              onClick={() => setCurrentTab(item.id)}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left group relative cursor-pointer"
              style={{
                background: isActive
                  ? 'linear-gradient(90deg, rgba(99, 102, 241, 0.12) 0%, rgba(99, 102, 241, 0.04) 100%)'
                  : 'transparent',
                border: isActive
                  ? '1px solid rgba(99, 102, 241, 0.15)'
                  : '1px solid transparent',
                transition: 'all 0.15s ease',
              }}
              onMouseEnter={(e) => {
                if (!isActive) {
                  e.currentTarget.style.background = 'rgba(148, 163, 184, 0.04)';
                  e.currentTarget.style.border = '1px solid rgba(148, 163, 184, 0.06)';
                }
              }}
              onMouseLeave={(e) => {
                if (!isActive) {
                  e.currentTarget.style.background = 'transparent';
                  e.currentTarget.style.border = '1px solid transparent';
                }
              }}
            >
              {/* Active bar */}
              {isActive && (
                <div
                  className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 rounded-r"
                  style={{ background: '#6366f1' }}
                />
              )}

              <div
                className="h-7 w-7 rounded-md flex items-center justify-center flex-shrink-0"
                style={{
                  background: isActive
                    ? 'rgba(99, 102, 241, 0.15)'
                    : 'rgba(148, 163, 184, 0.05)',
                  transition: 'background 0.15s ease',
                }}
              >
                <Icon
                  className="h-3.5 w-3.5"
                  style={{ color: isActive ? '#818cf8' : 'rgba(148, 163, 184, 0.5)' }}
                />
              </div>

              <div className="flex-1 min-w-0">
                <div
                  className="text-[13px] font-medium leading-none"
                  style={{
                    color: isActive ? '#f1f5f9' : 'rgba(148, 163, 184, 0.65)',
                    transition: 'color 0.15s ease',
                  }}
                >
                  {item.label}
                </div>
              </div>

              {isActive && (
                <ChevronRight className="h-3 w-3 flex-shrink-0" style={{ color: 'rgba(99, 102, 241, 0.5)' }} />
              )}
            </button>
          );
        })}
      </nav>

      {/* Footer Status */}
      <div
        className="px-4 py-4"
        style={{ borderTop: '1px solid rgba(148, 163, 184, 0.05)' }}
      >
        <div className="flex items-center gap-2">
          <div className="relative flex-shrink-0">
            <div
              className="h-1.5 w-1.5 rounded-full"
              style={{ background: '#10b981', boxShadow: '0 0 6px rgba(16, 185, 129, 0.5)' }}
            />
          </div>
          <div className="flex-1 min-w-0">
            <div
              className="text-[9px] font-semibold uppercase tracking-[0.12em]"
              style={{ color: 'rgba(16, 185, 129, 0.7)', fontFamily: "'JetBrains Mono', monospace" }}
            >
              Secure Enclave
            </div>
            <div
              className="text-[9px] tracking-wider mt-0.5"
              style={{ color: 'rgba(148, 163, 184, 0.3)', fontFamily: "'JetBrains Mono', monospace" }}
            >
              v1.0.0 · On-Premise
            </div>
          </div>
          <Activity className="h-3 w-3 flex-shrink-0" style={{ color: 'rgba(16, 185, 129, 0.4)' }} />
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
