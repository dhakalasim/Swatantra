'use client';

import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import AgentCard from '@/components/AgentCard';
import { apiClient } from '@/lib/apiClient';
import { useLanguage } from '@/lib/LanguageContext';
import { Agent, Log } from '@/types';

export default function DashboardPage() {
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
            id: Date.now(),
            time: new Date().toLocaleTimeString('ne-NP', { hour12: false }),
            type: 'infSystem is in ${healthData.mode} mode. Agents
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
      role: 'General Assistant',
      status: 'Active' as const,
      currentTask: 'Starting...',
      progress: 5,
      avatar: 'https://ui-avatars.com/api/?name=Agent&background=6366f1&color=fff',
      description: 'New Agent',
      agent_type: 'reasoning' as const,
      tools: ['web_search', 'execute_code'],
    };

    try {
      const createdAgent = await apiClient.createAgent(newAgent);
      setAgents((prev) => [createdAgent, ...prev]);
      setLogs((prev) => [
        {
          id: Date.now(),
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
          id: Date.now(),
          time: new Date().toLocaleTimeString('ne-NP', { hour12: false }),
          type: 'error',
          message: 'Error creating agent.',
        },
        ...prev,
      ]);
    }
  };

  return (
    <Layout>
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-black dark:text-white">{t('welcome')}</h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              {health ? `${health.mode} Mode` : `${t('loadingText')}...`}
            </p>
          </div>
          <button
            onClick={createAgent}
            className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium flex items-center gap-2"
          >
            <i className="fa-solid fa-plus"></i>
            {t('newAgent')}
          </button>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Agents Grid */}
          <div className="lg:col-span-2 space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-black dark:text-white">{t('activeSwarm')}</h2>
              <div className="flex space-x-2">
                <button className="px-3 py-1 text-xs font-medium bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-300 dark:hover:bg-gray-700 transition-colors">
                  {t('filter')}
                </button>
                <button className="px-3 py-1 text-xs font-medium bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-300 dark:hover:bg-gray-700 transition-colors">
                  {t('sort')}
                </button>
              </div>
            </div>

            {loading ? (
              <div className="text-center py-8 text-gray-600 dark:text-gray-400">{t('loadingText')}...</div>
            ) : agents.length === 0 ? (
              <div className="text-center py-8 text-gray-600 dark:text-gray-400">
                {t('noAgents')}
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {agents.map((agent) => (
                  <AgentCard key={agent.id} agent={agent} />
                ))}
              </div>
            )}
          </div>

          {/* Terminal / Logs */}
          <div className="lg:col-span-1">
            <div className="glass-panel rounded-xl overflow-hidden flex flex-col h-[500px]">
              <div className="bg-gray-100 dark:bg-gray-900 px-4 py-3 border-b border-gray-300 dark:border-gray-700 flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <i className="fa-solid fa-terminal text-gray-600 dark:text-gray-400 text-sm"></i>
                  <span className="text-sm font-mono text-gray-700 dark:text-gray-300">{t('systemLogs')}</span>
                </div>
                <div className="flex space-x-1.5">
                  <div className="w-2.5 h-2.5 rounded-full bg-red-500/50"></div>
                  <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/50"></div>
                  <div className="w-2.5 h-2.5 rounded-full bg-green-500/50"></div>
                </div>
              </div>
              <div className="flex-1 bg-white dark:bg-black p-4 font-mono text-xs overflow-y-auto space-y-2">
                {logs.length === 0 ? (
                  <div className="text-gray-400 dark:text-gray-600 text-center py-8">{t('noLogs')}</div>
                ) : (
                  logs.map((log) => (
                    <div key={log.id} className="flex space-x-2">
                      <span className="text-gray-500 dark:text-gray-600">{log.time}</span>
                      <span
                        className={
                          log.type === 'info'
                            ? 'text-blue-600 dark:text-blue-400'
                            : log.type === 'success'
                            ? 'text-green-600 dark:text-green-400'
                            : log.type === 'warning'
                            ? 'text-yellow-600 dark:text-yellow-400'
                            : 'text-red-600 dark:text-red-400'
                        }
                      >
                        {log.message}
                      </span>
                    </div>
                  ))
                )}
                <div className="animate-pulse text-primary-400">_</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
