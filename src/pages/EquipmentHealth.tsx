import React, { useState, useEffect } from 'react';
import { Activity, Thermometer, Gauge, AlertTriangle, MessageSquare, AlertCircle, TrendingUp, Zap, Server } from 'lucide-react';
import { Equipment } from '../types/equipment';
import { getEquipmentHealth } from '../services/api/equipment';

interface EquipmentHealthProps {
  onAskAI: (query: string) => void;
}

export const EquipmentHealth: React.FC<EquipmentHealthProps> = ({ onAskAI }) => {
  const [equipment, setEquipment] = useState<Equipment | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const data = await getEquipmentHealth('P-101');
        setEquipment(data);
      } catch (error) {
        console.error('Failed to fetch equipment health', error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchHealth();
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-pulse flex flex-col items-center">
          <Activity className="h-10 w-10 text-indigo-500 mb-4 animate-spin-slow" />
          <span className="text-slate-400 font-mono text-sm">LOADING ASSET DATA...</span>
        </div>
      </div>
    );
  }

  if (!equipment) return null;

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Healthy': return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20';
      case 'Warning': return 'text-amber-400 bg-amber-500/10 border-amber-500/20';
      case 'Critical': return 'text-rose-400 bg-rose-500/10 border-rose-500/20';
      default: return 'text-slate-400 bg-slate-500/10 border-slate-500/20';
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'Low': return 'text-emerald-400';
      case 'Medium': return 'text-amber-400';
      case 'High': return 'text-rose-400';
      default: return 'text-slate-400';
    }
  };

  const handleAskAI = () => {
    onAskAI(`Tell me more about the issues and recommended actions for ${equipment.name}. Context: Status is ${equipment.status} with health score ${equipment.healthScore}%. Issues: ${equipment.issues.map(i => i.description).join(', ')}.`);
  };

  return (
    <div className="space-y-6 animate-fadeIn pb-10">
      {/* Header section */}
      <div className="flex items-center justify-between border-b border-[#1e293b] pb-6">
        <div>
          <div className="flex items-center space-x-3 mb-2">
            <div className="h-10 w-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 shadow-[0_0_15px_rgba(99,102,241,0.15)]">
              <Server className="h-5 w-5" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-slate-100 tracking-tight">{equipment.name}</h1>
              <span className="text-sm text-slate-400 font-mono tracking-wider">ASSET ID: {equipment.id}</span>
            </div>
          </div>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex flex-col items-end mr-4">
            <span className="text-xs text-slate-500 font-mono uppercase tracking-wider mb-1">Health Score</span>
            <span className="text-3xl font-extrabold text-slate-100">{equipment.healthScore}<span className="text-lg text-slate-500 font-medium">%</span></span>
          </div>
          <div className={`px-4 py-2 rounded-lg border font-semibold tracking-wide uppercase text-sm ${getStatusColor(equipment.status)}`}>
            {equipment.status}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Metrics */}
        <div className="lg:col-span-2 space-y-6">
          <h2 className="text-sm font-semibold text-slate-400 tracking-wider uppercase font-mono flex items-center">
            <Activity className="h-4 w-4 mr-2" />
            Live Telemetry
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Temp Card */}
            <div className="bg-[#0f172a] border border-[#1e293b] rounded-xl p-5 relative overflow-hidden group hover:border-amber-500/30 transition-colors">
              <div className="absolute top-0 right-0 w-24 h-24 bg-radial-gradient from-amber-500/5 to-transparent rounded-bl-full pointer-events-none"></div>
              <div className="flex justify-between items-start mb-4 relative z-10">
                <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Temperature</span>
                <Thermometer className="h-4 w-4 text-amber-500" />
              </div>
              <div className="text-2xl font-bold text-slate-200">{equipment.metrics.temperature}<span className="text-sm text-slate-500 ml-1">°C</span></div>
              
              {/* Fake trendline */}
              <div className="mt-4 flex items-end space-x-1 h-8 opacity-60">
                <div className="w-1/6 bg-amber-500/20 rounded-t h-[40%]"></div>
                <div className="w-1/6 bg-amber-500/30 rounded-t h-[50%]"></div>
                <div className="w-1/6 bg-amber-500/40 rounded-t h-[45%]"></div>
                <div className="w-1/6 bg-amber-500/60 rounded-t h-[70%]"></div>
                <div className="w-1/6 bg-amber-500/80 rounded-t h-[85%]"></div>
                <div className="w-1/6 bg-amber-500 rounded-t h-[100%] animate-pulse"></div>
              </div>
            </div>

            {/* Vibration Card */}
            <div className="bg-[#0f172a] border border-[#1e293b] rounded-xl p-5 relative overflow-hidden group hover:border-rose-500/30 transition-colors">
              <div className="absolute top-0 right-0 w-24 h-24 bg-radial-gradient from-rose-500/5 to-transparent rounded-bl-full pointer-events-none"></div>
              <div className="flex justify-between items-start mb-4 relative z-10">
                <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Vibration</span>
                <TrendingUp className="h-4 w-4 text-rose-500" />
              </div>
              <div className="text-2xl font-bold text-slate-200">{equipment.metrics.vibration}<span className="text-sm text-slate-500 ml-1">mm/s</span></div>
              
              {/* Fake trendline */}
              <div className="mt-4 flex items-end space-x-1 h-8 opacity-60">
                <div className="w-1/6 bg-rose-500/20 rounded-t h-[30%]"></div>
                <div className="w-1/6 bg-rose-500/30 rounded-t h-[40%]"></div>
                <div className="w-1/6 bg-rose-500/50 rounded-t h-[60%]"></div>
                <div className="w-1/6 bg-rose-500/70 rounded-t h-[80%]"></div>
                <div className="w-1/6 bg-rose-500/90 rounded-t h-[95%]"></div>
                <div className="w-1/6 bg-rose-500 rounded-t h-[100%] animate-pulse"></div>
              </div>
            </div>

            {/* Pressure Card */}
            <div className="bg-[#0f172a] border border-[#1e293b] rounded-xl p-5 relative overflow-hidden group hover:border-emerald-500/30 transition-colors">
              <div className="absolute top-0 right-0 w-24 h-24 bg-radial-gradient from-emerald-500/5 to-transparent rounded-bl-full pointer-events-none"></div>
              <div className="flex justify-between items-start mb-4 relative z-10">
                <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Pressure</span>
                <Gauge className="h-4 w-4 text-emerald-500" />
              </div>
              <div className="text-2xl font-bold text-slate-200">{equipment.metrics.pressure}<span className="text-sm text-slate-500 ml-1">bar</span></div>
              
              {/* Fake trendline */}
              <div className="mt-4 flex items-end space-x-1 h-8 opacity-60">
                <div className="w-1/6 bg-emerald-500/60 rounded-t h-[60%]"></div>
                <div className="w-1/6 bg-emerald-500/50 rounded-t h-[50%]"></div>
                <div className="w-1/6 bg-emerald-500/60 rounded-t h-[60%]"></div>
                <div className="w-1/6 bg-emerald-500/50 rounded-t h-[50%]"></div>
                <div className="w-1/6 bg-emerald-500/50 rounded-t h-[50%]"></div>
                <div className="w-1/6 bg-emerald-500/60 rounded-t h-[60%]"></div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column - Issues & AI */}
        <div className="space-y-6">
          <h2 className="text-sm font-semibold text-slate-400 tracking-wider uppercase font-mono flex items-center">
            <AlertTriangle className="h-4 w-4 mr-2" />
            Detected Issues
          </h2>
          
          <div className="bg-[#0f172a] border border-[#1e293b] rounded-xl p-1 overflow-hidden shadow-sm">
            {equipment.issues.length === 0 ? (
              <div className="p-6 text-center text-slate-500 text-sm">
                No active issues detected.
              </div>
            ) : (
              <div className="divide-y divide-[#1e293b]">
                {equipment.issues.map((issue) => (
                  <div key={issue.id} className="p-4 flex items-start justify-between bg-slate-900/50 hover:bg-[#0d131f] transition-colors">
                    <div className="flex items-start space-x-3">
                      <AlertCircle className={`h-4 w-4 mt-0.5 ${getRiskColor(issue.riskLevel)}`} />
                      <div>
                        <p className="text-sm text-slate-200 font-medium leading-snug">{issue.description}</p>
                        <span className={`text-[10px] font-mono tracking-wider uppercase mt-1 inline-block ${getRiskColor(issue.riskLevel)}`}>
                          {issue.riskLevel} Risk
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* AI Recommendation Section */}
      <div className="mt-8">
        <div className="bg-gradient-to-br from-indigo-900/20 via-[#0f172a] to-slate-900 border border-indigo-500/20 rounded-xl p-1 overflow-hidden relative shadow-lg">
          <div className="absolute top-0 right-0 h-full w-1/3 bg-radial-gradient from-indigo-500/10 to-transparent pointer-events-none"></div>
          
          <div className="p-6 relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div className="flex items-start space-x-4">
              <div className="p-3 bg-indigo-500/10 rounded-lg text-indigo-400 border border-indigo-500/20 shadow-[0_0_15px_rgba(99,102,241,0.1)] shrink-0">
                <Zap className="h-6 w-6" />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-slate-200 mb-1 flex items-center">
                  Sovereign AI Recommendation
                  <span className="ml-2 px-1.5 py-0.5 text-[9px] uppercase tracking-wider bg-indigo-500/20 text-indigo-300 rounded font-mono">Auto-generated</span>
                </h3>
                <p className="text-sm text-slate-400 leading-relaxed max-w-3xl">
                  {equipment.aiRecommendation}
                </p>
              </div>
            </div>
            
            <button
              onClick={handleAskAI}
              className="shrink-0 flex items-center justify-center space-x-2 bg-indigo-600 hover:bg-indigo-500 text-white px-5 py-2.5 rounded-lg text-sm font-medium transition-all shadow-[0_0_15px_rgba(79,70,229,0.4)] hover:shadow-[0_0_20px_rgba(79,70,229,0.6)] cursor-pointer"
            >
              <MessageSquare className="h-4 w-4" />
              <span>Ask AI About This</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EquipmentHealth;
