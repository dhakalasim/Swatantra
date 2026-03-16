'use client';

import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import TaskCard from '@/components/TaskCard';
import { apiClient } from '@/lib/apiClient';
import { useLanguage } from '@/lib/LanguageContext';
import { Task } from '@/types';

export default function TasksPage() {
  const { t } = useLanguage();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState<string | null>(null);

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      const data = await apiClient.getTasks();
      setTasks(data || []);
    } catch (error) {
      console.error('Error fetching tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredTasks = filterStatus
    ? tasks.filter((task) => task.status === filterStatus)
    : tasks;

  const handleExecute = async (taskId: number) => {
    try {
      await apiClient.executeTask(taskId);
      fetchTasks();
    } catch (error) {
      console.error('Error executing task:', error);
    }
  };

  const handleCancel = async (taskId: number) => {
    try {
      await apiClient.cancelTask(taskId);
      fetchTasks();
    } catch (error) {
      console.error('Error canceling task:', error);
    }
  };

  return (
    <Layout>
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold text-black dark:text-white">{t('tasks')}</h1>
          <button className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium">
            <i className="fa-solid fa-plus mr-2"></i>
            {t('newTask')}
          </button>
        </div>

        {/* Filters */}
        <div className="flex gap-2 overflow-x-auto">
          <button
            onClick={() => setFilterStatus(null)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors whitespace-nowrap ${
              filterStatus === null
                ? 'bg-primary-600 text-white'
                : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
            }`}
          >
            {t('all')}
          </button>
          <button
            onClick={() => setFilterStatus('pending')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors whitespace-nowrap ${
              filterStatus === 'pending'
                ? 'bg-gray-600 text-white'
                : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
            }`}
          >
            {t('pending')}
          </button>
          <button
            onClick={() => setFilterStatus('running')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors whitespace-nowrap ${
              filterStatus === 'running'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
            }`}
          >
            {t('running')}
          </button>
          <button
            onClick={() => setFilterStatus('completed')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors whitespace-nowrap ${
              filterStatus === 'completed'
                ? 'bg-green-600 text-white'
                : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
            }`}
          >
            {t('completed')}
          </button>
          <button
            onClick={() => setFilterStatus('failed')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors whitespace-nowrap ${
              filterStatus === 'failed'
                ? 'bg-red-600 text-white'
                : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
            }`}
          >
            {t('failed')}
          </button>
        </div>

        {/* Tasks List */}
        {loading ? (
          <div className="text-center py-8 text-gray-400">{t('loadingText')}...</div>
        ) : filteredTasks.length === 0 ? (
          <div className="text-center py-8 text-gray-400">No tasks found.</div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {filteredTasks.map((task) => (
              <TaskCard
                key={task.id}
                task={task}
                onExecute={handleExecute}
                onCancel={handleCancel}
              />
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
}
