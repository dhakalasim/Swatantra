'use client';

import { ReactNode } from 'react';
import { DarkModeProvider } from '@/lib/DarkModeContext';
import { LanguageProvider } from '@/lib/LanguageContext';
import Sidebar from './Sidebar';

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  return (
    <DarkModeProvider>
      <LanguageProvider>
        <div className="bg-white dark:bg-black text-black dark:text-white font-sans antialiased h-screen overflow-hidden flex transition-colors duration-300">
          <style>{`
            ::-webkit-scrollbar {
              width: 8px;
              height: 8px;
            }
            ::-webkit-scrollbar-track {
              background: #f5f5f5; 
            }
            ::-webkit-scrollbar-thumb {
              background: #d1d5db; 
              border-radius: 4px;
            }
            ::-webkit-scrollbar-thumb:hover {
              background: #9ca3af; 
            }

            .dark ::-webkit-scrollbar-track {
              background: #1f2937; 
            }

            .dark ::-webkit-scrollbar-thumb {
              background: #4b5563; 
              border-radius: 4px;
            }

            .dark ::-webkit-scrollbar-thumb:hover {
              background: #6b7280; 
            }
            
            .glass-panel {
              background: rgba(243, 244, 246, 0.7);
              backdrop-filter: blur(10px);
              border: 1px solid rgba(209, 213, 219, 0.4);
            }

            .dark .glass-panel {
              background: rgba(31, 41, 55, 0.7);
              backdrop-filter: blur(10px);
              border: 1px solid rgba(75, 85, 99, 0.4);
            }
            
            .terminal-text {
              text-shadow: 0 0 2px rgba(16, 185, 129, 0.5);
            }

            .agent-card:hover {
              border-color: #6366f1;
              box-shadow: 0 0 15px rgba(99, 102, 241, 0.2);
            }
          `}</style>
          <Sidebar />
          <main className="flex-1 overflow-auto">
            {children}
          </main>
        </div>
      </LanguageProvider>
    </DarkModeProvider>
  );
}
