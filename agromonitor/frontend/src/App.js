import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useLocation } from 'react-router-dom';
import Login from './components/Login/Login';
import Dashboard from './components/Dashboard/Dashboard';
import Cadastro from './components/Cadastro/Cadastro';
import Sidebar from './components/Sidebar/Sidebar';
import Recuperar from './components/Recuparar/Recuperar';

function App() {
  const location = useLocation();
  const semSidebar = ['/', '/Login', '/recuperar'];
  const mostrarSidebar = !semSidebar.includes(location.pathname);

  return (
    <div className="app-layout">
      {mostrarSidebar && <Sidebar />}
      <main className={mostrarSidebar ? 'main-content' : 'full-page'}>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/cadastro" element={<Cadastro />} />
          <Route path="/recuperar" element={<Recuperar />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;