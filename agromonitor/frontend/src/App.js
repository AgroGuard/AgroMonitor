import React from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import Login from './components/Login/Login';
import Dashboard from './components/Dashboard/Dashboard';
import Cadastro from './components/Cadastro/Cadastro';
import Sidebar from './components/Sidebar/Sidebar';
import Recuperar from './components/Recuparar/Recuperar';
import CompletarCadastro from './components/Cadastro/CompletarCadastro';
import CadastroEstufa from './components/Cadastro/Cadastro-Estufa';
import Configuracoes from './components/Configuracoes/Configuracoes';
import ClimaDashboard from './components/Clima/ClimaDashboard';
import CadastroRegiao from './components/Cadastro/Cadastro-Regiao';
import NotAuthorized from './components/Common/NotAuthorized';
import Termos from './components/Termos/Termos';

function App() {
  const location = useLocation();
  const isLoggedIn = typeof window !== 'undefined' && Boolean(localStorage.getItem('authToken'));
  const noSidebarPaths = ['/', '/Login'];
  const isCompletarCadastroPage = location.pathname.startsWith('/completar-cadastro');
  const mostrarSidebar =
    !noSidebarPaths.includes(location.pathname) &&
    !location.pathname.startsWith('/recuperar') &&
    (isLoggedIn || isCompletarCadastroPage);

  const ProtectedRoute = ({ element }) => {
    return isLoggedIn ? element : <Navigate to="/" replace />;
  };

  return (
    <div className="app-layout">
      {mostrarSidebar && <Sidebar />}
      <main className={mostrarSidebar ? 'main-content' : 'full-page'}>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/dashboard" element={<ProtectedRoute element={<Dashboard />} />} />
          <Route path="/cadastro" element={<ProtectedRoute element={<Cadastro />} />} />
          <Route path="/cadastro-estufa" element={<ProtectedRoute element={<CadastroEstufa />} />} />
          <Route path="/clima" element={<ProtectedRoute element={<CadastroRegiao />} />} />
          <Route path="/nao-autorizado" element={<ProtectedRoute element={<NotAuthorized />} />} />
          <Route path="/configuracoes" element={<ProtectedRoute element={<Configuracoes />} />} />
          <Route path="/termos" element={<ProtectedRoute element={<Termos />} />} />
          <Route path="/recuperar" element={<Recuperar />} />
          <Route path="/recuperar/:token" element={<Recuperar />} />
          <Route path="/completar-cadastro" element={<CompletarCadastro />} />
          <Route path="/completar-cadastro/:token" element={<CompletarCadastro />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
