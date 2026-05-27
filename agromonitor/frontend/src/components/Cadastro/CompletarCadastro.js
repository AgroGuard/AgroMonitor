import React, { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { buildUrl } from '../../services/api';
import './Cadastro.css';

const CompletarCadastro = () => {
  const { token } = useParams();
  const navigate = useNavigate();
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!password || !confirmPassword) {
      setError('Preencha os dois campos de senha.');
      return;
    }

    if (password !== confirmPassword) {
      setError('As senhas não coincidem.');
      return;
    }

    if (password.length < 6) {
      setError('A senha deve ter pelo menos 6 caracteres.');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(buildUrl('/api/completar-cadastro/'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token,
          senha: password,
          confirma_senha: confirmPassword,
        }),
      });

      const data = await response.json();
      if (response.ok) {
        setSuccess('Cadastro concluído com sucesso! Redirecionando para login...');
        setTimeout(() => navigate('/'), 2000);
      } else {
        setError(data.error || 'Erro ao concluir cadastro.');
      }
    } catch (err) {
      setError('Erro de conexão com o servidor.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="registration-container">
      <section className="registration-card">
        <h2 className="card-title">Completar Cadastro</h2>
        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}
        <form onSubmit={handleSubmit} className="input-group">
          <label htmlFor="password">Senha</label>
          <input
            id="password"
            type="password"
            placeholder="Digite sua senha"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            minLength={6}
            required
          />

          <label htmlFor="confirmPassword">Confirmar senha</label>
          <input
            id="confirmPassword"
            type="password"
            placeholder="Confirme sua senha"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            minLength={6}
            required
          />

          <button type="submit" className="button-user" disabled={loading}>
            {loading ? 'Finalizando...' : 'Finalizar cadastro'}
          </button>
        </form>
      </section>
    </div>
  );
};

export default CompletarCadastro;
