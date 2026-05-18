import React from 'react';
import './Sidebar.css';
import { NavLink } from 'react-router-dom';

const Sidebar = () => {
  return (
    <div className="Sidebar">
      <div className="sidebar-header">
        <h1 className="sidebar-title">AgroMonitor</h1>
      </div>
      <nav className="sidebar-menu">
        <NavLink to="/dashboard" className={({ isActive }) => isActive ? 'menu-item active' : 'menu-item'}>
          Visão Geral
        </NavLink>
        <NavLink to="/cadastro-estufa" className={({ isActive }) => isActive ? 'menu-item active' : 'menu-item'}>
          Cadastro de Estufas
        </NavLink>
        <NavLink to="/cadastro" className={({ isActive }) => isActive ? 'menu-item active' : 'menu-item'}>
          Cadastro de Usuários
        </NavLink>
        <NavLink to="/configuracoes" className={({ isActive }) => isActive ? 'menu-item active' : 'menu-item'}>
          Configurações
        </NavLink>
      </nav>
    </div>
  );
};

export default Sidebar;