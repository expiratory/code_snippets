import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { SnippetList } from './components/SnippetList';
import { SnippetForm } from './components/SnippetForm';
import { SnippetDetail } from './components/SnippetDetail';
import { Login } from './components/Login';
import { Register } from './components/Register';
import { Profile } from './components/Profile';
import { Header } from './components/Header';
import { AuthCallback } from './components/AuthCallback';
import { GoogleRegister } from './components/GoogleRegister';
import { PrivateRoute } from './components/PrivateRoute';
import { ThemeProvider } from './context/ThemeContext';

import { Home } from './components/Home';
import { TagManager } from './components/TagManager';
import { CodeRunner } from './components/CodeRunner';
import { authService } from './services/authService';

import { useEffect, useState } from 'react';

const HomeRoute = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(authService.isAuthenticated());

  useEffect(() => {
    setIsAuthenticated(authService.isAuthenticated());

    const unsubscribe = authService.subscribe(() => {
      setIsAuthenticated(authService.isAuthenticated());
    });
    return unsubscribe;
  }, []);

  return isAuthenticated ? <SnippetList /> : <Home />;
};

function App() {
  return (
    <ThemeProvider>
      <Router>
        <div className="min-h-screen bg-gray-50 dark:bg-dark-bg transition-colors">
          <Header />
          <main>
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/auth/callback" element={<AuthCallback />} />
              <Route path="/auth/google-register" element={<GoogleRegister />} />
              <Route
                path="/profile"
                element={
                  <PrivateRoute>
                    <Profile />
                  </PrivateRoute>
                }
              />
              <Route
                path="/"
                element={<HomeRoute />}
              />
              <Route path="/new" element={<SnippetForm />} />
              <Route path="/snippets/:id/edit" element={<SnippetForm />} />
              <Route path="/snippets/:id" element={<SnippetDetail />} />

              <Route path="/tags" element={<PrivateRoute><TagManager /></PrivateRoute>} />
              <Route path="/run" element={<CodeRunner />} />
            </Routes>
          </main>
        </div>
      </Router>
    </ThemeProvider>
  );
}

export default App;
