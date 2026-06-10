import React, { useState, useRef, useEffect } from 'react';
import './Dashboard.css';
import ClimaDashboard from '../Clima/ClimaDashboard';

const API_BASE_URL = 'http://127.0.0.1:8000';

const Dashboard = () => {
  const [noteText, setNoteText] = useState('');
  const [notes, setNotes] = useState([]);
  const [isNotesOpen, setIsNotesOpen] = useState(false);
  const messagesEndRef = useRef(null);
  const [isPumpOn, setIsPumpOn] = useState(false);
  const [isLightOn, setIsLightOn] = useState(false);
  const [isFanOn, setIsFanOn] = useState(false);
  const [pumpDevices, setPumpDevices] = useState([]);
  const [lightDevices, setLightDevices] = useState([]);
  const [fanDevices, setFanDevices] = useState([]);
  const [selectedPumpId, setSelectedPumpId] = useState('');
  const [selectedLightId, setSelectedLightId] = useState('');
  const [selectedFanId, setSelectedFanId] = useState('');
  const [tempMin, setTempMin] = useState('');
  const [tempMax, setTempMax] = useState('');
  const [humidity, setHumidity] = useState('');
  const [luminosity, setLuminosity] = useState('');
  const [co2, setCo2] = useState('');
  const [actionStatus, setActionStatus] = useState('');
  const [paramStatus, setParamStatus] = useState('');
  const [showLogoutModal, setShowLogoutModal] = useState(false);
  const [isSystemCritical] = useState(false);
  const [dashboardStats, setDashboardStats] = useState({});
  const [activityLogs, setActivityLogs] = useState([]);
  const [statsError, setStatsError] = useState('');
  const [isLoadingStats, setIsLoadingStats] = useState(false);
  const [estufas, setEstufas] = useState([]);
  const [selectedEstufaId, setSelectedEstufaId] = useState('');
  const [downloadStatus, setDownloadStatus] = useState('');
  const [isDownloadingReport, setIsDownloadingReport] = useState(false);
  const nomeUsuario = localStorage.getItem('userName') || 'Visitante';
  const userRole = (typeof window !== 'undefined') ? localStorage.getItem('userRole') : null;
  const isSuperAdmin = userRole === 'super_admin';
  const isEmployee = userRole === 'employee';
  const notesStorageKey = `agromonitor_notes_${nomeUsuario}`;

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [notes]);

  const loadLocalNotes = () => {
    const storedNotes = localStorage.getItem(notesStorageKey);
    if (storedNotes) {
      try {
        setNotes(JSON.parse(storedNotes));
      } catch (err) {
        console.error('Erro ao carregar anotações:', err);
      }
    }
  };

  const carregarNotas = async () => {
    const token = getAuthToken();
    if (!token) {
      loadLocalNotes();
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/clima/notes/`, {
        method: 'GET',
        headers: buildHeaders(),
      });

      if (!response.ok) {
        throw new Error('Falha ao carregar anotações do servidor');
      }

      const data = await response.json();
      setNotes(data);
    } catch (err) {
      console.error('Erro ao carregar anotações do servidor:', err);
      loadLocalNotes();
    }
  };

  useEffect(() => {
    carregarNotas();
    carregarAtuadores();
    if (isSuperAdmin) {
      carregarDashboardStats();
    } else {
      carregarEstufas();
    }
  }, []);

  const getAuthToken = () => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('authToken') || localStorage.getItem('token');
    }
    return null;
  };

  const buildHeaders = () => {
    const headers = { 'Content-Type': 'application/json' };
    const token = getAuthToken();
    if (token) {
      headers.Authorization = `Token ${token}`;
    }
    return headers;
  };

  const carregarAtuadores = async () => {
    try {
      const [pumpRes, lightRes, fanRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/sensores/dispositivos/?tipo=atuador_bomba`),
        fetch(`${API_BASE_URL}/api/sensores/dispositivos/?tipo=atuador_luz`),
        fetch(`${API_BASE_URL}/api/sensores/dispositivos/?tipo=atuador_ventilador`),
      ]);

      const [pumpData, lightData, fanData] = await Promise.all([
        pumpRes.json(),
        lightRes.json(),
        fanRes.json(),
      ]);

      setPumpDevices(pumpData.dispositivos || []);
      setLightDevices(lightData.dispositivos || []);
      setFanDevices(fanData.dispositivos || []);

      if (pumpData.dispositivos?.length) {
        setSelectedPumpId(pumpData.dispositivos[0].dispositivo_id);
      }
      if (lightData.dispositivos?.length) {
        setSelectedLightId(lightData.dispositivos[0].dispositivo_id);
      }
      if (fanData.dispositivos?.length) {
        setSelectedFanId(fanData.dispositivos[0].dispositivo_id);
      }
    } catch (err) {
      console.error('Erro ao carregar atuadores:', err);
    }
  };

  const carregarDashboardStats = async () => {
    setIsLoadingStats(true);
    try {
      const response = await fetch(`${API_BASE_URL}/dashboard/api/stats/`, {
        method: 'GET',
        headers: buildHeaders(),
      });
      if (!response.ok) {
        throw new Error('Falha ao carregar estatísticas de dashboard');
      }
      const payload = await response.json();
      if (!payload.success) {
        throw new Error(payload.error || 'Erro desconhecido');
      }
      setDashboardStats(payload.data || {});
      setActivityLogs(payload.data?.atividades_recentes || []);
      setStatsError('');
    } catch (err) {
      console.error('Erro ao carregar stats do dashboard:', err);
      setStatsError('Não foi possível carregar estatísticas do super admin.');
      setDashboardStats({});
      setActivityLogs([]);
    } finally {
      setIsLoadingStats(false);
    }
  };

  const carregarEstufas = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/estufas/`, {
        method: 'GET',
        headers: buildHeaders(),
      });

      if (!response.ok) {
        throw new Error('Falha ao carregar estufas.');
      }

      const data = await response.json();
      const listaEstufas = data.estufas || [];
      setEstufas(listaEstufas);
      if (listaEstufas.length > 0) {
        setSelectedEstufaId(listaEstufas[0].id);
      }
    } catch (err) {
      console.error('Erro ao carregar estufas:', err);
      setDownloadStatus('Erro ao carregar estufas para relatório.');
    }
  };

  const handleDownloadRelatorio = async () => {
    if (!selectedEstufaId) {
      setDownloadStatus('Selecione uma estufa para gerar o relatório.');
      return;
    }

    setIsDownloadingReport(true);
    setDownloadStatus('Gerando relatório mensal...');

    try {
      const response = await fetch(`${API_BASE_URL}/api/relatorios/estufa/${selectedEstufaId}/mensal/`, {
        method: 'GET',
        headers: buildHeaders(),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Não foi possível obter o relatório.');
      }

      const blob = await response.blob();
      const contentDisposition = response.headers.get('content-disposition') || '';
      let filename = 'relatorio-mensal.csv';
      const filenameMatch = contentDisposition.match(/filename\*=UTF-8''(.+)|filename="?([^";]+)"?/i);
      if (filenameMatch) {
        filename = decodeURIComponent(filenameMatch[1] || filenameMatch[2]);
      }

      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      setDownloadStatus('Relatório baixado com sucesso.');
    } catch (err) {
      console.error('Erro ao baixar relatório:', err);
      setDownloadStatus(`Falha ao baixar relatório: ${err.message}`);
    } finally {
      setIsDownloadingReport(false);
    }
  };

  const enviarComando = async (dispositivoId, comando, parametros = {}) => {
    if (!dispositivoId) {
      throw new Error('Dispositivo MQTT não configurado');
    }

    const response = await fetch(`${API_BASE_URL}/api/sensores/comando/`, {
      method: 'POST',
      headers: buildHeaders(),
      body: JSON.stringify({ dispositivo_id: dispositivoId, comando, parametros }),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || 'Erro ao enviar comando MQTT');
    }

    return data;
  };

  const handleTogglePump = async () => {
    const newState = !isPumpOn;
    const comando = newState ? 'ligar_bomba' : 'desligar_bomba';

    try {
      setActionStatus('Enviando comando para bomba...');
      await enviarComando(selectedPumpId, comando);
      setIsPumpOn(newState);
      setActionStatus(`Bomba ${newState ? 'ligada' : 'desligada'} com sucesso.`);
    } catch (err) {
      console.error(err);
      setActionStatus(`Falha ao enviar comando da bomba: ${err.message}`);
    }
  };

  const handleToggleLight = async () => {
    const newState = !isLightOn;
    const comando = newState ? 'ligar_luz' : 'desligar_luz';

    try {
      setActionStatus('Enviando comando para iluminação...');
      await enviarComando(selectedLightId, comando);
      setIsLightOn(newState);
      setActionStatus(`Iluminação ${newState ? 'ligada' : 'desligada'} com sucesso.`);
    } catch (err) {
      console.error(err);
      setActionStatus(`Falha ao enviar comando da iluminação: ${err.message}`);
    }
  };

  const handleToggleFan = async () => {
    const newState = !isFanOn;
    const comando = newState ? 'ligar_ventilador' : 'desligar_ventilador';

    try {
      setActionStatus('Enviando comando para ventilação...');
      await enviarComando(selectedFanId, comando);
      setIsFanOn(newState);
      setActionStatus(`Ventilação ${newState ? 'ligada' : 'desligada'} com sucesso.`);
    } catch (err) {
      console.error(err);
      setActionStatus(`Falha ao enviar comando da ventilação: ${err.message}`);
    }
  };

  const buildParametrosPayload = () => {
    const payload = {};
    if (tempMin !== '') payload.temperatura_minima = Number(tempMin);
    if (tempMax !== '') payload.temperatura_maxima = Number(tempMax);
    if (humidity !== '') payload.umidade = Number(humidity);
    if (luminosity !== '') payload.luminosidade = Number(luminosity);
    if (co2 !== '') payload.co2 = Number(co2);
    return payload;
  };

  const handleEnviarParametros = async () => {
    const parametros = buildParametrosPayload();
    const dispositivoId = selectedPumpId || selectedLightId || selectedFanId;

    if (!dispositivoId) {
      setParamStatus('Defina pelo menos um dispositivo MQTT para enviar parâmetros.');
      return;
    }

    if (Object.keys(parametros).length === 0) {
      setParamStatus('Preencha pelo menos um parâmetro para envio.');
      return;
    }

    try {
      setParamStatus('Enviando parâmetros via MQTT...');
      await enviarComando(dispositivoId, 'configurar_parametros', parametros);
      setParamStatus('Parâmetros enviados com sucesso ao ESP32.');
    } catch (err) {
      console.error(err);
      setParamStatus(`Erro ao enviar parâmetros: ${err.message}`);
    }
  };

  const saveNotes = (updatedNotes) => {
    try {
      localStorage.setItem(notesStorageKey, JSON.stringify(updatedNotes));
    } catch (err) {
      console.error('Erro ao salvar anotações:', err);
    }
  };

  const handleAddNote = async (e) => {
    e.stopPropagation();
    const texto = noteText.trim();
    if (!texto) {
      return;
    }

    const token = getAuthToken();
    if (token) {
      try {
        const response = await fetch(`${API_BASE_URL}/api/clima/notes/`, {
          method: 'POST',
          headers: buildHeaders(),
          body: JSON.stringify({ texto }),
        });
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.erro || 'Falha ao salvar anotação no servidor.');
        }

        const newNote = await response.json();
        const updatedNotes = [...notes, newNote];
        setNotes(updatedNotes);
        setNoteText('');
        return;
      } catch (err) {
        console.error('Erro ao salvar anotação no servidor:', err);
      }
    }

    const newNote = {
      id: Date.now(),
      texto,
      criado_em: new Date().toISOString(),
    };
    const updatedNotes = [...notes, newNote];
    setNotes(updatedNotes);
    saveNotes(updatedNotes);
    setNoteText('');
  };

  const toggleNotesPanel = () => {
    setIsNotesOpen(!isNotesOpen);
  };

  const handleLogout = () => {
    localStorage.removeItem('user_id');
    localStorage.removeItem('userName');
    localStorage.removeItem('userRole');
    localStorage.removeItem('authToken');
    localStorage.removeItem('token');
    window.location.href = '/';
  };

  return (
    <>
      <div className="dashboard-container">
        <div className="dashboard-alert">
          {isSystemCritical && (
            <div className="critical-alert-banner">
              <span className="alert-icon">⚠️</span>
              <p>ALERTA CRÍTICO: Temperatura acima de 38ºC na Estufa 01</p>
            </div>
          )}
        </div>
        <div className={`chat-fixed-container ${isNotesOpen ? 'open' : ''}`} onClick={toggleNotesPanel}>
        <div className="chat-fixed-header">
          <h3>Anotações</h3>
          <div className="chat-header-actions">
            <span>{isNotesOpen ? '-' : '+'}</span>
          </div>
        </div>
        <div className="chat-fixed-body" onClick={(e) => e.stopPropagation()}>
          <div className="chat-messages-placeholder">
            {notes.length === 0 ? (
              <div className="chat-message received">Nenhuma anotação ainda. Adicione uma abaixo.</div>
            ) : (
              notes.map((note) => (
                <div key={note.id} className="chat-message sent">
                  <strong>{new Date(note.criado_em || note.createdAt).toLocaleString()}</strong>
                  <p>{note.texto || note.text}</p>
                </div>
              ))
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="chat-fixed-input-area" onClick={(e) => e.stopPropagation()}>
            <textarea placeholder="Anote algo para consultar depois" value={noteText} onChange={(e) => setNoteText(e.target.value)} />
            <button className="send-button-fixed" onClick={handleAddNote}>Salvar</button>
          </div>
        </div>
      </div>
      <div className="welcome-container">
        <span className="welcome-text">Seja Bem-Vindo, {nomeUsuario}!</span>
      </div>
      <header className="dashboard-header">
        <h1>Painel de Controle</h1>
        <button className="logout-bnt-top" onClick={() => setShowLogoutModal(true)}>Sair</button>
      </header>

      {isSuperAdmin ? (
        <>
          <section className="admin-overview-grid">
            <div className="stat-card">
              <h3>Usuários em uso agora</h3>
              <p>{dashboardStats.usuarios_ativos_no_momento ?? '—'}</p>
              <span>{isLoadingStats ? 'Carregando...' : 'Baseado em atividade recente'}</span>
            </div>
            <div className="stat-card">
              <h3>Total de usuários cadastrados</h3>
              <p>{dashboardStats.total_usuarios ?? '—'}</p>
              <span>Todos os perfis registrados no sistema</span>
            </div>
            <div className="stat-card">
              <h3>Usuários ativos este mês</h3>
              <p>{dashboardStats.usuarios_ativos_no_mes ?? '—'}</p>
              <span>Último login no mês corrente</span>
            </div>
          </section>

          <section className="admin-log-section">
            <div className="log-header">
              <h2>Registro de log de atividades</h2>
              <p>Visualiza as ações recentes de outros usuários na plataforma.</p>
            </div>

            {statsError && <p className="error-message">{statsError}</p>}

            <div className="log-table-wrapper">
              <table className="log-table">
                <thead>
                  <tr>
                    <th>Usuário</th>
                    <th>Atividade</th>
                    <th>Descrição</th>
                    <th>Data</th>
                  </tr>
                </thead>
                <tbody>
                  {activityLogs.length > 0 ? (
                    activityLogs.map((log, index) => (
                      <tr key={`${log.usuario}-${index}`}>
                        <td>{log.usuario}</td>
                        <td>{log.atividade}</td>
                        <td>{log.descricao || '—'}</td>
                        <td>{log.data}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="4">Nenhuma atividade registrada de outros usuários ainda.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </section>
        </>
      ) : (
        <section className="stats-grid">
          <div className="stat-card">
            <h3>Temperatura</h3>
            <p>24°C</p>
            <span>Status: Ideal</span>
          </div>
          <div className="stat-card">
            <h3>Umidade Solo</h3>
            <p>65%</p>
            <span>Status: Estável</span>
          </div>
          <div className="stat-card">
            <h3>Luminosidade</h3>
            <p>80%</p>
            <span>Status: Alto</span>
          </div>
        </section>
      )}
      {!isSuperAdmin && <ClimaDashboard showControls={false} />}
      {!isSuperAdmin && (
        <div className="control-card">
          <div className="parameter-card">
            <h3>Relatório mensal da estufa</h3>
            <p>Baixe o relatório do mês atual para a estufa monitorada.</p>
            {estufas.length > 0 ? (
              <div className="device-select-row">
                <label>
                  Estufa monitorada
                  <select value={selectedEstufaId} onChange={(e) => setSelectedEstufaId(e.target.value)}>
                    {estufas.map((estufa) => (
                      <option key={estufa.id} value={estufa.id}>
                        {estufa.nome}
                      </option>
                    ))}
                  </select>
                </label>
              </div>
            ) : (
              <p>{downloadStatus || 'Carregando estufas associadas...'}</p>
            )}
            <button
              className="button-user"
              type="button"
              onClick={handleDownloadRelatorio}
              disabled={!selectedEstufaId || isDownloadingReport}
            >
              {isDownloadingReport ? 'Baixando relatório...' : 'Baixar relatório mensal'}
            </button>
            {downloadStatus && <p className="status-message">{downloadStatus}</p>}
          </div>
        </div>
      )}
      {!isSuperAdmin && (
        <div className="control-card">
          <div className="controls-container">
            <div className="actuator-settings">
              <div className="actuator-header">
                <h3>Controle de Atuadores</h3>
                <p>Os interruptores agora enviam comandos MQTT ao ESP32.</p>
              </div>

            <div className="actuator-row">
              <div>
                <h4>Bomba de Irrigação</h4>
                <span className="device-hint">{selectedPumpId ? `MQTT ID: ${selectedPumpId}` : 'Dispositivo não configurado'}</span>
              </div>
              <label className="switch">
                <input type="checkbox" checked={isPumpOn} onChange={handleTogglePump} />
                <span className="slider round"></span>
              </label>
            </div>

            <div className="actuator-row">
              <div>
                <h4>Iluminação</h4>
                <span className="device-hint">{selectedLightId ? `MQTT ID: ${selectedLightId}` : 'Dispositivo não configurado'}</span>
              </div>
              <label className="switch">
                <input type="checkbox" checked={isLightOn} onChange={handleToggleLight} disabled={!selectedLightId} />
                <span className="slider round"></span>
              </label>
            </div>

            <div className="actuator-row">
              <div>
                <h4>Ventilação</h4>
                <span className="device-hint">{selectedFanId ? `MQTT ID: ${selectedFanId}` : 'Dispositivo não configurado'}</span>
              </div>
              <label className="switch">
                <input type="checkbox" checked={isFanOn} onChange={handleToggleFan} disabled={!selectedFanId} />
                <span className="slider round"></span>
              </label>
            </div>

            {!isEmployee ? (
              <div className="parameter-card">
                <h3>Parâmetros MQTT</h3>
                <div className="parameter-grid">
                  <label>
                    Temperatura mínima
                    <input type="number" value={tempMin} onChange={(e) => setTempMin(e.target.value)} placeholder="°C" />
                  </label>
                  <label>
                    Temperatura máxima
                    <input type="number" value={tempMax} onChange={(e) => setTempMax(e.target.value)} placeholder="°C" />
                  </label>
                  <label>
                    Umidade
                    <input type="number" value={humidity} onChange={(e) => setHumidity(e.target.value)} placeholder="%" />
                  </label>
                  <label>
                    Luminosidade
                    <input type="number" value={luminosity} onChange={(e) => setLuminosity(e.target.value)} placeholder="%" />
                  </label>
                  <label>
                    CO2
                    <input type="number" value={co2} onChange={(e) => setCo2(e.target.value)} placeholder="ppm" />
                  </label>
                </div>
                <button className="button-user" type="button" onClick={handleEnviarParametros}>
                  Enviar parâmetros MQTT
                </button>
                {paramStatus && <p className="status-message">{paramStatus}</p>}
              </div>
            ) : (
              <p className="info-message">Você não tem permissão para alterar parâmetros da estufa.</p>
            )}

            {actionStatus && <p className="status-message">{actionStatus}</p>}
          </div>
        </div>
      </div>
      )}
      {showLogoutModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <p>Tem certeza que deseja sair?</p>
            <div className="modal-buttons">
              <button className="confirm-bnt" onClick={handleLogout}>Sim</button>
              <button className="cancel-bnt" onClick={() => setShowLogoutModal(false)}>Cancelar</button>
            </div>
          </div>
        </div>
      )}
      </div>
    </>
  );
};

export default Dashboard;
