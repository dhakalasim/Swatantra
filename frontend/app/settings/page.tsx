'use client';

import Layout from '@/components/Layout';
import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/apiClient';
import { useLanguage } from '@/lib/LanguageContext';

function SettingsContent() {
  const { t } = useLanguage();
  const [config, setConfig] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    try {
      // Config endpoint not available, set default config
      setConfig({ theme: 'auto', language: 'en' });
    } catch (error) {
      console.error('Error fetching config:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-2xl">
        <h1 className="text-3xl font-bold text-black dark:text-white">{t('settings')}</h1>

        {loading ? (
          <div className="text-center py-8 text-gray-400">{t('loadingText')}...</div>
        ) : (
          <div className="space-y-6">
            {/* Mode Section */}
            <div className="bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded-lg p-6">
              <h2 className="text-lg font-semibold text-black dark:text-white mb-3">Operation Mode</h2>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-gray-700 dark:text-gray-300">Current Mode:</span>
                  <span className="text-primary-600 dark:text-primary-400 font-semibold">
                    {config?.mode === 'online' ? 'Online (Cloud)' : 'Offline (Local)'}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-700 dark:text-gray-300">Database:</span>
                  <span className="text-gray-600 dark:text-gray-400">{config?.database || 'SQLite/PostgreSQL'}</span>
                </div>
              </div>
            </div>

            {/* System Section */}
            <div className="bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded-lg p-6">
              <h2 className="text-lg font-semibold text-black dark:text-white mb-3">System</h2>
              <div className="space-y-3 text-sm">
                <div className="flex items-center justify-between">
                  <span className="text-gray-700 dark:text-gray-300">Version:</span>
                  <span className="text-gray-600 dark:text-gray-400">1.0.0</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-700 dark:text-gray-300">API Base URL:</span>
                  <span className="text-gray-600 dark:text-gray-400 break-all">
                    {process.env.NEXT_PUBLIC_API_BASE_URL}
                  </span>
                </div>
              </div>
            </div>

            {/* Sync Section */}
            <div className="bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded-lg p-6">
              <h2 className="text-lg font-semibold text-black dark:text-white mb-3">Synchronization</h2>
              <button
                onClick={async () => {
                  try {
                    await apiClient.syncNow();
                    alert('Sync successful.');
                  } catch (error) {
                    alert('Sync error.');
                  }
                }}
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
              >
                Sync Now
              </button>
            </div>

            {/* About Section */}
            <div className="bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded-lg p-6">
              <h2 className="text-lg font-semibold text-black dark:text-white mb-3">About</h2>
              <p className="text-gray-700 dark:text-gray-300 text-sm">
                Swatantra AI is a powerful agentic AI system that enables you to create and manage digital employees.
              </p>
            </div>
          </div>
        )}
      </div>
    );
}

export default function SettingsPage() {
  return (
    <Layout>
      <SettingsContent />
    </Layout>
  );
}
