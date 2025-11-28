import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { LogIn, User, UserPlus, Code2, Tag as TagIcon, PlusCircle, Terminal, Menu, X } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { ThemeToggle } from './ThemeToggle';
import LanguageSwitcher from './LanguageSwitcher';
import { authService } from '../services/authService';

export const Header: React.FC = () => {
  const { t } = useTranslation();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    setIsAuthenticated(authService.isAuthenticated());
    const unsubscribe = authService.subscribe(() => {
      setIsAuthenticated(authService.isAuthenticated());
    });
    return unsubscribe;
  }, []);

  // Close mobile menu when clicking outside or on a link
  const closeMobileMenu = () => setIsMobileMenuOpen(false);

  // Prevent body scroll when mobile menu is open
  useEffect(() => {
    if (isMobileMenuOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isMobileMenuOpen]);

  return (
    <header className="border-b border-gray-200 dark:border-dark-border bg-white dark:bg-dark-surface sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 group" onClick={closeMobileMenu}>
          <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center text-white font-bold shadow-lg shadow-primary-900/20 group-hover:scale-105 transition-transform">
            <Code2 className="w-5 h-5" />
          </div>
          <div className="flex flex-col">
            <span className="text-lg sm:text-xl font-bold text-gray-900 dark:text-white tracking-tight">
              {t('app.title')}
            </span>
            <span className="hidden sm:block text-sm text-gray-500 dark:text-gray-400">{t('app.subtitle')}</span>
          </div>
        </Link>

        {/* Desktop Navigation */}
        <div className="hidden lg:flex items-center gap-3">
          <LanguageSwitcher />
          <ThemeToggle />
          {isAuthenticated ? (
            <>
              <Link
                to="/run"
                className="flex items-center gap-2 px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-surface rounded-lg transition-colors font-medium"
              >
                <Terminal className="w-5 h-5" />
                <span>{t('nav.run_code')}</span>
              </Link>
              <Link
                to="/tags"
                className="flex items-center gap-2 px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-surface rounded-lg transition-colors font-medium"
              >
                <TagIcon className="w-5 h-5" />
                <span>{t('nav.tags')}</span>
              </Link>
              <Link
                to="/profile"
                className="flex items-center gap-2 bg-gray-100 dark:bg-dark-bg hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-900 dark:text-gray-100 px-4 py-2 rounded-lg transition-all font-medium text-sm"
              >
                <User className="w-4 h-4" />
                {t('nav.profile')}
              </Link>
              <Link
                to="/new"
                className="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors font-medium whitespace-nowrap"
              >
                <PlusCircle className="w-5 h-5" />
                <span>{t('nav.new_snippet')}</span>
              </Link>
            </>
          ) : (
            <>
              <Link
                to="/register"
                className="flex items-center gap-2 bg-gray-100 dark:bg-dark-bg hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-900 dark:text-gray-100 px-4 py-2 rounded-lg transition-all font-medium text-sm"
              >
                <UserPlus className="w-4 h-4" />
                {t('nav.sign_up')}
              </Link>
              <Link
                to="/login"
                className="flex items-center gap-2 bg-primary-600 hover:bg-primary-500 text-white px-4 py-2 rounded-lg transition-all shadow-md shadow-primary-900/20 font-medium text-sm"
              >
                <LogIn className="w-4 h-4" />
                {t('nav.login')}
              </Link>
            </>
          )}
        </div>

        {/* Mobile Controls */}
        <div className="flex lg:hidden items-center gap-2">
          <LanguageSwitcher />
          <ThemeToggle />
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="p-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-surface rounded-lg transition-colors"
            aria-label="Toggle menu"
          >
            {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Menu Overlay */}
      {isMobileMenuOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={closeMobileMenu}
        />
      )}

      {/* Mobile Menu Drawer */}
      <div
        className={`fixed top-16 right-0 bottom-0 w-64 bg-white dark:bg-dark-surface border-l border-gray-200 dark:border-dark-border z-40 transform transition-transform duration-300 ease-in-out lg:hidden ${
          isMobileMenuOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        <nav className="flex flex-col p-4 gap-2">
          {isAuthenticated ? (
            <>
              <Link
                to="/run"
                onClick={closeMobileMenu}
                className="flex items-center gap-3 px-4 py-3 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-border rounded-lg transition-colors font-medium"
              >
                <Terminal className="w-5 h-5" />
                <span>{t('nav.run_code')}</span>
              </Link>
              <Link
                to="/tags"
                onClick={closeMobileMenu}
                className="flex items-center gap-3 px-4 py-3 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-border rounded-lg transition-colors font-medium"
              >
                <TagIcon className="w-5 h-5" />
                <span>{t('nav.tags')}</span>
              </Link>
              <Link
                to="/profile"
                onClick={closeMobileMenu}
                className="flex items-center gap-3 px-4 py-3 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-border rounded-lg transition-colors font-medium"
              >
                <User className="w-5 h-5" />
                {t('nav.profile')}
              </Link>
              <Link
                to="/new"
                onClick={closeMobileMenu}
                className="flex items-center gap-3 px-4 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors font-medium mt-2"
              >
                <PlusCircle className="w-5 h-5" />
                <span>{t('nav.new_snippet')}</span>
              </Link>
            </>
          ) : (
            <>
              <Link
                to="/register"
                onClick={closeMobileMenu}
                className="flex items-center gap-3 px-4 py-3 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-border rounded-lg transition-colors font-medium"
              >
                <UserPlus className="w-5 h-5" />
                {t('nav.sign_up')}
              </Link>
              <Link
                to="/login"
                onClick={closeMobileMenu}
                className="flex items-center gap-3 px-4 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors font-medium mt-2"
              >
                <LogIn className="w-5 h-5" />
                {t('nav.login')}
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
};
