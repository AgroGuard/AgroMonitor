import React from 'react';
import './Sidebar.css';
import { NavLink, useLocation } from 'react-router-dom';

const Sidebar = () => {
  const role = (typeof window !== 'undefined') ? localStorage.getItem('userRole') : null;
  const location = useLocation();
  const isCompletarCadastroPage = location.pathname.startsWith('/completar-cadastro');

  return (
    <div className="Sidebar">
      <div className="sidebar-header">
        <h1 className="sidebar-title">AgroMonitor</h1>
      </div>
      {!isCompletarCadastroPage && (
        <nav className="sidebar-menu">
        <NavLink to="/dashboard" className={({ isActive }) => isActive ? 'menu-item active' : 'menu-item'}>
          Visão Geral
        </NavLink>
        <NavLink to="/clima" className={({ isActive }) => isActive ? 'menu-item active' : 'menu-item'}>
          Clima
        </NavLink>
        {role === 'owner' && (
          <NavLink to="/cadastro-estufa" className={({ isActive }) => isActive ? 'menu-item active' : 'menu-item'}>
            Cadastro de Estufas
          </NavLink>
        )}
        <NavLink to="/cadastro" className={({ isActive }) => isActive ? 'menu-item active' : 'menu-item'}>
          Cadastro de Usuários
        </NavLink>
        <NavLink to="/termos" className={({ isActive }) => isActive ? 'menu-item active' : 'menu-item'}>
          Termos e Privacidade
        </NavLink>
        <NavLink to="/configuracoes" className={({ isActive }) => isActive ? 'menu-item active' : 'menu-item'}>
          Configurações de Conta
        </NavLink>
        </nav>
      )}
    </div>
  );
};

export default Sidebar;