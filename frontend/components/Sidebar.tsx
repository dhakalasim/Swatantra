'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useDarkMode } from '@/lib/DarkModeContext';
import { useLanguage } from '@/lib/LanguageContext';
import { Language } from '@/lib/translations';

export default function Sidebar() {
  const pathname = usePathname();
  const { isDarkMode, toggleDarkMode } = useDarkMode();
  const { language, setLanguage, t } = useLanguage();

  const isActive = (path: string) => pathname === path;

  const navItems = [
    { href: '/', label: t('dashboard'), icon: 'fa-grid-2' },
    { href: '/agents', label: t('myAgents'), icon: 'fa-robot' },
    { href: '/tasks', label: t('tasks'), icon: 'fa-list-check' },
    { href: '/analytics', label: t('analytics'), icon: 'fa-chart-line' },
    { href: '/settings', label: t('settings'), icon: 'fa-gear' },
  ];

  return (
    <aside className="w-64 dark:bg-gray-900 bg-gray-50 dark:border-gray-800 border-gray-200 border-r flex flex-col transition-all duration-300 hidden md:flex">
      <div className="h-16 flex items-center px-6 dark:border-gray-800 border-gray-200 border-b">
        <span className="text-xl font-bold tracking-tight dark:text-white text-gray-900">
          स्वतन्त्र<span className="text-primary-400">AI</span>
        </span>
      </div>

      <nav className="flex-1 px-4 py-6 space-y-1">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={`group flex items-center px-3 py-2.5 text-sm font-medium rounded-r-md transition-colors border-l-4 ${
              isActive(item.href)
                ? 'dark:bg-gray-800 dark:text-white bg-gray-200 text-gray-900 border-l-4 border-primary-500'
                : 'dark:text-gray-400 dark:hover:bg-gray-800 dark:hover:text-white text-gray-600 hover:bg-gray-100 hover:text-gray-900 border-l-4 border-transparent'
            }`}
          >
            <i className={`fa-solid ${item.icon} w-6 text-center mr-2`}></i>
            {item.label}
          </Link>
        ))}
      </nav>

      <div className="p-4 dark:border-gray-800 border-gray-200 border-t space-y-4">
        {/* Language Selector */}
        <div className="space-y-2">
          <p className="text-xs font-semibold text-gray-700 dark:text-gray-400 px-3">LANGUAGE</p>
          <div className="flex gap-2">
            <button
              onClick={() => setLanguage('ne' as Language)}
              className={`flex-1 px-2 py-1.5 text-xs font-semibold rounded transition-colors ${
                language === 'ne'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-400 hover:bg-gray-300 dark:hover:bg-gray-700'
              }`}
            >
              नेपाली
            </button>
            <button
              onClick={() => setLanguage('en' as Language)}
              className={`flex-1 px-2 py-1.5 text-xs font-semibold rounded transition-colors ${
                language === 'en'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-400 hover:bg-gray-300 dark:hover:bg-gray-700'
              }`}
            >
              English
            </button>
            <button
              onClick={() => setLanguage('hi' as Language)}
              className={`flex-1 px-2 py-1.5 text-xs font-semibold rounded transition-colors ${
                language === 'hi'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-400 hover:bg-gray-300 dark:hover:bg-gray-700'
              }`}
            >
              हिंदी
            </button>
          </div>
        </div>

        {/* Dark Mode Toggle */}
        <button
          onClick={toggleDarkMode}
          className="w-full flex items-center justify-between px-3 py-2 rounded-lg dark:bg-gray-800 dark:hover:bg-gray-700 bg-gray-200 hover:bg-gray-300 transition-colors text-sm"
        >
          <span className="dark:text-gray-300 text-gray-700">
            {isDarkMode ? '🌙 ' + t('darkMode') : '☀️ ' + t('lightMode')}
          </span>
          <div className={`relative w-10 h-6 rounded-full transition-colors ${isDarkMode ? 'bg-primary-600' : 'bg-gray-400'}`}>
            <div
              className={`absolute top-1 left-1 w-4 h-4 rounded-full bg-white transition-transform ${isDarkMode ? 'translate-x-4' : ''}`}
            ></div>
          </div>
        </button>

        {/* User Profile */}
        <div className="flex items-center space-x-3">
          <img
            className="h-10 w-10 rounded-full border dark:border-gray-600 border-gray-300"
            src="https://ui-avatars.com/api/?name=Admin+User&background=4f46e5&color=fff"
            alt="User"
          />
          <div className="hidden sm:block">
            <p className="text-sm font-medium dark:text-white text-gray-900">Admin User</p>
            <p className="text-xs dark:text-gray-400 text-gray-500">{t('admin')}</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
