import React from 'react';
import { Database, ArrowRight, Upload, Play, Eye, Cpu, Zap, Lock } from 'lucide-react';
import { DocumentResponse } from '../types/documents';
import BackendStatus from '../components/layout/BackendStatus';

interface DashboardProps {
  documents: DocumentResponse[];
  setCurrentTab: (tab: string) => void;
}

const surface2 = '#0f172a';
const borderDefault = 'rgba(148, 163, 184, 0.08)';
const borderHover = 'rgba(99, 102, 241, 0.18)';

interface MetricCardProps {
  label: string;
  icon: React.ReactNode;
  children: React.ReactNode;
  onClick?: () => void;
  accent?: boolean;
}

const MetricCard: React.FC<MetricCardProps> = ({ label, icon, children, onClick, accent }) => (
  <div
    onClick={onClick}
    className={onClick ? 'cursor-pointer' : ''}
    style={{
      background: accent
        ? 'linear-gradient(135deg, rgba(99,102,241,0.12) 0%, rgba(124,58,237,0.06) 100%)'
        : surface2,
      border: `1px solid ${accent ? 'rgba(99, 102, 241, 0.2)' : borderDefault}`,
      borderRadius: '12px',
      padding: '24px',
      transition: 'all 0.2s ease',
      position: 'relative',
      overflow: 'hidden',
    }}
    onMouseEnter={(e) => {
      if (onClick) {
        (e.currentTarget as HTMLDivElement).style.border = `1px solid ${borderHover}`;
        (e.currentTarget as HTMLDivElement).style.boxShadow = '0 8px 32px rgba(0,0,0,0.3), 0 0 0 1px rgba(99, 102, 241, 0.08)';
        (e.currentTarget as HTMLDivElement).style.transform = 'translateY(-1px)';
      }
    }}
    onMouseLeave={(e) => {
      if (onClick) {
        (e.currentTarget as HTMLDivElement).style.border = `1px solid ${accent ? 'rgba(99, 102, 241, 0.2)' : borderDefault}`;
        (e.currentTarget as HTMLDivElement).style.boxShadow = 'none';
        (e.currentTarget as HTMLDivElement).style.transform = 'translateY(0)';
      }
    }}
  >
    <div className="flex items-center justify-between mb-4">
      <span
        style={{
          fontSize: '9px',
          fontWeight: 700,
          letterSpacing: '0.12em',
          textTransform: 'uppercase',
          color: 'rgba(148, 163, 184, 0.5)',
          fontFamily: "'JetBrains Mono', monospace",
        }}
      >
        {label}
      </span>
      <div
        style={{
          color: accent ? '#818cf8' : 'rgba(148, 163, 184, 0.4)',
        }}
      >
        {icon}
      </div>
    </div>
    {children}
  </div>
);

interface ActionCardProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  onClick: () => void;
}

const ActionCard: React.FC<ActionCardProps> = ({ title, description, icon, onClick }) => (
  <button
    onClick={onClick}
    className="w-full text-left group cursor-pointer"
    style={{
      background: '#0a0f1a',
      border: `1px solid ${borderDefault}`,
      borderRadius: '10px',
      padding: '18px 20px',
      transition: 'all 0.18s ease',
    }}
    onMouseEnter={(e) => {
      (e.currentTarget as HTMLButtonElement).style.background = '#0f172a';
      (e.currentTarget as HTMLButtonElement).style.border = `1px solid rgba(99, 102, 241, 0.15)`;
      (e.currentTarget as HTMLButtonElement).style.boxShadow = '0 4px 20px rgba(0,0,0,0.2)';
    }}
    onMouseLeave={(e) => {
      (e.currentTarget as HTMLButtonElement).style.background = '#0a0f1a';
      (e.currentTarget as HTMLButtonElement).style.border = `1px solid ${borderDefault}`;
      (e.currentTarget as HTMLButtonElement).style.boxShadow = 'none';
    }}
  >
    <div className="flex items-start justify-between gap-3">
      <div className="flex items-start gap-3 flex-1 min-w-0">
        <div
          className="h-8 w-8 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5"
          style={{
            background: 'rgba(99, 102, 241, 0.1)',
            border: '1px solid rgba(99, 102, 241, 0.15)',
          }}
        >
          <div style={{ color: '#818cf8' }}>{icon}</div>
        </div>
        <div className="min-w-0">
          <div
            className="text-sm font-semibold leading-none"
            style={{ color: '#e2e8f0', letterSpacing: '-0.01em' }}
          >
            {title}
          </div>
          <div
            className="text-xs mt-1.5 leading-relaxed"
            style={{ color: 'rgba(148, 163, 184, 0.5)' }}
          >
            {description}
          </div>
        </div>
      </div>
      <ArrowRight
        className="h-4 w-4 flex-shrink-0 mt-0.5 transition-transform duration-200 group-hover:translate-x-0.5"
        style={{ color: 'rgba(148, 163, 184, 0.25)' }}
      />
    </div>
  </button>
);

export const Dashboard: React.FC<DashboardProps> = ({ documents, setCurrentTab }) => {
  return (
    <div className="min-h-full animate-fadeIn">
      {/* Hero Banner */}
      <div
        className="relative overflow-hidden"
        style={{
          background: 'linear-gradient(180deg, #0a0f1a 0%, #080c15 100%)',
          borderBottom: '1px solid rgba(148, 163, 184, 0.06)',
          padding: '40px 48px 36px',
        }}
      >
        {/* Grid background */}
        <div
          className="absolute inset-0 bg-grid opacity-60"
          style={{ pointerEvents: 'none' }}
        />
        {/* Glow accent top-right */}
        <div
          className="absolute -top-20 -right-20 h-64 w-64 rounded-full"
          style={{
            background: 'radial-gradient(circle, rgba(99,102,241,0.08) 0%, transparent 70%)',
            pointerEvents: 'none',
          }}
        />

        <div className="relative max-w-3xl">
          {/* Badge */}
          <div className="flex items-center gap-2 mb-5">
            <div
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-md"
              style={{
                background: 'rgba(99, 102, 241, 0.08)',
                border: '1px solid rgba(99, 102, 241, 0.15)',
              }}
            >
              <Lock className="h-2.5 w-2.5" style={{ color: '#818cf8' }} />
              <span
                style={{
                  fontSize: '9px',
                  fontWeight: 700,
                  letterSpacing: '0.12em',
                  textTransform: 'uppercase',
                  color: '#818cf8',
                  fontFamily: "'JetBrains Mono', monospace",
                }}
              >
                Sovereign Engine Active
              </span>
            </div>
          </div>

          <h1
            style={{
              fontSize: '28px',
              fontWeight: 800,
              letterSpacing: '-0.03em',
              color: '#f1f5f9',
              lineHeight: 1.15,
            }}
          >
            Enterprise Intelligence
            <br />
            <span style={{ color: 'rgba(148, 163, 184, 0.6)', fontWeight: 600 }}>
              Command Center
            </span>
          </h1>

          <p
            className="mt-4 max-w-xl"
            style={{
              fontSize: '13px',
              lineHeight: 1.7,
              color: 'rgba(148, 163, 184, 0.55)',
            }}
          >
            A secure, on-premise AI platform for enterprise operations. Index critical
            documents, run analytics, and query your intelligence layer without exposing
            sensitive data to external systems.
          </p>
        </div>
      </div>

      {/* Content Area */}
      <div style={{ padding: '32px 48px', maxWidth: '1280px' }}>

        {/* Metrics Row */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          {/* System Engine */}
          <MetricCard
            label="System Engine"
            icon={<Cpu className="h-4 w-4" />}
          >
            <div style={{ marginTop: '4px' }}>
              <BackendStatus />
            </div>
            <div
              className="mt-3 text-xs"
              style={{ color: 'rgba(148, 163, 184, 0.4)', fontFamily: "'JetBrains Mono', monospace" }}
            >
              FastAPI · On-Premise
            </div>
          </MetricCard>

          {/* Knowledge Base */}
          <MetricCard
            label="Knowledge Base"
            icon={<Database className="h-4 w-4" />}
          >
            <div className="flex items-end gap-2 mt-1">
              <span
                style={{
                  fontSize: '36px',
                  fontWeight: 800,
                  color: '#f1f5f9',
                  letterSpacing: '-0.03em',
                  lineHeight: 1,
                }}
              >
                {documents.length}
              </span>
              <span
                className="mb-1"
                style={{ fontSize: '12px', color: 'rgba(148, 163, 184, 0.45)' }}
              >
                documents
              </span>
            </div>
            <div
              className="mt-3 text-xs"
              style={{ color: 'rgba(148, 163, 184, 0.4)', fontFamily: "'JetBrains Mono', monospace" }}
            >
              indexed · secure enclave
            </div>
          </MetricCard>

          {/* AI Capability */}
          <MetricCard
            label="AI Capability"
            icon={<Zap className="h-4 w-4" style={{ color: '#818cf8' }} />}
            onClick={() => setCurrentTab('chat')}
            accent
          >
            <div
              style={{
                fontSize: '16px',
                fontWeight: 700,
                color: '#f1f5f9',
                letterSpacing: '-0.02em',
                marginTop: '4px',
              }}
            >
              Ask Sovereign AI
            </div>
            <div className="flex items-center gap-1.5 mt-3">
              <span
                style={{ fontSize: '11px', color: 'rgba(148, 163, 184, 0.45)' }}
              >
                Start secure session
              </span>
              <ArrowRight className="h-3 w-3" style={{ color: 'rgba(99, 102, 241, 0.5)' }} />
            </div>
          </MetricCard>
        </div>

        {/* Quick Actions */}
        <div>
          <div className="flex items-center gap-3 mb-4">
            <span
              style={{
                fontSize: '9px',
                fontWeight: 700,
                letterSpacing: '0.12em',
                textTransform: 'uppercase',
                color: 'rgba(148, 163, 184, 0.35)',
                fontFamily: "'JetBrains Mono', monospace",
              }}
            >
              Quick Actions
            </span>
            <div
              className="flex-1"
              style={{ height: '1px', background: 'rgba(148, 163, 184, 0.06)' }}
            />
          </div>

          <div className="grid grid-cols-3 gap-3">
            <ActionCard
              title="Upload Documents"
              description="Index files into the secure knowledge base for AI querying"
              icon={<Upload className="h-4 w-4" />}
              onClick={() => setCurrentTab('documents')}
            />
            <ActionCard
              title="Ask AI Assistant"
              description="Query your organization's documents with natural language"
              icon={<Play className="h-4 w-4" />}
              onClick={() => setCurrentTab('chat')}
            />
            <ActionCard
              title="Browse Knowledge"
              description="Review, manage, and inspect indexed workspace documents"
              icon={<Eye className="h-4 w-4" />}
              onClick={() => setCurrentTab('documents')}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
