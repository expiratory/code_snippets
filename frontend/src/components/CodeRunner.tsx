import { useState, useEffect, useRef } from 'react';
import Editor from '@monaco-editor/react';
import { Play, Terminal, Loader2 } from 'lucide-react';
import { useTranslation } from 'react-i18next';

const LANGUAGES = [
  { id: 'python', name: 'Python', defaultCode: 'print("Hello, World!")' },
  { id: 'javascript', name: 'JavaScript', defaultCode: 'console.log("Hello, World!");' },
  { id: 'java', name: 'Java', defaultCode: 'public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello, World!");\n    }\n}' },
  { id: 'go', name: 'Go', defaultCode: 'package main\n\nimport "fmt"\n\nfunc main() {\n    fmt.Println("Hello, World!")\n}' },
];

import { useLocation } from 'react-router-dom';

export function CodeRunner() {
  const { t } = useTranslation();
  const location = useLocation();
  const initialState = location.state as { code?: string; language?: string } | null;

  const [language, setLanguage] = useState(() => {
    if (initialState?.language) {
      const lang = LANGUAGES.find(l => l.name.toLowerCase() === initialState.language?.toLowerCase());
      if (lang) return lang;
    }
    return LANGUAGES[0];
  });

  const [code, setCode] = useState(initialState?.code || LANGUAGES[0].defaultCode);
  const [output, setOutput] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Connect to WebSocket
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.hostname}:8000/code/ws/run`;

    const connect = () => {
        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            console.log('Connected to Code Runner WebSocket');
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.error) {
                setOutput(prev => prev + `Error: ${data.error}\n`);
            } else {
                let result = '';
                if (data.stdout) result += data.stdout;
                if (data.stderr) result += `Error:\n${data.stderr}`;
                if (data.exit_code !== undefined && data.exit_code !== 0) {
                    result += `\nProcess exited with code ${data.exit_code}`;
                }
                setOutput(result);
            }
            setIsRunning(false);
        };

        ws.onclose = () => {
            console.log('Disconnected from Code Runner WebSocket');
            // Optional: Reconnect logic
        };

        wsRef.current = ws;
    };

    connect();

    return () => {
        if (wsRef.current) {
            wsRef.current.close();
        }
    };
  }, []);

  const handleLanguageChange = (langId: string) => {
    const lang = LANGUAGES.find(l => l.id === langId);
    if (lang) {
      setLanguage(lang);
      setCode(lang.defaultCode);
    }
  };

  const handleRun = () => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
        setOutput(t('runner.connection_lost'));
        // Reconnect logic could be triggered here or handled by the effect
        return;
    }

    setIsRunning(true);
    setOutput(t('runner.running') + '\n');

    wsRef.current.send(JSON.stringify({
        code: code,
        language: language.id
    }));
  };

  return (
    <div className="container mx-auto px-4 py-8 h-[calc(100vh-64px)] flex flex-col">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
          <Terminal className="w-6 h-6" />
          {t('runner.title')}
        </h1>
        <div className="flex items-center gap-4">
          <select
            value={language.id}
            onChange={(e) => handleLanguageChange(e.target.value)}
            className="block w-40 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white p-2"
          >
            {LANGUAGES.map((lang) => (
              <option key={lang.id} value={lang.id}>
                {lang.name}
              </option>
            ))}
          </select>
          <button
            onClick={handleRun}
            disabled={isRunning}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isRunning ? (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Play className="w-4 h-4 mr-2" />
            )}
            {t('runner.run')}
          </button>
        </div>
      </div>

      <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-4 min-h-0">
        <div className="border rounded-lg overflow-hidden shadow-sm bg-white dark:bg-gray-800 flex flex-col">
            <div className="bg-gray-50 dark:bg-gray-700 px-4 py-2 border-b dark:border-gray-600 text-sm font-medium text-gray-500 dark:text-gray-300">
                {t('runner.editor')}
            </div>
            <div className="flex-1">
                <Editor
                    height="100%"
                    language={language.id === 'c++' ? 'cpp' : language.id}
                    value={code}
                    onChange={(value) => setCode(value || '')}
                    theme="vs-dark"
                    options={{
                        minimap: { enabled: false },
                        fontSize: 14,
                        scrollBeyondLastLine: false,
                    }}
                />
            </div>
        </div>

        <div className="border rounded-lg overflow-hidden shadow-sm bg-white dark:bg-gray-800 flex flex-col">
            <div className="bg-gray-50 dark:bg-gray-700 px-4 py-2 border-b dark:border-gray-600 text-sm font-medium text-gray-500 dark:text-gray-300">
                {t('runner.output')}
            </div>
            <pre className="flex-1 p-4 bg-gray-900 text-green-400 font-mono text-sm overflow-auto whitespace-pre-wrap">
                {output || t('runner.output_placeholder')}
            </pre>
        </div>
      </div>
    </div>
  );
}
