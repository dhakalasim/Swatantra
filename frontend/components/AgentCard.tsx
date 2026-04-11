'use client';

import { Agent } from '@/types';
import { useLanguage } from '@/lib/LanguageContext';

interface AgentCardProps {
  agent: Agent;
}

export default function AgentCard({ agent }: AgentCardProps) {
  const { t } = useLanguage();
  const statusColors = {
    Active: { 
      bg: 'from-emerald-500/20 to-teal-500/10', 
      text: 'text-emerald-300', 
      indicator: 'bg-emerald-500',
      ring: 'ring-emerald-500/30'
    },
    Idle: { 
      bg: 'from-amber-500/20 to-orange-500/10', 
      text: 'text-amber-300', 
      indicator: 'bg-amber-500',
      ring: 'ring-amber-500/30'
    },
    Error: { 
      bg: 'from-red-500/20 to-pink-500/10', 
      text: 'text-red-300', 
      indicator: 'bg-red-500',
      ring: 'ring-red-500/30'
    },
  };

  const colors = statusColors[(agent.status as keyof typeof statusColors) || 'Idle'] || statusColors.Idle;

  return (
    <div className="agent-card group">
      <div className={`relative bg-gradient-to-br ${colors.bg} backdrop-blur-xl border border-white/10 rounded-2xl p-6 transition-all duration-500 overflow-hidden`}>
        {/* Animated gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
        
        {/* Top accent line */}
        <div className={`absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent ${colors.text} to-transparent opacity-0 group-hover:opacity-100 transition-opacity`}></div>

        <div className="relative z-10">
          {/* Header with avatar and status */}
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center space-x-3 flex-1">
              <div className={`relative ring-2 ${colors.ring}`}>
                <img
                  src={agent.avatar}
                  alt={agent.name}
                  className="w-14 h-14 rounded-xl object-cover"
                />
                <span
                  className={`absolute -bottom-2 -right-2 w-4 h-4 rounded-full border-2 border-slate-800 ${colors.indicator} animate-pulse`}
                ></span>
              </div>
              <div className="flex-1">
                <h3 className="font-bold text-white text-lg group-hover:gradient-text transition-all">{agent.name}</h3>
                <p className="text-xs text-slate-400 group-hover:text-slate-300 transition-colors">{agent.description || 'AI Agent'}</p>
              </div>
            </div>
            <div className={`px-3 py-1 rounded-full text-xs font-semibold ${colors.text} bg-white/5 backdrop-blur-sm border border-white/10`}>
              {agent.status}
            </div>
          </div>

          {/* Stats section */}
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-slate-300 font-medium">{t('progress')}</span>
              <span className={`text-sm font-bold ${colors.text}`}>{agent.progress}%</span>
            </div>
            
            {/* Advanced progress bar with gradient */}
            <div className="relative h-2 bg-white/5 rounded-full overflow-hidden border border-white/10">
              <div
                className={`h-full rounded-full bg-gradient-to-r ${colors.bg.replace('from-', 'from-').replace('to-', 'to-')} transition-all duration-500`}
                style={{ width: `${agent.progress}%` }}
              >
                <div className="absolute inset-0 animate-shimmer"></div>
              </div>
            </div>

            {/* Current task with icon */}
            {agent.currentTask && (
              <div className="flex items-center space-x-2 mt-3 p-2 rounded-lg bg-white/5 border border-white/10">
                <span className="text-cyan-400 text-sm">⚡</span>
                <span className="text-xs text-slate-300 truncate">{agent.currentTask}</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
