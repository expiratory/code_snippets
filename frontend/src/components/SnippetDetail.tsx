import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { Trash2, Copy, Check, Edit, Play } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import api from '../lib/api';
import type { Snippet } from '../types';
import { CodeEditor } from './CodeEditor';
import Modal from './Modal';

export const SnippetDetail: React.FC = () => {
  const { t } = useTranslation();
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [snippet, setSnippet] = useState<Snippet | null>(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);

  useEffect(() => {
    const fetchSnippet = async () => {
      try {
        const response = await api.get<Snippet>(`/snippets/${id}`);
        setSnippet(response.data);
      } catch (error) {
        console.error('Failed to fetch snippet:', error);
        navigate('/');
      } finally {
        setLoading(false);
      }
    };
    fetchSnippet();
  }, [id, navigate]);

  const handleDeleteClick = () => {
    setIsDeleteModalOpen(true);
  };

  const handleConfirmDelete = async () => {
    try {
      await api.delete(`/snippets/${id}`);
      navigate('/');
    } catch (error) {
      console.error('Failed to delete snippet:', error);
    }
  };

  const handleCopy = async () => {
    if (snippet) {
      await navigator.clipboard.writeText(snippet.code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (loading) return <div className="text-center text-gray-400 py-12">{t('loading')}</div>;
  if (!snippet) return null;

  return (
    <div className="max-w-4xl mx-auto px-4 py-6 sm:py-12">
      <div className="bg-white dark:bg-dark-surface rounded-2xl border border-gray-200 dark:border-dark-border overflow-hidden shadow-xl dark:shadow-none">
        <div className="p-4 sm:p-8 border-b border-gray-200 dark:border-dark-border flex flex-col sm:flex-row items-start justify-between bg-gray-50/50 dark:bg-transparent gap-4">
          <div className="flex-1 w-full">
            <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white mb-3">{snippet.title}</h1>
            <span className="inline-block bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 px-3 sm:px-4 py-1 sm:py-1.5 rounded-full text-xs sm:text-sm font-semibold">
              {typeof snippet.language === 'object' ? snippet.language?.name : snippet.language}
            </span>
            {snippet.tags && snippet.tags.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-3">
                {snippet.tags.map((tag) => (
                  <span
                    key={tag.id}
                    className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300"
                  >
                    {tag.name}
                  </span>
                ))}
              </div>
            )}
          </div>
          <div className="flex items-center gap-3 w-full sm:w-auto">
            <button
              onClick={handleCopy}
              className="flex-1 sm:flex-none p-2.5 text-gray-500 hover:text-primary-600 hover:bg-primary-50 dark:text-gray-400 dark:hover:text-white dark:hover:bg-gray-800 rounded-xl transition-all flex items-center justify-center"
              title={t('snippets.detail.copy')}
            >
              {copied ? <Check className="w-5 h-5 text-green-500" /> : <Copy className="w-5 h-5" />}
            </button>
            <button
              onClick={() => navigate('/run', {
                state: {
                  code: snippet.code,
                  language: typeof snippet.language === 'object' ? snippet.language?.name : snippet.language
                }
              })}
              className="flex-1 sm:flex-none p-2.5 text-gray-500 hover:text-primary-600 hover:bg-primary-50 dark:text-gray-400 dark:hover:text-white dark:hover:bg-gray-800 rounded-xl transition-all flex items-center justify-center"
              title={t('snippets.detail.run')}
            >
              <Play className="w-5 h-5" />
            </button>
            <Link
              to={`/snippets/${id}/edit`}
              className="flex-1 sm:flex-none p-2.5 text-gray-500 hover:text-primary-600 hover:bg-primary-50 dark:text-gray-400 dark:hover:text-white dark:hover:bg-gray-800 rounded-xl transition-all flex items-center justify-center"
              title={t('snippets.detail.edit')}
            >
              <Edit className="w-5 h-5" />
            </Link>
            <button
              onClick={handleDeleteClick}
              className="flex-1 sm:flex-none p-2.5 text-gray-500 hover:text-red-600 hover:bg-red-50 dark:text-gray-400 dark:hover:text-red-400 dark:hover:bg-red-500/10 rounded-xl transition-all flex items-center justify-center"
              title={t('snippets.detail.delete')}
            >
              <Trash2 className="w-5 h-5" />
            </button>
          </div>
        </div>

        <div className="border-t border-gray-200 dark:border-dark-border">
          <CodeEditor
            value={snippet.code}
            language={typeof snippet.language === 'object' ? snippet.language?.name || 'python' : snippet.language}
            readOnly={true}
            height="600px"
          />
        </div>
      </div>

      <Modal
        isOpen={isDeleteModalOpen}
        onClose={() => setIsDeleteModalOpen(false)}
        title={t('snippets.detail.delete_modal.title')}
      >
        <div className="space-y-6">
          <p className="text-sm sm:text-base text-gray-600 dark:text-gray-300">
            {t('snippets.detail.delete_modal.confirm')}
          </p>
          <div className="flex flex-col sm:flex-row justify-end gap-3">
            <button
              onClick={() => setIsDeleteModalOpen(false)}
              className="px-4 py-2 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors font-medium"
            >
              {t('snippets.detail.delete_modal.cancel')}
            </button>
            <button
              onClick={handleConfirmDelete}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors font-medium shadow-sm"
            >
              {t('snippets.detail.delete_modal.delete_btn')}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};
