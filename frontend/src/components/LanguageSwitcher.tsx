import React, { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Globe } from 'lucide-react';

const LanguageSwitcher: React.FC = () => {
  const { t, i18n } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
    setIsOpen(false);
  };

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        aria-label={t('nav.language_switcher')}
        title={t('nav.language_switcher')}
      >
        <Globe className="w-5 h-5" />
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-dark-surface rounded-xl shadow-lg border border-gray-200 dark:border-dark-border py-1 z-50">
          <button
            onClick={() => changeLanguage('en')}
            className={`w-full px-4 py-2 text-left text-sm hover:bg-gray-50 dark:hover:bg-dark-border transition-colors flex items-center justify-between ${
              i18n.language === 'en' ? 'text-primary-600 dark:text-primary-400 font-medium' : 'text-gray-700 dark:text-gray-300'
            }`}
          >
            <span>English</span>
            {i18n.language === 'en' && <span className="text-primary-600 dark:text-primary-400">✓</span>}
          </button>
          <button
            onClick={() => changeLanguage('ru')}
            className={`w-full px-4 py-2 text-left text-sm hover:bg-gray-50 dark:hover:bg-dark-border transition-colors flex items-center justify-between ${
              i18n.language === 'ru' ? 'text-primary-600 dark:text-primary-400 font-medium' : 'text-gray-700 dark:text-gray-300'
            }`}
          >
            <span>Русский</span>
            {i18n.language === 'ru' && <span className="text-primary-600 dark:text-primary-400">✓</span>}
          </button>
        </div>
      )}
    </div>
  );
};

export default LanguageSwitcher;
