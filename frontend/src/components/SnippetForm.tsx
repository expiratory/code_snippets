import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Save } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import api from '../lib/api';
import { CodeEditor } from './CodeEditor';
import { LanguageSelect } from './LanguageSelect';

interface Language {
  id: number;
  name: string;
  slug: string;
}

export const SnippetForm: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { id } = useParams();
  const isEditing = !!id;
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    code: '',
    language: null as Language | null,
    tags: [] as string[],
  });
  const [tagInput, setTagInput] = useState('');
  const [availableTags, setAvailableTags] = useState<string[]>([]);

  useEffect(() => {
    if (isEditing) {
      fetchSnippet();
    } else {
      setFormData({
        title: '',
        code: '',
        language: null,
        tags: [],
      });
    }
    fetchTags();
  }, [id]);

  const fetchTags = async () => {
    try {
      const response = await api.get('/tags', { params: { limit: 10 } });
      setAvailableTags(response.data.map((t: any) => t.name));
    } catch (error) {
      console.error('Failed to fetch tags:', error);
    }
  };

  const fetchSnippet = async () => {
    try {
      const response = await api.get(`/snippets/${id}`);
      setFormData({
        title: response.data.title,
        code: response.data.code,
        language: response.data.language,
        tags: response.data.tags.map((t: any) => t.name),
      });
    } catch (error) {
      console.error('Failed to fetch snippet:', error);
      navigate('/');
    }
  };

  const handleAddTag = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && tagInput.trim()) {
      e.preventDefault();
      if (!formData.tags.includes(tagInput.trim())) {
        setFormData({ ...formData, tags: [...formData.tags, tagInput.trim()] });
      }
      setTagInput('');
    }
  };

  const removeTag = (tagToRemove: string) => {
    setFormData({
      ...formData,
      tags: formData.tags.filter(tag => tag !== tagToRemove)
    });
  };

  const toggleTag = (tag: string) => {
    if (formData.tags.includes(tag)) {
      removeTag(tag);
    } else {
      setFormData({ ...formData, tags: [...formData.tags, tag] });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    const lineCount = formData.code.split('\n').length;
    if (lineCount > 100) {
      alert(t('snippets.form.error_lines'));
      setLoading(false);
      return;
    }

    try {
      if (isEditing) {
        await api.put(`/snippets/${id}`, {
          ...formData,
          language_id: formData.language?.id
        });
      } else {
        await api.post('/snippets', {
          ...formData,
          language_id: formData.language?.id
        });
      }
      navigate('/');
    } catch (error) {
      console.error('Failed to create snippet:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <div className="bg-white dark:bg-dark-surface rounded-2xl border border-gray-200 dark:border-dark-border p-8 shadow-xl dark:shadow-none">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
          {isEditing ? t('snippets.form.edit_title') : t('snippets.form.create_title')}
        </h1>

        <form onSubmit={handleSubmit} className="space-y-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">{t('snippets.form.title_label')}</label>
              <input
                type="text"
                required
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="w-full bg-gray-50 dark:bg-[#0f0f11] border border-gray-200 dark:border-dark-border text-gray-900 dark:text-white px-4 py-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 transition-all"
                placeholder={t('snippets.form.title_placeholder')}
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">{t('snippets.form.language_label')}</label>
              <LanguageSelect
                value={formData.language}
                onChange={(language) => setFormData({ ...formData, language })}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">{t('snippets.form.tags_label')}</label>
            <div className="space-y-3">
              <div className="flex flex-wrap gap-2 mb-2">
                {formData.tags.map(tag => (
                  <span key={tag} className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 text-sm">
                    {tag}
                    <button type="button" onClick={() => removeTag(tag)} className="hover:text-primary-900 dark:hover:text-primary-100">
                      &times;
                    </button>
                  </span>
                ))}
              </div>
              <input
                type="text"
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyDown={handleAddTag}
                className="w-full bg-gray-50 dark:bg-[#0f0f11] border border-gray-200 dark:border-dark-border text-gray-900 dark:text-white px-4 py-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 transition-all"
                placeholder={t('snippets.form.tags_placeholder')}
              />
              {availableTags.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-2">
                  <span className="text-xs text-gray-500 dark:text-gray-400 mr-2 py-1">{t('snippets.form.suggested_tags')}</span>
                  {availableTags.filter(t => !formData.tags.includes(t)).map(tag => (
                    <button
                      key={tag}
                      type="button"
                      onClick={() => toggleTag(tag)}
                      className="text-xs px-2 py-1 rounded-md bg-gray-100 dark:bg-dark-bg text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-dark-border transition-colors"
                    >
                      + {tag}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">{t('snippets.form.code_label')}</label>
            <div className="border border-gray-200 dark:border-dark-border rounded-xl overflow-hidden">
              <CodeEditor
                value={formData.code}
                onChange={(value) => setFormData({ ...formData, code: value || '' })}
                language={formData.language?.name || 'python'}
                height="500px"
              />
            </div>
            <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
              {t('snippets.form.max_chars')}
            </p>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 bg-primary-600 hover:bg-primary-500 text-white px-8 py-4 rounded-xl transition-all shadow-lg shadow-primary-900/20 font-bold text-lg disabled:opacity-50 disabled:cursor-not-allowed hover:-translate-y-0.5"
          >
            <Save className="w-5 h-5" />
            {loading ? t('snippets.form.saving') : (isEditing ? t('snippets.form.update') : t('snippets.form.save'))}
          </button>
        </form>
      </div>
    </div>
  );
};
