'use client';

import { Agent } from '@/types';
import { useLanguage } from '@/lib/LanguageContext';

interface AgentCardProps {
  agent: Agent;
}

export default function AgentCard({ agent }: AgentCardProps) {
  const { t } = useLanguage();
  const statusColors = {
    Active: { bg: 'bg-green-500/10', text: 'text-green-400', indicator: 'bg-green-500' },
    Idle: { bg: 'bg-yellow-500/10', text: 'text-yellow-400', indicator: 'bg-yellow-500' },
    Error: { bg: 'bg-red-500/10', text: 'text-red-400', indicator: 'bg-red-500' },
  };

  const colors = statusColors[agent.status] || statusColors.Idle;

  return (
    <div className="agent-card bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded-xl p-4 transition-all duration-300 cursor-pointer group">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center space-x-3">
          <div className="relative">
            <img
              src={agent.avatar}
              alt={agent.name}
              className="w-12 h-12 rounded-lg object-cover border border-gray-300 dark:border-gray-600 group-hover:dark:border-primary-500 group-hover:border-primary-400 transition-colors"
            />
            <span
              className={`absolute -bottom-1 -right-1 w-3 h-3 rounded-full border-2 border-gray-100 dark:border-gray-800 ${colors.indicator}`}
            ></span>
          </div>
          <div>
            <h3 className="font-medium text-black dark:text-white">{agent.name}</h3>
            <p className="text-xs text-gray-600 dark:text-gray-400">{agent.role}</p>
          </div>
        </div>
        <div className={`px-2 py-1 rounded text-xs font-medium ${colors.bg} ${colors.text}`}>
          {agent.status}
        </div>
      </div>

      <div className="mt-4 space-y-2">
        <div className="flex justify-between text-xs text-gray-600 dark:text-gray-400">
          <span>{t('currentTask')}</span>
          <span className="text-gray-800 dark:text-gray-300">{agent.currentTask}</span>
        </div>
        <div className="w-full bg-gray-300 dark:bg-gray-700 rounded-full h-1.5">
          <div
            className="bg-primary-500 h-1.5 rounded-full"
            style={{ width: `${agent.progress}%` }}
          ></div>
        </div>
        <div className="flex justify-between text-xs text-gray-500 dark:text-gray-500">
          <span>{t('progress')}</span>
          <span>{agent.progress}%</span>
        </div>
      </div>
    </div>
  );
}
