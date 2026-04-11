'use client';

import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import AgentCard from '@/components/AgentCard';
import { apiClient } from '@/lib/apiClient';
import { useLanguage } from '@/lib/LanguageContext';
import { Agent, Log } from '@/types';

function DashboardContent() {
  const { t } = useLanguage();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [logs, setLogs] = useState<Log[]>([]);
  const [loading, setLoading] = useState(true);
  const [health, setHealth] = useState<any>(null);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [healthData, agentsData] = await Promise.all([
        apiClient.getHealth().catch(() => null),
        apiClient.getAgents().catch(() => []),
      ]);

      setHealth(healthData);
      setAgents(agentsData || []);

      // Add log entry
      if (healthData) {
        setLogs((prev) => [
          {
            id: `${Date.now()}-${Math.random()}`,
            time: new Date().toLocaleTimeString('ne-NP', { hour12: false }),
            type: 'info',
            message: `प्रणाली ${healthData.mode} मोडमा छ। एजेन्ट संख्या: ${agentsData?.length || 0}`,
          },
          ...prev.slice(0, 9),
        ]);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const createAgent = async () => {
    const newAgent = {
      name: `New Agent ${agents.length + 1}`,
      description: 'New Agent',
      agent_type: 'reasoning' as const,
      tools: [
        { name: 'web_search', enabled: true },
        { name: 'execute_code', enabled: true },
      ],
    };

    try {
      const createdAgent = await apiClient.createAgent(newAgent as Omit<Agent, 'id'>);
      setAgents((prev) => [createdAgent, ...prev]);
      setLogs((prev) => [
        {
          id: `${Date.now()}-${Math.random()}`,
          time: new Date().toLocaleTimeString('ne-NP', { hour12: false }),
          type: 'success',
          message: `Agent "${createdAgent.name}" created successfully.`,
        },
        ...prev,
      ]);
    } catch (error) {
      console.error('Error creating agent:', error);
      setLogs((prev) => [
        {
          id: `${Date.now()}-${Math.random()}`,
          time: new Date().toLocaleTimeString('ne-NP', { hour12: false }),
          type: 'error',
          message: 'Error creating agent.',
        },
        ...prev,
      ]);
    }
  };

  return (
    <div className="p-8 space-y-8">
        {/* Header section */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-5xl font-black gradient-text">{t('welcome')}</h1>
            <p className="text-slate-400 mt-2 text-lg">
              {health ? (
                <span>
                  <span className="inline-block w-2 h-2 bg-emerald-400 rounded-full mr-2 animate-pulse"></span>
                  {health.mode} Mode
                </span>
              ) : (
                `${t('loadingText')}...`
              )}
            </p>
          </div>
          <button
            onClick={createAgent}
            className="neon-button px-8 py-3 text-white rounded-xl font-semibold flex items-center gap-2 text-lg"
          >
            <i className="fa-solid fa-sparkles"></i>
            {t('newAgent')}
          </button>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Agents Grid */}
          <div className="lg:col-span-2 space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold gradient-text">{t('activeSwarm')}</h2>
                <p className="text-sm text-slate-400 mt-1">Manage and monitor your autonomous agents</p>
              </div>
              <div className="flex space-x-2">
                <button className="px-4 py-2 text-sm font-semibold bg-white/5 backdrop-blur-sm border border-white/10 text-slate-300 rounded-lg hover:bg-white/10 hover:border-white/20 transition-all hover:scale-105">
                  {t('filter')}
                </button>
                <button className="px-4 py-2 text-sm font-semibold bg-white/5 backdrop-blur-sm border border-white/10 text-slate-300 rounded-lg hover:bg-white/10 hover:border-white/20 transition-all hover:scale-105">
                  {t('sort')}
                </button>
              </div>
            </div>

            {loading ? (
              <div className="text-center py-16 text-slate-400 text-lg">{t('loadingText')}...</div>
            ) : agents.length === 0 ? (
              <div className="text-center py-16 text-slate-400">
                <p className="text-lg">{t('noAgents')}</p>
                <p className="text-sm mt-2">Create your first agent to get started</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                {agents.map((agent) => (
                  <AgentCard key={agent.id} agent={agent} />
                ))}
              </div>
            )}
          </div>

          {/* Terminal / Logs */}
          <div className="lg:col-span-1">
            <div className="glass-panel rounded-2xl overflow-hidden flex flex-col h-[500px] border border-cyan-500/20">
              <div className="bg-gradient-to-r from-slate-800 to-slate-900 px-5 py-4 border-b border-white/10 flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="text-cyan-400 text-sm animate-pulse">⚡</div>
                  <span className="text-sm font-mono font-semibold text-white">{t('systemLogs')}</span>
                </div>
                <div className="flex space-x-2">
                  <div className="w-2.5 h-2.5 rounded-full bg-red-500 animate-pulse"></div>
                  <div className="w-2.5 h-2.5 rounded-full bg-yellow-500 animate-pulse animation-delay-1000"></div>
                  <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse animation-delay-2000"></div>
                </div>
              </div>
              <div className="flex-1 bg-gradient-to-b from-slate-900/50 to-slate-950/80 p-4 font-mono text-xs overflow-y-auto space-y-3">
                {logs.length === 0 ? (
                  <div className="text-slate-500 text-center py-8 flex flex-col items-center justify-center h-full">
                    <i className="fa-solid fa-terminal text-2xl mb-3 opacity-50"></i>
                    <p>{t('noLogs')}</p>
                  </div>
                ) : (
                  logs.map((log) => (
                    <div key={log.id} className="flex space-x-3 hover:bg-white/5 px-2 py-1 rounded transition-colors group">
                      <span className="text-slate-600 group-hover:text-slate-500 flex-shrink-0">{log.time}</span>
                      <span
                        className={`flex-shrink-0 font-bold ${
                          log.type === 'info'
                            ? 'text-blue-400'
                            : log.type === 'success'
                            ? 'text-emerald-400'
                            : log.type === 'warning'
                            ? 'text-amber-400'
                            : 'text-red-400'
                        }`}
                      >
                        {log.type === 'info' ? '[•]' : log.type === 'success' ? '[✓]' : log.type === 'warning' ? '[!]' : '[✕]'}
                      </span>
                      <span className="text-slate-300 group-hover:text-slate-200 transition-colors flex-1">{log.message}</span>
                    </div>
                  ))
                )}
                <div className="animate-pulse text-cyan-400 ml-3">▮</div>
              </div>
            </div>
          </div>
        </div>
      </div>

  );
}


export default function DashboardPage() {
  return (
    <Layout>
      <DashboardContent />
    </Layout>
  );
}
