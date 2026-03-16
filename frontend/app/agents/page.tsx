'use client';

import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import AgentCard from '@/components/AgentCard';
import { apiClient } from '@/lib/apiClient';
import { useLanguage } from '@/lib/LanguageContext';
import { Agent } from '@/types';

export default function AgentsPage() {
  const { t } = useLanguage();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState<string | null>(null);

  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    try {
      const data = await apiClient.getAgents();
      setAgents(data || []);
    } catch (error) {
      console.error('Error fetching agents:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredAgents = filterStatus
    ? agents.filter((agent) => agent.status === filterStatus)
    : agents;

  const handleActivate = async (agentId: number) => {
    try {
      await apiClient.activateAgent(agentId);
      fetchAgents();
    } catch (error) {
      console.error('Error activating agent:', error);
    }
  };

  const handleDeactivate = async (agentId: number) => {
    try {
      await apiClient.deactivateAgent(agentId);
      fetchAgents();
    } catch (error) {
      console.error('Error deactivating agent:', error);
    }
  };

  return (
    <Layout>
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-betw dark:text-white">{t('myAgents')}</h1>
          <button className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium">
            <i className="fa-solid fa-plus mr-2"></i>
            {t('newAgent')}e="fa-solid fa-plus mr-2"></i>
            नयाँ एजेन्ट
          </button>
        </div>

        {/* Filters */}
        <div className="flex gap-2">
          <button
            onClick={() => setFilterStatus(null)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filterStatus === null
                ? 'bg-primary-600 text-white'
                : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
            }`}
          >
            {t('all')}
          </button>
          <button
            onClick={() => setFilterStatus('Active')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filterStatus === 'Active'
                ? 'bg-green-600 text-white'
                : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
            }`}
          >
            {t('active')}
          </button>
          <button
            onClick={() => setFilterStatus('Idle')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filterStatus === 'Idle'
                ? 'bg-yellow-600 text-white'
                : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
            }`}
          >
            {t('idle')}
          </button>
          <button
            onClick={() => setFilterStatus('Error')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filterStatus === 'Error'
                ? 'bg-red-600 text-white'
                : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
            }`}
          >
            Error
          </button>
        </div>

        {/* Agents Grid */}
        {loading ? (
          <div className="text-center py-8 text-gray-400">{t('loadingText')}...</div>
        ) : filteredAgents.length === 0 ? (
          <div className="text-center py-8 text-gray-400">{t('noAgents')}</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredAgents.map((agent) => (
              <div key={agent.id} className="relative">
                <AgentCard agent={agent} />
                <div className="flex gap-2 mt-2">
                  {agent.status === 'Active' ? (
                    <button
                      onClick={() => handleDeactivate(agent.id)}
                      className="flex-1 px-3 py-1 text-xs font-medium bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
                    >
                      Deactivate
                    </button>
                  ) : (
                    <button
                      onClick={() => handleActivate(agent.id)}
                      className="flex-1 px-3 py-1 text-xs font-medium bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
                    >
                      Activate
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
}
