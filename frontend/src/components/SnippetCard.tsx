import React from 'react';
import { Link } from 'react-router-dom';
import { Code2, ArrowRight } from 'lucide-react';
import type { Snippet } from '../types';

interface SnippetCardProps {
  snippet: Snippet;
}

export const SnippetCard: React.FC<SnippetCardProps> = ({ snippet }) => {
  return (
    <div className="bg-white dark:bg-dark-surface rounded-2xl p-6 hover:shadow-xl hover:-translate-y-1 transition-all duration-300 border border-gray-100 dark:border-dark-border group">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-primary-50 dark:bg-primary-900/20 rounded-xl group-hover:scale-110 transition-transform duration-300">
            <Code2 className="w-6 h-6 text-primary-600 dark:text-primary-400" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-gray-900 dark:text-white group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">{snippet.title}</h3>
            <span className="text-sm font-medium text-gray-500 dark:text-gray-400">
              {typeof snippet.language === 'object' ? snippet.language?.name : snippet.language}
            </span>
          </div>
        </div>
      </div>

      <div className="bg-gray-50 dark:bg-[#0f0f11] rounded-xl p-4 mb-4 font-mono text-sm text-gray-600 dark:text-gray-300 overflow-hidden h-32 relative border border-gray-100 dark:border-dark-border">
        <pre>{snippet.code}</pre>
        <div className="absolute bottom-0 left-0 right-0 h-16 bg-gradient-to-t from-gray-50 dark:from-[#0f0f11] to-transparent" />
      </div>

      <Link
        to={`/snippets/${snippet.id}`}
        className="inline-flex items-center text-sm font-semibold text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 transition-colors"
      >
        View Details <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
      </Link>
    </div>
  );
};
