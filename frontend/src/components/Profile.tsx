import React, { useEffect, useState } from 'react';
import { authService, type User } from '../services/authService';
import { useNavigate } from 'react-router-dom';
import { Key, LogOut, Mail, User as UserIcon, X } from 'lucide-react';
import { useTranslation } from 'react-i18next';

export const Profile: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [passwordData, setPasswordData] = useState({
    old_password: '',
    new_password: '',
    confirm_new_password: '',
  });
  const [passwordErrors, setPasswordErrors] = useState<string[]>([]);
  const [passwordSuccess, setPasswordSuccess] = useState(false);
  const [changingPassword, setChangingPassword] = useState(false);

  useEffect(() => {
    if ('scrollRestoration' in history) {
      history.scrollRestoration = 'manual';
    }
    window.scrollTo(0, 0);
    loadUser();

    return () => {
      if ('scrollRestoration' in history) {
        history.scrollRestoration = 'auto';
      }
    };
  }, []);

  const loadUser = async () => {
    try {
      const userData = await authService.getCurrentUser();
      setUser(userData);
    } catch (error) {
      navigate('/login');
    } finally {
      setLoading(false);
    }
  };

  const validatePassword = (password: string): string[] => {
    const errors: string[] = [];

    if (password.length < 8) {
      errors.push(t('auth.errors.password_length'));
    }
    if (!/[A-Z]/.test(password)) {
      errors.push(t('auth.errors.password_uppercase'));
    }
    if (!/[a-z]/.test(password)) {
      errors.push(t('auth.errors.password_lowercase'));
    }
    if (!/\d/.test(password)) {
      errors.push(t('auth.errors.password_digit'));
    }
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
      errors.push(t('auth.errors.password_special'));
    }

    return errors;
  };

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    setPasswordErrors([]);
    setPasswordSuccess(false);

    if (passwordData.new_password !== passwordData.confirm_new_password) {
      setPasswordErrors([t('profile.modal.error_mismatch')]);
      return;
    }

    const validationErrors = validatePassword(passwordData.new_password);
    if (validationErrors.length > 0) {
      setPasswordErrors(validationErrors);
      return;
    }

    setChangingPassword(true);

    try {
      await authService.changePassword({
        old_password: passwordData.old_password,
        new_password: passwordData.new_password,
        confirm_new_password: passwordData.confirm_new_password,
      });

      setPasswordSuccess(true);
      setPasswordData({ old_password: '', new_password: '', confirm_new_password: '' });

      setTimeout(() => {
        setShowPasswordModal(false);
        setPasswordSuccess(false);
      }, 2000);
    } catch (error: any) {
      setPasswordErrors([error.response?.data?.detail || t('profile.modal.error_generic')]);
    } finally {
      setChangingPassword(false);
    }
  };

  const handleLogout = () => {
    authService.logout();
    navigate('/');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-dark-bg">
        <div className="text-gray-600 dark:text-gray-400">{t('loading')}</div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-dark-bg px-4 py-12">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white dark:bg-dark-surface rounded-2xl shadow-xl p-8 border border-gray-200 dark:border-dark-border">
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
              {t('profile.title')}
            </h2>
          </div>

          <div className="space-y-6">
            {/* Username Field */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                <div className="flex items-center gap-2">
                  <UserIcon className="w-4 h-4" />
                  {t('auth.username')}
                </div>
              </label>
              <div className="w-full px-4 py-3 bg-gray-100 dark:bg-dark-bg border border-gray-300 dark:border-dark-border rounded-lg text-gray-700 dark:text-gray-300">
                {user.username}
              </div>
            </div>

            {/* Email Field */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                <div className="flex items-center gap-2">
                  <Mail className="w-4 h-4" />
                  {t('auth.email')}
                </div>
              </label>
              <div className="w-full px-4 py-3 bg-gray-100 dark:bg-dark-bg border border-gray-300 dark:border-dark-border rounded-lg text-gray-700 dark:text-gray-300">
                {user.email}
              </div>
            </div>

            {/* Change Password Button */}
            <div className="pt-4 flex justify-between">
              <button
                onClick={() => setShowPasswordModal(true)}
                className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-lg font-medium hover:from-primary-700 hover:to-primary-800 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 dark:focus:ring-offset-dark-surface transition-all"
              >
                <Key className="w-4 h-4" />
                {t('profile.change_password')}
              </button>
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-red-600 to-red-700 text-white rounded-lg font-medium hover:from-red-700 hover:to-red-800 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 dark:focus:ring-offset-dark-surface transition-all"
              >
                <LogOut className="w-4 h-4" />
                {t('profile.logout')}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Password Change Modal */}
      {showPasswordModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-dark-surface rounded-2xl shadow-2xl max-w-md w-full p-6 border border-gray-200 dark:border-dark-border">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {t('profile.modal.title')}
              </h3>
              <button
                onClick={() => {
                  setShowPasswordModal(false);
                  setPasswordErrors([]);
                  setPasswordSuccess(false);
                  setPasswordData({ old_password: '', new_password: '', confirm_new_password: '' });
                }}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            {passwordSuccess && (
              <div className="mb-4 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                <p className="text-sm text-green-600 dark:text-green-400">
                  {t('profile.modal.success')}
                </p>
              </div>
            )}

            {passwordErrors.length > 0 && (
              <div className="mb-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                <ul className="text-sm text-red-600 dark:text-red-400 space-y-1">
                  {passwordErrors.map((error, index) => (
                    <li key={index}>• {error}</li>
                  ))}
                </ul>
              </div>
            )}

            <form onSubmit={handlePasswordChange} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {t('profile.modal.current_password')}
                </label>
                <input
                  type="password"
                  value={passwordData.old_password}
                  onChange={(e) =>
                    setPasswordData({ ...passwordData, old_password: e.target.value })
                  }
                  className="w-full px-4 py-3 bg-gray-50 dark:bg-dark-bg border border-gray-300 dark:border-dark-border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent text-gray-900 dark:text-gray-100 transition-all"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {t('profile.modal.new_password')}
                </label>
                <input
                  type="password"
                  value={passwordData.new_password}
                  onChange={(e) =>
                    setPasswordData({ ...passwordData, new_password: e.target.value })
                  }
                  className="w-full px-4 py-3 bg-gray-50 dark:bg-dark-bg border border-gray-300 dark:border-dark-border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent text-gray-900 dark:text-gray-100 transition-all"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {t('profile.modal.confirm_new_password')}
                </label>
                <input
                  type="password"
                  value={passwordData.confirm_new_password}
                  onChange={(e) =>
                    setPasswordData({ ...passwordData, confirm_new_password: e.target.value })
                  }
                  className="w-full px-4 py-3 bg-gray-50 dark:bg-dark-bg border border-gray-300 dark:border-dark-border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent text-gray-900 dark:text-gray-100 transition-all"
                  required
                />
              </div>

              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => {
                    setShowPasswordModal(false);
                    setPasswordErrors([]);
                    setPasswordData({ old_password: '', new_password: '', confirm_new_password: '' });
                  }}
                  className="flex-1 px-4 py-3 border border-gray-300 dark:border-dark-border text-gray-700 dark:text-gray-300 rounded-lg font-medium hover:bg-gray-50 dark:hover:bg-dark-bg transition-all"
                >
                  {t('profile.modal.cancel')}
                </button>
                <button
                  type="submit"
                  disabled={changingPassword}
                  className="flex-1 bg-gradient-to-r from-primary-600 to-primary-700 text-white py-3 px-4 rounded-lg font-medium hover:from-primary-700 hover:to-primary-800 focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {changingPassword ? t('profile.modal.submitting') : t('profile.modal.submit')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
