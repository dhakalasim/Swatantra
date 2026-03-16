'use client';

import Layout from '@/components/Layout';
import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/apiClient';
import { useLanguage } from '@/lib/LanguageContext';

export default function AnalyticsPage() {
  const { t } = useLanguage();
  const [analytics, setAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const data = await apiClient.getAnalyticsSummary();
      setAnalytics(data);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="p-6 space-y-6">
        <h1 className="text-3xl font-bold text-black dark:text-white">{t('analytics')}</h1>

        {loading ? (
          <div className="text-center py-8 text-gray-400">{t('loadingText')}...</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded-lg p-6">
              <div className="text-gray-600 dark:text-gray-400 text-sm">Total Agents</div>
              <div className="text-3xl font-bold text-black dark:text-white mt-2">
                {analytics?.total_agents || 0}
              </div>
            </div>
            <div className="bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded-lg p-6">
              <div className="text-gray-600 dark:text-gray-400 text-sm">Active Tasks</div>
              <div className="text-3xl font-bold text-blue-600 dark:text-blue-400 mt-2">
                {analytics?.active_tasks || 0}
              </div>
            </div>
            <div className="bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded-lg p-6">
              <div className="text-gray-600 dark:text-gray-400 text-sm">Completed Tasks</div>
              <div className="text-3xl font-bold text-green-600 dark:text-green-400 mt-2">
                {analytics?.completed_tasks || 0}
              </div>
            </div>
            <div className="bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded-lg p-6">
              <div className="text-gray-600 dark:text-gray-400 text-sm">Average Time</div>
              <div className="text-3xl font-bold text-yellow-600 dark:text-yellow-400 mt-2">
                {analytics?.avg_execution_time || 0}s
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}
