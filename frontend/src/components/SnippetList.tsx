import React, { useEffect, useState, useRef, useCallback } from 'react';
import { Search, Filter, ChevronDown, Check } from 'lucide-react';
import axios from 'axios';
import { useTranslation } from 'react-i18next';
import api from '../lib/api';
import type { Snippet, Tag } from '../types';
import { SnippetCard } from './SnippetCard';
import { LanguageSelect } from './LanguageSelect';

interface Language {
  id: number;
  name: string;
  slug: string;
}

export const SnippetList: React.FC = () => {
  const { t } = useTranslation();
  const [snippets, setSnippets] = useState<Snippet[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [tags, setTags] = useState<Tag[]>([]);
  const [selectedTag, setSelectedTag] = useState('');
  const [selectedLanguage, setSelectedLanguage] = useState<Language | null>(null);
  const [page, setPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const observerTarget = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    const fetchTags = async () => {
      try {
        const response = await api.get('/tags');
        setTags(response.data);
      } catch (error) {
        console.error('Failed to fetch tags:', error);
      }
    };
    fetchTags();
  }, []);

  const [debouncedSearchQuery, setDebouncedSearchQuery] = useState('');

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearchQuery(searchQuery);
    }, 300);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  const fetchSnippets = useCallback(async (reset = false) => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    abortControllerRef.current = new AbortController();

    setLoading(true);
    try {
      const currentOffset = reset ? 0 : page * 10;
      const response = await api.get('/snippets', {
        params: {
          q: debouncedSearchQuery || undefined,
          tag: selectedTag || undefined,
          language_id: selectedLanguage?.id || undefined,
          offset: currentOffset,
          limit: 10,
        },
        signal: abortControllerRef.current.signal,
      });

      const newSnippets = response.data;
      if (newSnippets.length < 10) setHasMore(false);
      else setHasMore(true);

      setSnippets(prev => reset ? newSnippets : [...prev, ...newSnippets]);
      if (reset) setPage(1);
      else setPage(prev => prev + 1);
    } catch (error) {
      if (axios.isCancel(error)) {
        return;
      }
      console.error('Failed to fetch snippets:', error);
    } finally {
      if (abortControllerRef.current && !abortControllerRef.current.signal.aborted) {
        setLoading(false);
        abortControllerRef.current = null;
      }
    }
  }, [debouncedSearchQuery, selectedTag, selectedLanguage, page]);

  useEffect(() => {
    setPage(0);
    setHasMore(true);
    fetchSnippets(true);
  }, [debouncedSearchQuery, selectedTag, selectedLanguage]);

  useEffect(() => {
    const observer = new IntersectionObserver(
      entries => {
        if (entries[0].isIntersecting && hasMore && !loading) {
          fetchSnippets(false);
        }
      },
      { threshold: 0.1 }
    );

    if (observerTarget.current) {
      observer.observe(observerTarget.current);
    }

    return () => {
      if (observerTarget.current) {
        observer.unobserve(observerTarget.current);
      }
    };
  }, [hasMore, loading, fetchSnippets]);

  return (
    <div className="max-w-7xl mx-auto px-4 py-12">
      <div className="flex flex-col md:flex-row items-center justify-between mb-12 gap-6">
      </div>

      <div className="relative mb-12 max-w-2xl mx-auto flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder={t('snippets.search_placeholder')}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-12 pr-4 py-4 bg-white dark:bg-dark-surface border border-gray-200 dark:border-dark-border rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 transition-all shadow-sm text-gray-900 dark:text-white placeholder-gray-500"
          />
        </div>
        <div className="relative w-48" ref={dropdownRef}>
          <button
            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
            className="w-full pl-12 pr-4 py-4 bg-white dark:bg-dark-surface border border-gray-200 dark:border-dark-border rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 transition-all shadow-sm text-left flex items-center justify-between text-gray-900 dark:text-white"
          >
            <Filter className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <span className="truncate">{selectedTag || t('snippets.all_tags')}</span>
            <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform duration-200 ${isDropdownOpen ? 'transform rotate-180' : ''}`} />
          </button>

          {isDropdownOpen && (
            <div className="absolute z-10 w-full mt-2 bg-white dark:bg-dark-surface border border-gray-200 dark:border-dark-border rounded-xl shadow-lg max-h-60 overflow-auto py-1">
              <button
                onClick={() => {
                  setSelectedTag('');
                  setIsDropdownOpen(false);
                }}
                className={`w-full px-4 py-2 text-left hover:bg-gray-50 dark:hover:bg-dark-border transition-colors flex items-center justify-between ${
                  selectedTag === '' ? 'text-primary-600 dark:text-primary-400 bg-primary-50 dark:bg-primary-900/20' : 'text-gray-700 dark:text-gray-300'
                }`}
              >
                <span>{t('snippets.all_tags')}</span>
                {selectedTag === '' && <Check className="w-4 h-4" />}
              </button>
              {tags.map(tag => (
                <button
                  key={tag.id}
                  onClick={() => {
                    setSelectedTag(tag.name);
                    setIsDropdownOpen(false);
                  }}
                  className={`w-full px-4 py-2 text-left hover:bg-gray-50 dark:hover:bg-dark-border transition-colors flex items-center justify-between ${
                    selectedTag === tag.name ? 'text-primary-600 dark:text-primary-400 bg-primary-50 dark:bg-primary-900/20' : 'text-gray-700 dark:text-gray-300'
                  }`}
                >
                  <span className="truncate">{tag.name}</span>
                  {selectedTag === tag.name && <Check className="w-4 h-4" />}
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="relative w-48">
          <LanguageSelect
            value={selectedLanguage}
            onChange={setSelectedLanguage}
            className="w-full"
            variant="filter"
          />
        </div>
      </div>

      {loading && snippets.length === 0 ? (
        <div className="text-center text-gray-500 dark:text-gray-400 py-12">{t('snippets.loading')}</div>
      ) : (
        <>
          {snippets.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {snippets.map((snippet) => (
                <SnippetCard key={snippet.id} snippet={snippet} />
              ))}
            </div>
          ) : (
            <div className="text-center py-20">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 dark:bg-dark-surface mb-6">
                <Search className="w-8 h-8 text-gray-400" />
              </div>
              <h3 className="text-xl font-medium text-gray-900 dark:text-white mb-2">{t('snippets.no_snippets_title')}</h3>
              <p className="text-gray-500 dark:text-gray-400 max-w-md mx-auto">
                {t('snippets.no_snippets_desc')}
              </p>
            </div>
          )}

          {hasMore && snippets.length > 0 && (
            <div ref={observerTarget} className="h-10 flex items-center justify-center mt-8">
              {loading && <div className="text-gray-500 dark:text-gray-400">{t('snippets.loading_more')}</div>}
            </div>
          )}
        </>
      )}
    </div>
  );
};
