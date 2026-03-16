'use client';

import { Task } from '@/types';
import { useLanguage } from '@/lib/LanguageContext';

interface TaskCardProps {
  task: Task;
  onExecute?: (id: number) => void;
  onCancel?: (id: number) => void;
}

export default function TaskCard({ task, onExecute, onCancel }: TaskCardProps) {
  const { t } = useLanguage();
  const statusColors = {
    pending: { bg: 'bg-gray-500/10', text: 'text-gray-400' },
    running: { bg: 'bg-blue-500/10', text: 'text-blue-400' },
    completed: { bg: 'bg-green-500/10', text: 'text-green-400' },
    failed: { bg: 'bg-red-500/10', text: 'text-red-400' },
  };

  const colors = statusColors[task.status] || statusColors.pending;
  const priorityColor =
    task.priority >= 8 ? 'text-red-400' : task.priority >= 5 ? 'text-yellow-400' : 'text-green-400';

  return (
    <div className="bg-gray-50 dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded-lg p-4 hover:dark:border-primary-500 hover:border-primary-400 transition-all">
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <h3 className="font-medium text-black dark:text-white text-lg">{task.title}</h3>
          <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">{task.objective}</p>
        </div>
        <div className={`px-2 py-1 rounded text-xs font-medium ${colors.bg} ${colors.text}`}>
          {task.status}
        </div>
      </div>

      <div className="flex items-center justify-between text-xs text-gray-600 dark:text-gray-400 mb-3">
        <s{t('priority')}:{' '}
          <span className={`font-semibold ${priorityColor}`}>
            {task.priority}/10
          </span>
        </span>
        {task.execution_time_seconds && (
          <span>{t('time')}tion_time_seconds && (
          <span>समय: {task.execution_time_seconds}s</span>
        )}
      </div>

      {task.result && (
        <div className="mb-3 p-2 bg-gray-200 dark:bg-gray-800 rounded text-xs text-gray-800 dark:text-gray-300 max-h-20 overflow-y-auto">
          {typeof task.result === 'string' ? task.result : JSON.stringify(task.result, null, 2)}
        </div>
      )}

      {task.error_message && (
        <div className="mb-3 p-2 bg-red-100 dark:bg-red-900/20 rounded text-xs text-red-700 dark:text-red-400">
          {task.error_message}
        </div>
      )}

      <div className="flex gap-2">
        {task.status === 'pending' && onExecute && (
          <button
            onClick={() => onExecute(task.id)}
            className="flex-1 px-3 py-1 text-xs font-medium bg-primary-600 text-white rounded hover:bg-primary-700 transition-colors"
          >
            {t('run')}
          </button>
        )}
        {task.status === 'running' && onCancel && (
          <button
            onClick={() => onCancel(task.id)}
            className="flex-1 px-3 py-1 text-xs font-medium bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
          >
            {t('cancel')}
          </button>
        )}
      </div>
    </div>
  );
}
