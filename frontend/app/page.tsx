'use client';

import { useState, useEffect, useRef, KeyboardEvent } from 'react';
import Layout from '@/components/Layout';
import { apiClient } from '@/lib/apiClient';
import { useLanguage } from '@/lib/LanguageContext';
import { Language } from '@/lib/translations';
import { Agent, Task } from '@/types';

const ASSISTANT_NAME = 'Swatantra Assistant';
const ALL_TOOLS = [
  'read_file',
  'write_file',
  'execute_code',
  'http_request',
  'get_time',
  'analyze_data',
  'document_processor',
  'web_search',
];

const TOOL_INFO: Record<string, { icon: string; en: string; ne: string; hi: string }> = {
  web_search: { icon: '🔍', en: 'Searched the web', ne: 'वेबमा खोजियो', hi: 'वेब पर खोजा गया' },
  get_time: { icon: '🕒', en: 'Checked the time', ne: 'समय जाँचियो', hi: 'समय जांचा गया' },
  document_processor: { icon: '📄', en: 'Summarized the text', ne: 'पाठको सारांश बनाइयो', hi: 'पाठ का सारांश बनाया गया' },
  analyze_data: { icon: '📊', en: 'Analyzed the data', ne: 'डाटा विश्लेषण गरियो', hi: 'डेटा का विश्लेषण किया गया' },
  execute_code: { icon: '💻', en: 'Ran the code', ne: 'कोड चलाइयो', hi: 'कोड चलाया गया' },
  read_file: { icon: '📂', en: 'Read the file', ne: 'फाइल पढियो', hi: 'फ़ाइल पढ़ी गई' },
  write_file: { icon: '💾', en: 'Saved the file', ne: 'फाइल सुरक्षित गरियो', hi: 'फ़ाइल सहेजी गई' },
  http_request: { icon: '🌐', en: 'Called the API', ne: 'एपिआई कल गरियो', hi: 'एपीआई कॉल किया गया' },
};

interface Example {
  icon: string;
  label: Record<Language, string>;
  objective: Record<Language, string>;
  toolOverride: string;
  extraInput?: Record<string, any>;
}

const EXAMPLES: Example[] = [
  {
    icon: '🔍',
    label: { en: 'Search Mount Everest', ne: 'सगरमाथाबारे खोज्नुहोस्', hi: 'माउंट एवरेस्ट खोजें' },
    objective: {
      en: 'Search: Mount Everest',
      ne: 'खोज्नुहोस्: सगरमाथा',
      hi: 'खोजें: माउंट एवरेस्ट',
    },
    toolOverride: 'web_search',
    extraInput: { query: 'Mount Everest' },
  },
  {
    icon: '🕒',
    label: { en: 'What time is it?', ne: 'अहिले कति बजे?', hi: 'अभी समय क्या है?' },
    objective: {
      en: 'What time is it right now?',
      ne: 'अहिले कति बजे भयो?',
      hi: 'अभी समय क्या हुआ है?',
    },
    toolOverride: 'get_time',
  },
  {
    icon: '📄',
    label: { en: 'Summarize a paragraph', ne: 'अनुच्छेदको सारांश', hi: 'पैराग्राफ़ का सारांश' },
    objective: {
      en: 'Summarize: Nepal is a landlocked country in South Asia, home to the Himalayas and Mount Everest.',
      ne: 'सारांश: नेपाल दक्षिण एसियाको एउटा भूपरिवेष्ठित देश हो, जहाँ हिमालय र सगरमाथा छन्।',
      hi: 'सारांश: नेपाल दक्षिण एशिया का एक स्थलरुद्ध देश है, जहाँ हिमालय और माउंट एवरेस्ट हैं।',
    },
    toolOverride: 'document_processor',
    extraInput: {
      document_text: 'Nepal is a landlocked country in South Asia, home to the Himalayas and Mount Everest.',
      action: 'summarize',
    },
  },
  {
    icon: '💻',
    label: { en: 'Run a bit of code', ne: 'सानो कोड चलाउनुहोस्', hi: 'थोड़ा कोड चलाएं' },
    objective: {
      en: 'Code: result = 5 * 7',
      ne: 'कोड: result = 5 * 7',
      hi: 'कोड: result = 5 * 7',
    },
    toolOverride: 'execute_code',
    extraInput: { code: 'result = 5 * 7', language: 'python' },
  },
];

// Lightweight parser: recognizes a few English prefixes so free typing can
// still drive tools that need structured input (not just search/time).
function parseObjective(text: string): Record<string, any> {
  const lower = text.toLowerCase();

  const stripPrefix = (prefixes: string[]): string | null => {
    for (const p of prefixes) {
      if (lower.startsWith(p)) return text.slice(p.length).trim();
    }
    return null;
  };

  let payload = stripPrefix(['summarize:', 'summarise:']);
  if (payload !== null) return { tool: 'document_processor', document_text: payload, action: 'summarize' };

  payload = stripPrefix(['analyze:', 'analyse:']);
  if (payload !== null) {
    let data_type = 'text';
    try {
      JSON.parse(payload);
      data_type = 'json';
    } catch {
      if (payload.includes(',') && payload.includes('\n')) data_type = 'csv';
    }
    return { tool: 'analyze_data', data: payload, data_type };
  }

  payload = stripPrefix(['run code:', 'code:']);
  if (payload !== null) return { tool: 'execute_code', code: payload, language: 'python' };

  payload = stripPrefix(['read file:']);
  if (payload !== null) return { tool: 'read_file', file_path: payload };

  payload = stripPrefix(['write file:']);
  if (payload !== null) {
    const [firstLine, ...rest] = payload.split('\n');
    const pipeIdx = firstLine.indexOf('|');
    if (pipeIdx >= 0) {
      return {
        tool: 'write_file',
        file_path: firstLine.slice(0, pipeIdx).trim(),
        content: firstLine.slice(pipeIdx + 1).trim() || rest.join('\n').trim(),
      };
    }
    return { tool: 'write_file', file_path: firstLine.trim(), content: rest.join('\n').trim() };
  }

  payload = stripPrefix(['search:', 'search for']);
  if (payload !== null) return { tool: 'web_search', query: payload };

  const urlMatch = text.match(/https?:\/\/\S+/);
  if (urlMatch && (lower.includes('http') || lower.includes('api') || lower.includes('fetch'))) {
    return { tool: 'http_request', url: urlMatch[0] };
  }

  return {};
}

function AskContent() {
  const { t, language } = useLanguage();
  const [inputText, setInputText] = useState('');
  const [running, setRunning] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [history, setHistory] = useState<Task[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [selectedExample, setSelectedExample] = useState<Example | null>(null);
  const [expandedTaskIds, setExpandedTaskIds] = useState<Set<number>>(new Set());
  const agentRef = useRef<Agent | null>(null);

  const toggleReasoning = (taskId: number) => {
    setExpandedTaskIds((prev) => {
      const next = new Set(prev);
      if (next.has(taskId)) next.delete(taskId);
      else next.add(taskId);
      return next;
    });
  };

  useEffect(() => {
    apiClient
      .getTasks()
      .then((tasks) => setHistory((tasks || []).sort((a, b) => b.id - a.id)))
      .catch(() => setHistory([]))
      .finally(() => setLoadingHistory(false));
  }, []);

  const getOrCreateAssistant = async (): Promise<Agent> => {
    if (agentRef.current) return agentRef.current;
    const agents = await apiClient.getAgents();
    let assistant = agents.find((a) => a.name === ASSISTANT_NAME);
    if (!assistant) {
      assistant = await apiClient.createAgent({
        name: ASSISTANT_NAME,
        description: 'Your all-purpose Swatantra assistant',
        agent_type: 'execution',
        tools: ALL_TOOLS.map((name) => ({ name, enabled: true })),
      } as Omit<Agent, 'id'>);
    }
    agentRef.current = assistant;
    return assistant;
  };

  const handleExampleClick = (example: Example) => {
    setSelectedExample(example);
    setInputText(example.objective[language]);
  };

  const handleTextChange = (value: string) => {
    setInputText(value);
    if (selectedExample && value !== selectedExample.objective[language]) {
      setSelectedExample(null);
    }
  };

  const handleRun = async () => {
    const text = inputText.trim();
    if (!text || running) return;

    setRunning(true);
    setErrorMsg(null);

    try {
      const assistant = await getOrCreateAssistant();

      const input_data =
        selectedExample && selectedExample.objective[language] === text
          ? { tool: selectedExample.toolOverride, ...selectedExample.extraInput }
          : parseObjective(text);

      const task = await apiClient.createTask({
        agent_id: assistant.id,
        title: text.slice(0, 80),
        objective: text,
        input_data,
      } as Omit<Task, 'id'>);

      const executed = await apiClient.executeTask(task.id);
      setHistory((prev) => [executed, ...prev]);
      setInputText('');
      setSelectedExample(null);
    } catch (e) {
      console.error('Error running task:', e);
      setErrorMsg(
        language === 'ne'
          ? 'केही गडबड भयो। फेरि प्रयास गर्नुहोस्।'
          : language === 'hi'
          ? 'कुछ गड़बड़ हुई। फिर से कोशिश करें।'
          : 'Something went wrong. Please try again.'
      );
    } finally {
      setRunning(false);
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleRun();
    }
  };

  return (
    <div className="p-6 md:p-10 max-w-3xl mx-auto space-y-8">
      {/* Hero / description */}
      <div className="text-center space-y-3">
        <h1 className="text-4xl font-black gradient-text">{t('heroTitle')}</h1>
        <p className="text-slate-300 text-base leading-relaxed max-w-xl mx-auto">
          {t('heroDescription')}
        </p>
      </div>

      {/* Ask box */}
      <div className="glass-panel rounded-2xl p-5 space-y-4 border border-cyan-500/20">
        <textarea
          value={inputText}
          onChange={(e) => handleTextChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={t('askPlaceholder')}
          rows={3}
          className="w-full bg-white/5 border border-white/10 rounded-xl p-4 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 resize-none"
        />

        <div className="flex items-center justify-between gap-3">
          <p className="text-xs text-slate-500">{t('tipText')}</p>
          <button
            onClick={handleRun}
            disabled={running || !inputText.trim()}
            className="neon-button px-6 py-2.5 text-white rounded-xl font-semibold whitespace-nowrap disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {running ? t('workingText') : t('run')}
          </button>
        </div>

        {/* Example chips */}
        <div className="flex flex-wrap gap-2 pt-1">
          <span className="text-xs text-slate-500 self-center mr-1">{t('tryLabel')}:</span>
          {EXAMPLES.map((example, idx) => (
            <button
              key={idx}
              onClick={() => handleExampleClick(example)}
              className="px-3 py-1.5 text-xs font-medium bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 text-slate-300 rounded-lg transition-all"
            >
              {example.icon} {example.label[language]}
            </button>
          ))}
        </div>

        {errorMsg && (
          <div className="text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-4 py-2">
            {errorMsg}
          </div>
        )}
      </div>

      {/* Recent activity / results */}
      <div className="space-y-3">
        <h2 className="text-lg font-bold text-slate-300">{t('recentLabel')}</h2>

        {loadingHistory ? (
          <div className="text-center py-8 text-slate-500">{t('loadingText')}...</div>
        ) : history.length === 0 ? (
          <div className="text-center py-10 text-slate-500 glass-panel rounded-2xl">
            {t('noHistoryText')}
          </div>
        ) : (
          <div className="space-y-3">
            {history.map((task) => {
              const inner = (task.result as any) || {};
              const toolsUsed: string[] =
                inner.tools_used && inner.tools_used.length
                  ? inner.tools_used
                  : inner.tool_used
                  ? [inner.tool_used]
                  : [];
              const uniqueTools = Array.from(new Set(toolsUsed));
              const reasoningSteps: Array<{
                step_number: number;
                action_type: string;
                description: string;
                output?: { value: string };
              }> = inner.reasoning_steps || [];
              const engine = inner.engine as string | undefined;
              const failed = task.status === 'failed';
              const outputText = failed
                ? task.error_message || inner.error || '—'
                : typeof inner.result === 'string'
                ? inner.result
                : JSON.stringify(inner.result, null, 2);
              const isExpanded = expandedTaskIds.has(task.id);

              return (
                <div
                  key={task.id}
                  className={`glass-panel rounded-xl p-4 border ${
                    failed ? 'border-red-500/30' : 'border-white/10'
                  }`}
                >
                  <p className="text-sm font-semibold text-white mb-1">{task.objective}</p>
                  <p
                    className={`text-sm whitespace-pre-wrap break-words ${
                      failed ? 'text-red-400' : 'text-slate-300'
                    }`}
                  >
                    {outputText}
                  </p>

                  <div className="flex flex-wrap items-center gap-2 mt-2">
                    {uniqueTools.map((name) => {
                      const info = TOOL_INFO[name];
                      return (
                        <span key={name} className="text-xs text-slate-500">
                          {info ? `${info.icon} ${t('viaLabel')} ${info[language]}` : name}
                        </span>
                      );
                    })}
                  </div>

                  <div className="flex items-center justify-between mt-2">
                    {engine && (
                      <span className="text-[11px] text-slate-500">
                        {engine === 'claude' ? t('engineClaude') : t('engineRuleBased')}
                      </span>
                    )}
                    {reasoningSteps.length > 0 && (
                      <button
                        onClick={() => toggleReasoning(task.id)}
                        className="text-[11px] text-cyan-400 hover:text-cyan-300 transition-colors ml-auto"
                      >
                        {isExpanded ? t('hideReasoning') : t('showReasoning')}
                      </button>
                    )}
                  </div>

                  {isExpanded && reasoningSteps.length > 0 && (
                    <div className="mt-3 space-y-2 border-t border-white/10 pt-3">
                      {reasoningSteps.map((step, idx) => (
                        <div key={idx} className="text-xs text-slate-400 flex gap-2">
                          <span className="text-slate-600 shrink-0">
                            {step.action_type === 'tool_call'
                              ? '🔧'
                              : step.action_type === 'decision'
                              ? '🧭'
                              : '💭'}
                          </span>
                          <div className="min-w-0">
                            <p className="break-words whitespace-pre-wrap">{step.description}</p>
                            {step.output?.value && (
                              <p className="text-slate-600 break-words whitespace-pre-wrap mt-0.5">
                                → {step.output.value.slice(0, 300)}
                              </p>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

export default function HomePage() {
  return (
    <Layout>
      <AskContent />
    </Layout>
  );
}
