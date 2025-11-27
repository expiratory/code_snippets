import React from 'react';
import { Link } from 'react-router-dom';
import { Code2, LogIn, Search, UserPlus, Zap } from 'lucide-react';
import { useTranslation } from 'react-i18next';

export const Home: React.FC = () => {
  const { t } = useTranslation();

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-dark-bg">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary-600/20 to-purple-600/20 dark:from-primary-900/40 dark:to-purple-900/40 z-0" />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-32 relative z-10">
          <div className="text-center max-w-3xl mx-auto">
            <h1 className="text-5xl md:text-6xl font-bold text-gray-900 dark:text-white mb-8 tracking-tight">
              {t('app.title')}
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-300 mb-12 leading-relaxed">
              {t('home.hero_text')}
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/register"
                className="flex items-center gap-2 px-8 py-4 bg-white dark:bg-dark-surface border border-gray-200 dark:border-dark-border text-gray-900 dark:text-white rounded-xl font-bold text-lg hover:bg-gray-50 dark:hover:bg-dark-border transition-all hover:-translate-y-1"
              >
                <UserPlus className="w-4 h-4" />
                {t('nav.sign_up')}
              </Link>
              <Link
                to="/login"
                className="flex items-center gap-2 px-8 py-4 bg-primary-600 hover:bg-primary-700 text-white rounded-xl font-bold text-lg shadow-lg shadow-primary-600/30 transition-all hover:-translate-y-1"
              >
                <LogIn className="w-4 h-4" />
                {t('nav.login')}
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
          <div className="p-8 bg-white dark:bg-dark-surface rounded-2xl border border-gray-200 dark:border-dark-border shadow-sm hover:shadow-md transition-all">
            <div className="w-14 h-14 bg-blue-100 dark:bg-blue-900/30 rounded-xl flex items-center justify-center mb-6">
              <Code2 className="w-7 h-7 text-blue-600 dark:text-blue-400" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">{t('home.features.syntax.title')}</h3>
            <p className="text-gray-600 dark:text-gray-400">
              {t('home.features.syntax.desc')}
            </p>
          </div>

          <div className="p-8 bg-white dark:bg-dark-surface rounded-2xl border border-gray-200 dark:border-dark-border shadow-sm hover:shadow-md transition-all">
            <div className="w-14 h-14 bg-purple-100 dark:bg-purple-900/30 rounded-xl flex items-center justify-center mb-6">
              <Search className="w-7 h-7 text-purple-600 dark:text-purple-400" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">{t('home.features.search.title')}</h3>
            <p className="text-gray-600 dark:text-gray-400">
              {t('home.features.search.desc')}
            </p>
          </div>

          <div className="p-8 bg-white dark:bg-dark-surface rounded-2xl border border-gray-200 dark:border-dark-border shadow-sm hover:shadow-md transition-all">
            <div className="w-14 h-14 bg-green-100 dark:bg-green-900/30 rounded-xl flex items-center justify-center mb-6">
              <Zap className="w-7 h-7 text-green-600 dark:text-green-400" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">{t('home.features.fast.title')}</h3>
            <p className="text-gray-600 dark:text-gray-400">
              {t('home.features.fast.desc')}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
