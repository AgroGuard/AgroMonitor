import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './Cadastro.css';

const ROLE_OPTIONS = {
  owner: [
    { value: 'supervisor', label: 'Supervisor' },
    { value: 'employee', label: 'Funcionário' },
  ],
  admin: [
    { value: 'owner', label: 'Owner' },
  ],
  super_admin: [
    { value: 'owner', label: 'Owner' },
  ],
};

const API_BASE_URL = 'http://127.0.0.1:8000';

const Cadastro = () => {
  const navigate = useNavigate();
  const [userRole, setUserRole] = useState('');
  const [formUsuario, setFormUsuario] = useState({
    nomeFuncionario: '',
    email: '',
    confirmaEmail: '',
    cargo: 'employee',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const allowedRoles = ROLE_OPTIONS[userRole] || [];
  const canInvite = allowedRoles.length > 0;

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const role = localStorage.getItem('userRole');
      if (!role) {
        navigate('/nao-autorizado');
        return;
      }

      setUserRole(role);
    }
  }, [navigate]);

  useEffect(() => {
    if (!userRole) {
      return;
    }

    if (!canInvite) {
      navigate('/nao-autorizado');
      return;
    }

    if (!allowedRoles.some((option) => option.value === formUsuario.cargo)) {
      setFormUsuario((prev) => ({
        ...prev,
        cargo: allowedRoles[0].value,
      }));
    }
  }, [userRole, canInvite, allowedRoles, formUsuario.cargo, navigate]);

  const getAuthToken = () => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('authToken');
    }
    return null;
  };

  const handleUsuarioChange = (e) => {
    const { name, value } = e.target;
    setFormUsuario((prev) => ({ ...prev, [name]: value }));
    setError('');
  };

  const handleCadastroUsuario = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (!canInvite) {
      setError('Você não tem permissão para cadastrar usuários.');
      setLoading(false);
      return;
    }

    const { nomeFuncionario, email, confirmaEmail, cargo } = formUsuario;

    if (!nomeFuncionario || !email || !confirmaEmail || !cargo) {
      setError('Todos os campos são obrigatórios.');
      setLoading(false);
      return;
    }

    if (email !== confirmaEmail) {
      setError('Os e-mails informados não coincidem.');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/convidar/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Token ${getAuthToken()}`,
        },
        body: JSON.stringify({
          usuario: nomeFuncionario,
          email,
          role: cargo,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        alert('Convite enviado com sucesso! O usuário receberá um email para completar o cadastro.');
        setFormUsuario({
          nomeFuncionario: '',
          email: '',
          confirmaEmail: '',
          cargo: allowedRoles[0]?.value || 'employee',
        });
      } else {
        setError(data.error || 'Erro ao enviar convite.');
      }
    } catch (err) {
      console.error('Erro:', err);
      setError('Erro ao conectar com o servidor. Verifique se o Django está rodando.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="registration-container">
      <section className="registration-card">
        <h2 className="card-title">Cadastro de Usuário</h2>
        {userRole && canInvite && (
          <p className="info-message">
            {userRole === 'owner'
              ? 'Como owner, você pode convidar supervisores e funcionários.'
              : 'Como administrador, você pode convidar owners.'}
          </p>
        )}
        {error && <div className="error-message">{error}</div>}
        <div className="form-row-flex">
          <div className="inputs-column">
            <div className="input-group">
              <label htmlFor="nome">Nome Completo</label>
              <input
                id="nome"
                type="text"
                name="nomeFuncionario"
                placeholder="Digite o nome do funcionário"
                value={formUsuario.nomeFuncionario}
                onChange={handleUsuarioChange}
                required
              />

              <label htmlFor="email">Email</label>
              <input
                id="email"
                type="email"
                name="email"
                placeholder="seu.email@exemplo.com"
                value={formUsuario.email}
                onChange={handleUsuarioChange}
                required
              />

              <label htmlFor="confirmaEmail">Confirmar Email</label>
              <input
                id="confirmaEmail"
                type="email"
                name="confirmaEmail"
                placeholder="Confirme seu email"
                value={formUsuario.confirmaEmail}
                onChange={handleUsuarioChange}
                required
              />

              <label htmlFor="cargo">Cargo</label>
              <select
                id="cargo"
                name="cargo"
                value={formUsuario.cargo}
                onChange={handleUsuarioChange}
                required
              >
                {allowedRoles.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <div className="button-column">
            <button className="button-user" onClick={handleCadastroUsuario} disabled={loading}>
              {loading ? 'Enviando convite...' : 'Enviar Convite'}
            </button>
          </div>
        </div>
      </section>

      <section className="table-section">
        <table className="custom-table">
          <thead>
            <tr>
              <th>Nome</th>
              <th>E-mail</th>
              <th>Cargo</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Exemplo Nome</td>
              <td>exemplo@email.com</td>
              <td>Supervisor</td>
            </tr>
          </tbody>
        </table>
      </section>
    </div>
  );
};

export default Cadastro;
