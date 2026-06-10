import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './Cadastro-estufa.css';

const API_BASE_URL = (() => {
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      return 'http://127.0.0.1:8000';
    }
  }
  return process.env.REACT_APP_API_URL || 'https://api.agromonitor.vercel.app';
})();

const CadastroEstufa = () => {
  const [formEstufa, setFormEstufa] = useState({
    nomeEstufa: '',
    observacoes: ''
  });
  const [estufas, setEstufas] = useState([]);
  const [statusMessage, setStatusMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [userRole, setUserRole] = useState('');

  const getAuthToken = () => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('authToken');
    }
    return null;
  };

  const apiHeaders = () => {
    const token = getAuthToken();
    const headers = { 'Content-Type': 'application/json' };
    if (token) {
      headers.Authorization = `Token ${token}`;
    }
    return headers;
  };

  const loadEstufas = async () => {
    setErrorMessage('');
    try {
      const response = await fetch(`${API_BASE_URL}/api/estufas/`, {
        method: 'GET',
        headers: apiHeaders()
      });

      const data = await response.json();
      if (!response.ok) {
        setErrorMessage(data.error || 'Falha ao carregar estufas.');
        return;
      }

      setEstufas(data.estufas || []);
    } catch (error) {
      setErrorMessage('Erro de rede ao carregar estufas.');
    }
  };

  const navigate = useNavigate();

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const roleFromStorage = localStorage.getItem('userRole') || '';
      setUserRole(roleFromStorage);
      // Redirect non-owners away from this route
      if (roleFromStorage && roleFromStorage !== 'owner') {
        navigate('/nao-autorizado');
      }
    }
  }, [navigate]);

  useEffect(() => {
    loadEstufas();
  }, []);

  const handleCadastroEstufa = async (e) => {
    e.preventDefault();
    setStatusMessage('');
    setErrorMessage('');

    if (userRole !== 'owner') {
      setErrorMessage('Apenas owners podem cadastrar estufas.');
      return;
    }

    if (!formEstufa.nomeEstufa.trim()) {
      setErrorMessage('O nome da estufa é obrigatório.');
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/estufas/`, {
        method: 'POST',
        headers: apiHeaders(),
        body: JSON.stringify({
          nome: formEstufa.nomeEstufa,
          descricao: formEstufa.observacoes
        })
      });

      const data = await response.json();
      if (!response.ok) {
        setErrorMessage(data.error || 'Falha ao cadastrar estufa.');
        return;
      }

      setEstufas((prev) => [...prev, data.estufa]);
      setStatusMessage('Estufa cadastrada com sucesso!');
      setFormEstufa({ nomeEstufa: '', observacoes: '' });
    } catch (error) {
      setErrorMessage('Erro de rede ao cadastrar estufa.');
    }
  };

  const handleEstufaChange = (e) => {
    const { name, value } = e.target;
    setFormEstufa((prev) => ({ ...prev, [name]: value }));
  };

  return (
    <div className="registration-container">
      <section className="registration-card">
        <h2 className="card-title">Cadastro de Estufa</h2>
        {userRole === 'owner' ? (
          <form className="form-row-flex" onSubmit={handleCadastroEstufa}>
            <div className="inputs-column">
              <div className="input-group">
                <label htmlFor="nomeEstufa">Nome da Estufa</label>
                <input
                  id="nomeEstufa"
                  type="text"
                  name="nomeEstufa"
                  placeholder="Digite o nome ou número da estufa"
                  value={formEstufa.nomeEstufa}
                  onChange={handleEstufaChange}
                  required
                />

                <label htmlFor="observacoes">Observações</label>
                <textarea
                  id="observacoes"
                  name="observacoes"
                  placeholder="Adicione observações sobre a estufa (ex: tipo de cultura, localização)"
                  value={formEstufa.observacoes}
                  onChange={handleEstufaChange}
                  rows="4"
                />
              </div>
            </div>

            <div className="button-column">
              <button type="submit" className="button-user">
                Cadastrar
              </button>
            </div>
          </form>
        ) : (
          <p className="info-message">Você pode visualizar estufas, mas apenas owners podem cadastrar novas estufas.</p>
        )}

        {statusMessage && <p className="success-message">{statusMessage}</p>}
        {errorMessage && <p className="error-message">{errorMessage}</p>}
      </section>

      <section className="table-section">
        <h3>Estufas cadastradas</h3>
        <table className="custom-table">
          <thead>
            <tr>
              <th>Nome da Estufa</th>
              <th>Observações</th>
            </tr>
          </thead>
          <tbody>
            {estufas.length > 0 ? (
              estufas.map((estufa) => (
                <tr key={estufa.id}>
                  <td>{estufa.nome}</td>
                  <td>{estufa.descricao || '-'}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="2">Nenhuma estufa cadastrada.</td>
              </tr>
            )}
          </tbody>
        </table>
      </section>
    </div>
  );
};

export default CadastroEstufa;
