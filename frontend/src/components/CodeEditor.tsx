import React, { useEffect } from 'react';
import Editor, { type OnMount } from '@monaco-editor/react';
import { useTheme } from '../context/ThemeContext';

interface CodeEditorProps {
  value: string;
  onChange?: (value: string | undefined) => void;
  language?: string;
  readOnly?: boolean;
  height?: string;
}

export const CodeEditor: React.FC<CodeEditorProps> = ({
  value,
  onChange,
  language = 'python',
  readOnly = false,
  height = '400px',
}) => {
  const { theme } = useTheme();
  const [monacoInstance, setMonacoInstance] = React.useState<any>(null);

  const handleEditorDidMount: OnMount = (_, monaco) => {
    setMonacoInstance(monaco);

    monaco.editor.defineTheme('custom-dark', {
      base: 'vs-dark',
      inherit: true,
      rules: [],
      colors: {
        'editor.background': '#0f0f11',
        'editor.lineHighlightBackground': '#18181b',
      },
    });

    monaco.editor.defineTheme('custom-light', {
      base: 'vs',
      inherit: true,
      rules: [],
      colors: {
        'editor.background': '#ffffff',
        'editor.lineHighlightBackground': '#f5f3ff',
      },
    });

    monaco.editor.setTheme(theme === 'dark' ? 'custom-dark' : 'custom-light');
  };

  useEffect(() => {
    if (monacoInstance) {
      monacoInstance.editor.setTheme(theme === 'dark' ? 'custom-dark' : 'custom-light');
    }
  }, [theme, monacoInstance]);

  return (
    <div className="rounded-xl overflow-hidden border border-gray-200 dark:border-dark-border">
      <Editor
        height={height}
        language={language.toLowerCase()}
        value={value}
        onChange={onChange}
        onMount={handleEditorDidMount}
        theme={theme === 'dark' ? 'custom-dark' : 'custom-light'}
        options={{
          readOnly,
          minimap: { enabled: false },
          scrollBeyondLastLine: false,
          fontSize: 14,
          fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
          padding: { top: 45, bottom: 32 },
          renderLineHighlight: 'all',
          smoothScrolling: true,
          cursorBlinking: 'smooth',
          cursorSmoothCaretAnimation: 'on',
          lineNumbers: 'on',
          roundedSelection: true,
        }}
      />
    </div>
  );
};
