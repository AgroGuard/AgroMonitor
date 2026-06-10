import React, { useEffect, useState } from 'react';
import climaService from '../../services/climaService';
import CadastroRegiao from '../Cadastro/Cadastro-Regiao';

const ClimaDashboard = ({ showControls = true }) => {
  const [regioes, setRegioes] = useState([]);
  const [regiaoSelecionada, setRegiaoSelecionada] = useState(null);
  const [climaResumo, setClimaResumo] = useState(null);
  const [previsaoAtual, setPrevisaoAtual] = useState(null);
  const [alertas, setAlertas] = useState([]);
  const [loadingResumo, setLoadingResumo] = useState(true);
  const [loadingDetalhes, setLoadingDetalhes] = useState(false);
  const [erro, setErro] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('authToken');
    if (token) {
      climaService.setAuthToken(token);
    }
    carregarRegioes();
    carregarResumo();
  }, []);

  const carregarRegioes = async () => {
    try {
      const data = await climaService.obterLocalidades();
      if (Array.isArray(data) && data.length > 0) {
        setRegioes(data);
        setRegiaoSelecionada(data[0]);
        carregarDetalhes(data[0].id);
      } else {
        setRegioes([]);
      }
    } catch (err) {
      console.error(err);
      setErro('Falha ao carregar regiões de clima.');
    }
  };

  const carregarResumo = async () => {
    setLoadingResumo(true);
    try {
      const data = await climaService.obterResumo();
      if (data?.sucesso) {
        setClimaResumo(data.localidades?.[0] || null);
      } else {
        setErro(data?.erro || 'Não foi possível carregar o resumo do clima.');
      }
    } catch (err) {
      console.error(err);
      setErro('Falha ao carregar o resumo do clima.');
    } finally {
      setLoadingResumo(false);
    }
  };

  const carregarDetalhes = async (localidadeId, forcarAtualizacao = false) => {
    if (!localidadeId) {
      return;
    }

    setLoadingDetalhes(true);
    setPrevisaoAtual(null);
    setAlertas([]);
    setErro('');

    try {
      const data = await climaService.obterPrevisoesAtuais(localidadeId);
      if (!data) {
        throw new Error('Resposta inválida do servidor.');
      }

      if (data.sucesso === false || data.erro) {
        const mensagem = data.erro || data.detail || 'Falha ao carregar detalhes da região.';
        if (mensagem.toLowerCase().includes('token') || mensagem.toLowerCase().includes('autentic')) {
          climaService.clearAuthToken();
        }
        setErro(mensagem);
        return;
      }

      if (!data.previsao_atual && !forcarAtualizacao) {
        await handleAtualizarPrevisao(localidadeId, true);
        return;
      }

      setPrevisaoAtual(data.previsao_atual);
      setAlertas(data.alertas || []);
    } catch (err) {
      console.error(err);
      setErro(err.message || 'Falha ao carregar detalhes da região.');
    } finally {
      setLoadingDetalhes(false);
    }
  };

  const handleSelecionarRegiao = (event) => {
    const regionId = Number(event.target.value);
    const region = regioes.find((item) => item.id === regionId);
    setRegiaoSelecionada(region);
    carregarDetalhes(regionId);
  };

  const handleAtualizarPrevisao = async (localidadeId = regiaoSelecionada?.id, skipRefresh = false) => {
    if (!localidadeId) {
      return;
    }

    const token = localStorage.getItem('authToken');
    if (!token) {
      setErro('Faça login para atualizar a previsão.');
      return;
    }

    setLoadingDetalhes(true);
    setErro('');

    try {
      const data = await climaService.atualizarPrevisao(localidadeId);
      if (data?.sucesso) {
        if (!skipRefresh) {
          await carregarDetalhes(localidadeId, true);
        }
        return;
      }

      const mensagem = data?.erro || data?.detail || 'Não foi possível atualizar a previsão.';
      if (mensagem.toLowerCase().includes('token') || mensagem.toLowerCase().includes('autentic')) {
        climaService.clearAuthToken();
      }
      setErro(mensagem);
    } catch (err) {
      console.error(err);
      setErro(err.message || 'Erro ao atualizar a previsão de clima.');
    } finally {
      setLoadingDetalhes(false);
    }
  };

  const [showCadastro, setShowCadastro] = useState(false);

  return (
    <section className="weather-section">
      <div className="weather-header">
        <div>
          <h2>Monitoramento Climático</h2>
          <p>
            {regiaoSelecionada
              ? `Exibindo clima para ${regiaoSelecionada.nome}`
              : 'Selecione uma região para ver os dados climáticos.'}
          </p>
        </div>
        <div className="weather-actions">
          <label htmlFor="regiao-clima">Região</label>
          <select
            id="regiao-clima"
            value={regiaoSelecionada?.id || ''}
            onChange={handleSelecionarRegiao}
          >
            {regioes.length === 0 ? (
              <option value="">Nenhuma região cadastrada</option>
            ) : (
              regioes.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.nome} {item.estado ? `- ${item.estado}` : ''}
                </option>
              ))
            )}
          </select>
          {showControls && (
            <>
              <button className="button" type="button" onClick={handleAtualizarPrevisao} disabled={loadingDetalhes || !regiaoSelecionada}>
                {loadingDetalhes ? 'Atualizando...' : 'Atualizar previsão'}
              </button>
              <button className="button secondary" type="button" onClick={() => setShowCadastro(!showCadastro)}>
                {showCadastro ? 'Fechar cadastro' : 'Cadastrar Região'}
              </button>
            </>
          )}
        </div>
      </div>

      {erro && <div className="error-message">{erro}</div>}

      <div className="weather-grid">
        <article className="weather-card highlight">
          <h3>Resumo</h3>
          {loadingResumo ? (
            <p>Carregando resumo...</p>
          ) : climaResumo ? (
            <>
              <p>{climaResumo.nome}</p>
              <p>Alertas: {climaResumo.total_alertas ?? 0}</p>
              <p>Latitude: {climaResumo.latitude}</p>
              <p>Longitude: {climaResumo.longitude}</p>
            </>
          ) : (
            <p>Resumo do clima indisponível</p>
          )}
        </article>

        <article className="weather-card">
          <h3>Previsão atual</h3>
          {loadingDetalhes ? (
            <p>Carregando...</p>
          ) : previsaoAtual ? (
            <>
              <p className="weather-value">{previsaoAtual.temperatura_atual ?? '—'}°C</p>
              <span>{previsaoAtual.descricao || previsaoAtual.condicao_tempo || '—'}</span>
              <div className="weather-details">
                <span>Umidade: {previsaoAtual.umidade ?? '—'}%</span>
                <span>Vento: {previsaoAtual.velocidade_vento ?? '—'} m/s</span>
                <span>Chuva: {previsaoAtual.chance_chuva ?? '—'}%</span>
              </div>
            </>
          ) : (
            <p>Selecione uma região para ver a previsão atual.</p>
          )}
        </article>

        <article className="weather-card">
          <h3>Alertas ativos</h3>
          {loadingDetalhes ? (
            <p>Carregando alertas...</p>
          ) : alertas.length > 0 ? (
            <ul>
              {alertas.slice(0, 3).map((alerta) => (
                <li key={alerta.id}>
                  <strong>{alerta.tipo_alerta}</strong> — {alerta.descricao}
                </li>
              ))}
            </ul>
          ) : (
            <p>Nenhum alerta ativo</p>
          )}
        </article>
      </div>
      {showControls && showCadastro && (
        <div className="cadastro-section">
          <CadastroRegiao />
        </div>
      )}
    </section>
  );
};

export default ClimaDashboard;
