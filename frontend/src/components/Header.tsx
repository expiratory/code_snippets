import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { LogIn, User, UserPlus, Code2, Tag as TagIcon, PlusCircle, Terminal } from 'lucide-react';
import { ThemeToggle } from './ThemeToggle';
import { authService } from '../services/authService';

export const Header: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    setIsAuthenticated(authService.isAuthenticated());
    const unsubscribe = authService.subscribe(() => {
      setIsAuthenticated(authService.isAuthenticated());
    });
    return unsubscribe;
  }, []);

  return (
    <header className="border-b border-gray-200 dark:border-dark-border bg-white dark:bg-dark-surface sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 group">
          <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center text-white font-bold shadow-lg shadow-primary-900/20 group-hover:scale-105 transition-transform">
            <Code2 className="w-5 h-5" />
          </div>
          <div className="flex flex-col">
            <span className="text-xl font-bold text-gray-900 dark:text-white tracking-tight">
              Code Snippets
            </span>
            <span className="text-sm text-gray-500 dark:text-gray-400">Manage your code fragments efficiently.</span>
          </div>
        </Link>

        <div className="flex items-center gap-3">
          <ThemeToggle />
          {isAuthenticated ? (
            <>
              <Link
                to="/run"
                className="flex items-center gap-2 px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-surface rounded-lg transition-colors font-medium"
              >
                <Terminal className="w-5 h-5" />
                <span>Run Code</span>
              </Link>
              <Link
                to="/tags"
                className="flex items-center gap-2 px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-surface rounded-lg transition-colors font-medium"
              >
                <TagIcon className="w-5 h-5" />
                <span>Tags</span>
              </Link>
              <Link
                to="/profile"
                className="flex items-center gap-2 bg-gray-100 dark:bg-dark-bg hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-900 dark:text-gray-100 px-4 py-2 rounded-lg transition-all font-medium text-sm"
              >
                <User className="w-4 h-4" />
                Profile
              </Link>
              <Link
                to="/new"
                className="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors font-medium"
              >
                <PlusCircle className="w-5 h-5" />
                <span>New Snippet</span>
              </Link>
            </>
          ) : (
            <>
              <Link
                to="/register"
                className="flex items-center gap-2 bg-gray-100 dark:bg-dark-bg hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-900 dark:text-gray-100 px-4 py-2 rounded-lg transition-all font-medium text-sm"
              >
                <UserPlus className="w-4 h-4" />
                Sign Up
              </Link>
              <Link
                to="/login"
                className="flex items-center gap-2 bg-primary-600 hover:bg-primary-500 text-white px-4 py-2 rounded-lg transition-all shadow-md shadow-primary-900/20 font-medium text-sm"
              >
                <LogIn className="w-4 h-4" />
                Login
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
};
