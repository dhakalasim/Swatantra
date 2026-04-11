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
        <div className="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white font-sans antialiased h-screen overflow-hidden flex transition-colors duration-300">
          {/* Animated background elements */}
          <div className="absolute inset-0 pointer-events-none">
            <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl animate-blob"></div>
            <div className="absolute top-1/3 right-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-blob animation-delay-2000"></div>
            <div className="absolute bottom-0 left-1/2 w-96 h-96 bg-cyan-500/20 rounded-full blur-3xl animate-blob animation-delay-4000"></div>
          </div>

          <style>{`
            ::-webkit-scrollbar {
              width: 8px;
              height: 8px;
            }
            ::-webkit-scrollbar-track {
              background: rgba(30, 41, 59, 0.5);
            }
            ::-webkit-scrollbar-thumb {
              background: linear-gradient(to bottom, #3b82f6, #8b5cf6);
              border-radius: 4px;
            }
            ::-webkit-scrollbar-thumb:hover {
              background: linear-gradient(to bottom, #60a5fa, #a78bfa);
            }
            
            .glass-panel {
              background: rgba(15, 23, 42, 0.6);
              backdrop-filter: blur(10px);
              border: 1px solid rgba(59, 130, 246, 0.2);
            }

            .glass-panel:hover {
              border-color: rgba(168, 85, 247, 0.3);
            }
            
            .gradient-text {
              background: linear-gradient(135deg, #3b82f6, #8b5cf6, #06b6d4);
              -webkit-background-clip: text;
              -webkit-text-fill-color: transparent;
              background-clip: text;
            }

            @keyframes blob {
              0%, 100% { transform: translate(0, 0) scale(1); }
              33% { transform: translate(30px, -50px) scale(1.1); }
              66% { transform: translate(-20px, 20px) scale(0.9); }
            }

            .animate-blob {
              animation: blob 7s infinite;
            }

            .animation-delay-2000 {
              animation-delay: 2s;
            }

            .animation-delay-4000 {
              animation-delay: 4s;
            }

            .agent-card {
              background: linear-gradient(135deg, rgba(30, 58, 138, 0.3) 0%, rgba(88, 28, 135, 0.2) 100%);
              border: 1px solid rgba(59, 130, 246, 0.3);
              transition: all 0.3s ease;
            }

            .agent-card:hover {
              border-color: rgba(168, 85, 247, 0.5);
              background: linear-gradient(135deg, rgba(30, 58, 138, 0.5) 0%, rgba(88, 28, 135, 0.4) 100%);
              box-shadow: 0 0 30px rgba(139, 92, 246, 0.3), inset 0 0 20px rgba(59, 130, 246, 0.1);
            }

            .neon-button {
              background: linear-gradient(135deg, #3b82f6, #8b5cf6);
              border: none;
              box-shadow: 0 0 20px rgba(59, 130, 246, 0.5);
              transition: all 0.3s ease;
            }

            .neon-button:hover {
              box-shadow: 0 0 40px rgba(139, 92, 246, 0.8);
              transform: translateY(-2px);
            }

            .terminal-text {
              text-shadow: 0 0 10px rgba(34, 197, 94, 0.6);
            }
          `}</style>
          
          <Sidebar />
          <main className="flex-1 overflow-auto relative z-10">
            {children}
          </main>
        </div>
      </LanguageProvider>
    </DarkModeProvider>
  );
}
