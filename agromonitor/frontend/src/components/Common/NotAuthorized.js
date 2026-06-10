import React from 'react';
import { Link } from 'react-router-dom';
import './NotAuthorized.css';

const NotAuthorized = () => {
  return (
    <div className="not-authorized-container">
      <div className="not-authorized-card">
        <h1>403 — Acesso não autorizado</h1>
        <p>Você não tem permissão para acessar esta página.</p>
        <div className="actions">
          <Link to="/dashboard" className="button-user">Voltar ao Painel</Link>
        </div>
      </div>
    </div>
  );
};

export default NotAuthorized;
