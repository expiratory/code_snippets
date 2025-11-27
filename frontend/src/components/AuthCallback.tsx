import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService } from '../services/authService';

export const AuthCallback: React.FC = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const hash = window.location.hash.substring(1);
    const params = new URLSearchParams(hash);

    const token = params.get('token');
    const refreshToken = params.get('refresh_token');

    if (token && refreshToken) {
      authService.setToken({
        access_token: token,
        refresh_token: refreshToken,
        token_type: 'bearer',
      });
      navigate('/', { replace: true });
    } else {
      navigate('/login');
    }
  }, [navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-dark-bg">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4"></div>
        <p className="text-gray-600 dark:text-gray-400">Completing authentication...</p>
      </div>
    </div>
  );
};
