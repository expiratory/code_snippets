import React from 'react';
import { Navigate } from 'react-router-dom';
import { authService } from '../services/authService';

export const PrivateRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const isAuthenticated = authService.isAuthenticated();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
};
