import React, { useState, useEffect } from 'react';

/**
 * Exemplo de integração da API de Clima no frontend React
 * 
 * Este arquivo mostra como usar os endpoints da API Clima
 * no seu componente React
 */

// ============================================
// Serviço de API de Clima
// ============================================

const climaService = {
  // URL base dinâmica que detecta ambiente
  get BASE_URL() {
    // Em desenvolvimento
    if (typeof window !== 'undefined' && window.location.hostname === 'localhost') {
      return 'http://localhost:8000/api/clima';
    }
    // Em produção - usar variável de ambiente
    const apiUrl = process.env.REACT_APP_API_URL || 'https://api.agromonitor.vercel.app/api/clima';
    return apiUrl;
  },
  
  // Configurar token de autenticação
  setAuthToken(token) {
    this.authToken = token;
    // Salvar token no localStorage para persistência
    if (typeof window !== 'undefined') {
      localStorage.setItem('authToken', token);
    }
  },
  
  // Obter token do localStorage
  getAuthToken() {
    if (typeof window !== 'undefined') {
      return this.authToken || localStorage.getItem('authToken');
    }
    return this.authToken;
  },
  
  // Headers padrão para requisições
  getHeaders() {
    const token = this.getAuthToken();
    const headers = {
      'Content-Type': 'application/json',
    };
    if (token) {
      headers['Authorization'] = `Token ${token}`;
    }
    return headers;
  },
  
  // ============ Localidades ============
  
  async obterLocalidades() {
    const response = await fetch(`${this.BASE_URL}/api/localidades/`, {
      headers: this.getHeaders()
    });
    return response.json();
  },
  
  async criarLocalidade(dados) {
    const response = await fetch(`${this.BASE_URL}/api/localidades/`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(dados)
    });
    return response.json();
  },
  
  async obterLocalidade(id) {
    const response = await fetch(`${this.BASE_URL}/api/localidades/${id}/`, {
      headers: this.getHeaders()
    });
    return response.json();
  },
  
  async atualizarLocalidade(id, dados) {
    const response = await fetch(`${this.BASE_URL}/api/localidades/${id}/`, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: JSON.stringify(dados)
    });
    return response.json();
  },
  
  // ============ Previsões ============
  
  async obterPrevisoes(filtros = {}) {
    const params = new URLSearchParams(filtros).toString();
    const url = params ? `${this.BASE_URL}/api/previsoes/?${params}` : `${this.BASE_URL}/api/previsoes/`;
    
    const response = await fetch(url, {
      headers: this.getHeaders()
    });
    return response.json();
  },
  
  async obterPrevisoesAtuais(localidadeId) {
    const response = await fetch(
      `${this.BASE_URL}/api/localidades/${localidadeId}/previsoes_atuais/`,
      { headers: this.getHeaders() }
    );
    return response.json();
  },
  
  async atualizarPrevisao(localidadeId) {
    const response = await fetch(
      `${this.BASE_URL}/api/localidades/${localidadeId}/atualizar_previsao/`,
      {
        method: 'POST',
        headers: this.getHeaders()
      }
    );
    return response.json();
  },
  
  async atualizarTodasPrevisoes() {
    const response = await fetch(
      `${this.BASE_URL}/api/localidades/atualizar_todas/`,
      {
        method: 'POST',
        headers: this.getHeaders()
      }
    );
    return response.json();
  },
  
  // ============ Alertas ============
  
  async obterAlertas(filtros = {}) {
    const params = new URLSearchParams(filtros).toString();
    const url = params ? `${this.BASE_URL}/api/alertas/?${params}` : `${this.BASE_URL}/api/alertas/`;
    
    const response = await fetch(url, {
      headers: this.getHeaders()
    });
    return response.json();
  },
  
  async obterAlertasLocalidade(localidadeId) {
    const response = await fetch(
      `${this.BASE_URL}/api/localidades/${localidadeId}/alertas/`,
      { headers: this.getHeaders() }
    );
    return response.json();
  },
  
  async desativarAlerta(alertaId) {
    const response = await fetch(
      `${this.BASE_URL}/api/alertas/${alertaId}/desativar/`,
      {
        method: 'POST',
        headers: this.getHeaders()
      }
    );
    return response.json();
  },
  
  // ============ Histórico ============
  
  async obterHistorico(localidadeId, dias = 30) {
    const response = await fetch(
      `${this.BASE_URL}/api/localidades/${localidadeId}/historico/?dias=${dias}`,
      { headers: this.getHeaders() }
    );
    return response.json();
  },
  
  // ============ Utilitários ============
  
  async obterResumo() {
    const response = await fetch(`${this.BASE_URL}/api/resumo/`);
    return response.json();
  },
  
  async sincronizar() {
    const response = await fetch(`${this.BASE_URL}/api/sincronizar/`, {
      method: 'POST'
    });
    return response.json();
  }
};

// ============================================
// Componentes React de Exemplo
// ============================================

/**
 * Componente para exibir previsão do tempo de uma localidade
 */
export function WidgetPrevisaoTempo({ localidadeId }) {
  const [previsao, setPrevisao] = useState(null);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState(null);
  
  useEffect(() => {
    carregarPrevisao();
    // Atualizar a cada 30 minutos
    const intervalo = setInterval(carregarPrevisao, 30 * 60 * 1000);
    
    return () => clearInterval(intervalo);
  }, [localidadeId]);
  
  const carregarPrevisao = async () => {
    try {
      setCarregando(true);
      const dados = await climaService.obterPrevisoesAtuais(localidadeId);
      setPrevisao(dados.previsao_atual);
      setErro(null);
    } catch (err) {
      setErro('Erro ao carregar previsão');
      console.error(err);
    } finally {
      setCarregando(false);
    }
  };
  
  if (carregando) return <div>Carregando previsão...</div>;
  if (erro) return <div style={{ color: 'red' }}>{erro}</div>;
  if (!previsao) return <div>Nenhuma previsão disponível</div>;
  
  return (
    <div className="widget-previsao">
      <h3>{previsao.localidade_nome}</h3>
      <div className="previsao-atual">
        <div className="temperatura">
          {previsao.temperatura_atual}°C
        </div>
        <div className="condicao">
          {previsao.descricao}
        </div>
        <div className="detalhes">
          <span>💧 Umidade: {previsao.umidade}%</span>
          <span>💨 Vento: {previsao.velocidade_vento} m/s</span>
          <span>🌧️ Chuva: {previsao.chance_chuva}%</span>
        </div>
      </div>
    </div>
  );
}

/**
 * Componente para exibir alertas climáticos
 */
export function WidgetAlertas({ localidadeId }) {
  const [alertas, setAlertas] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState(null);
  
  useEffect(() => {
    carregarAlertas();
    // Atualizar a cada 15 minutos
    const intervalo = setInterval(carregarAlertas, 15 * 60 * 1000);
    
    return () => clearInterval(intervalo);
  }, [localidadeId]);
  
  const carregarAlertas = async () => {
    try {
      setCarregando(true);
      const dados = await climaService.obterAlertasLocalidade(localidadeId);
      setAlertas(dados.alertas || []);
      setErro(null);
    } catch (err) {
      setErro('Erro ao carregar alertas');
      console.error(err);
    } finally {
      setCarregando(false);
    }
  };
  
  const handleDesativar = async (alertaId) => {
    try {
      await climaService.desativarAlerta(alertaId);
      carregarAlertas();
    } catch (err) {
      console.error('Erro ao desativar alerta', err);
    }
  };
  
  if (carregando) return <div>Carregando alertas...</div>;
  if (erro) return <div style={{ color: 'red' }}>{erro}</div>;
  
  return (
    <div className="widget-alertas">
      <h3>Alertas Climáticos ({alertas.length})</h3>
      {alertas.length === 0 ? (
        <p>Nenhum alerta ativo</p>
      ) : (
        <ul>
          {alertas.map(alerta => (
            <li key={alerta.id} className={`alerta-${alerta.severidade}`}>
              <div className="alerta-header">
                <strong>{alerta.tipo_alerta}</strong>
                <span className="severidade">{alerta.severidade}</span>
              </div>
              <p>{alerta.descricao}</p>
              <p className="recomendacoes">{alerta.recomendacoes}</p>
              <button onClick={() => handleDesativar(alerta.id)}>
                Desativar
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

/**
 * Componente para exibir previsão de 5 dias
 */
export function WidgetPrevisao5Dias({ localidadeId }) {
  const [previsoes, setPrevisoes] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState(null);
  
  useEffect(() => {
    carregarPrevisoes();
  }, [localidadeId]);
  
  const carregarPrevisoes = async () => {
    try {
      setCarregando(true);
      const dados = await climaService.obterPrevisoesAtuais(localidadeId);
      setPrevisoes(dados.previsoes_proximos_dias || []);
      setErro(null);
    } catch (err) {
      setErro('Erro ao carregar previsões');
      console.error(err);
    } finally {
      setCarregando(false);
    }
  };
  
  if (carregando) return <div>Carregando previsões...</div>;
  if (erro) return <div style={{ color: 'red' }}>{erro}</div>;
  
  // Agrupar por dia
  const previsoesPorDia = {};
  previsoes.forEach(p => {
    const data = new Date(p.data_hora).toLocaleDateString('pt-BR');
    if (!previsoesPorDia[data]) {
      previsoesPorDia[data] = [];
    }
    previsoesPorDia[data].push(p);
  });
  
  return (
    <div className="widget-previsao-5-dias">
      <h3>Previsão de 5 Dias</h3>
      <div className="dias">
        {Object.entries(previsoesPorDia).map(([data, prev]) => (
          <div key={data} className="dia">
            <h4>{data}</h4>
            <div className="previsoes-hora">
              {prev.map((p, idx) => (
                <div key={idx} className="previsao-hora">
                  <small>{new Date(p.data_hora).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}</small>
                  <strong>{p.temperatura_atual}°C</strong>
                  <small>{p.condicao_tempo}</small>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/**
 * Componente para exibir histórico climático
 */
export function WidgetHistorico({ localidadeId, dias = 30 }) {
  const [historico, setHistorico] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState(null);
  
  useEffect(() => {
    carregarHistorico();
  }, [localidadeId, dias]);
  
  const carregarHistorico = async () => {
    try {
      setCarregando(true);
      const dados = await climaService.obterHistorico(localidadeId, dias);
      setHistorico(dados.historico || []);
      setErro(null);
    } catch (err) {
      setErro('Erro ao carregar histórico');
      console.error(err);
    } finally {
      setCarregando(false);
    }
  };
  
  if (carregando) return <div>Carregando histórico...</div>;
  if (erro) return <div style={{ color: 'red' }}>{erro}</div>;
  
  return (
    <div className="widget-historico">
      <h3>Histórico Climático ({dias} dias)</h3>
      <table>
        <thead>
          <tr>
            <th>Data</th>
            <th>Temp. Mín.</th>
            <th>Temp. Máx.</th>
            <th>Temp. Méd.</th>
            <th>Umidade</th>
            <th>Precipitação</th>
          </tr>
        </thead>
        <tbody>
          {historico.map(h => (
            <tr key={h.id}>
              <td>{h.data}</td>
              <td>{h.temperatura_minima}°C</td>
              <td>{h.temperatura_maxima}°C</td>
              <td>{h.temperatura_media}°C</td>
              <td>{h.umidade_media}%</td>
              <td>{h.precipitacao_total}mm</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// ============================================
// Uso nos Componentes
// ============================================

/**
 * Exemplo de uso em um componente de Dashboard
 */
export function DashboardClima() {
  const localidadeId = 1; // ID da localidade desejada
  
  // Configurar token ao montar o componente
  useEffect(() => {
    const token = localStorage.getItem('authToken');
    if (token) {
      climaService.setAuthToken(token);
    }
  }, []);
  
  return (
    <div className="dashboard-clima">
      <h1>Monitoramento Climático</h1>
      
      <div className="widgets-container">
        <div className="widget">
          <WidgetPrevisaoTempo localidadeId={localidadeId} />
        </div>
        
        <div className="widget">
          <WidgetAlertas localidadeId={localidadeId} />
        </div>
        
        <div className="widget">
          <WidgetPrevisao5Dias localidadeId={localidadeId} />
        </div>
        
        <div className="widget">
          <WidgetHistorico localidadeId={localidadeId} dias={30} />
        </div>
      </div>
    </div>
  );
}

export default climaService;
