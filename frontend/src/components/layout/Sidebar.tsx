import React from 'react';
import { LayoutDashboard, FileText, MessageSquare, Server, Shield } from 'lucide-react';

interface SidebarProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentTab, setCurrentTab }) => {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'documents', label: 'Documents', icon: FileText },
    { id: 'chat', label: 'AI Assistant', icon: MessageSquare },
    { id: 'system', label: 'System Status', icon: Server },
  ];

  return (
    <aside className="w-64 bg-[#0d131f] border-r border-[#1e293b] flex flex-col h-full text-slate-300">
      {/* Brand Header */}
      <div className="p-6 border-b border-[#1e293b] flex items-center space-x-3">
        <div className="h-9 w-9 rounded-lg bg-indigo-600 flex items-center justify-center text-white shadow-[0_0_12px_rgba(79,70,229,0.35)]">
          <Shield className="h-5 w-5" />
        </div>
        <div>
          <h1 className="font-bold text-sm text-slate-100 tracking-wide uppercase">Sovereign AI</h1>
          <p className="text-[10px] text-slate-500 font-mono">ON-PREMISE ENGINE</p>
        </div>
      </div>

      {/* Navigation Menu */}
      <nav className="flex-1 px-4 py-6 space-y-1.5">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setCurrentTab(item.id)}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 cursor-pointer ${
                isActive
                  ? 'bg-indigo-600/10 text-indigo-400 border-l-2 border-indigo-500 pl-3.5'
                  : 'hover:bg-slate-800/60 text-slate-400 hover:text-slate-200 pl-4 border-l-2 border-transparent'
              }`}
            >
              <Icon className={`h-4.5 w-4.5 ${isActive ? 'text-indigo-400' : 'text-slate-400 group-hover:text-slate-200'}`} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Footer Info */}
      <div className="p-4 border-t border-[#1e293b] text-[11px] font-mono text-slate-500">
        <div>SECURE ENCLAVE ACTIVE</div>
        <div>v1.0.0 (STABLE)</div>
      </div>
    </aside>
  );
};
export default Sidebar;
