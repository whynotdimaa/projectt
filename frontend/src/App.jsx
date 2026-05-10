import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import './App.css';

import Layout from './components/Layout';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Candidates from './pages/Candidates';
import Vacancies from './pages/Vacancies';
import Interviews from './pages/Interviews';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) return <div style={{ background: 'var(--bg-main)', height: '100vh' }}></div>;
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
};

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          <Route path="/" element={
            <ProtectedRoute>
              <Layout><Dashboard /></Layout>
            </ProtectedRoute>
          } />
          
          <Route path="/candidates" element={
            <ProtectedRoute>
              <Layout><Candidates /></Layout>
            </ProtectedRoute>
          } />
          
          <Route path="/vacancies" element={
            <ProtectedRoute>
              <Layout><Vacancies /></Layout>
            </ProtectedRoute>
          } />
          
          <Route path="/interviews" element={
            <ProtectedRoute>
              <Layout><Interviews /></Layout>
            </ProtectedRoute>
          } />
          
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
