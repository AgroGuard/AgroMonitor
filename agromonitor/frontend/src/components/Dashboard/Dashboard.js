import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './Dashboard.css';

const Dashboard = () => {
  const [comment, setComment] = useState('');
  const [allComments, setAllComments] = useState([]);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const messagesEndRef = useRef(null);
  const videoRef = useRef(null);
  const [isPumpOn, setIsPumpOn] = useState(false);
  const [isLightOn, setIsLightOn] = useState(false);
  const [isFanOn, setIsFanOn] = useState(false);
  const navigate = useNavigate();
  const [showLogoutModal, setShowLogoutModal] = useState(false);
  const [isSystemCritical, setIsSystemCritical] = useState(false);
  const nomeUsuario = localStorage.getItem('userName') || 'Visitante';
  // const nomeUsuario = localStorage.getItem('user_name') || localStorage.getItem('user');
  // dps que criar a classe, substituir o nome do usuário pelo nome do funcionário logado, que deve ser salvo na classe no momento do login
  const verificarStatus = (temperaturaAtual) =>{
    if (temperaturaAtual > 35){
      return true;
    } else {
      return false;
    }
  };

  const handleLogout = () => {
    navigate('/');
  };

  const togglePump = () => {
    setIsPumpOn(!isPumpOn);
    //adicionar a lógica para enviar o comando para ligar/desligar a bomba
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [allComments]);

  const handleSendComment = (e) => {
    e.stopPropagation();
    if (comment.trim() !== '') {
      setAllComments([...allComments, comment]);
      setComment('');
    }
  };

  const toggleChat = () => {
    setIsChatOpen(!isChatOpen);
  };

  return (
    <>
      <div className="main-content">
        {isSystemCritical && (
          <div className="critical-alert-banner">
            <span className="alert-icon">⚠️</span>
            <p>ALERTA CRÍTICO: Temperatura acima de 38ºC na Estufa 01</p>
          </div>
        )}
      </div>
      <div className={`chat-fixed-container ${isChatOpen ? 'open' : ''}`} onClick={toggleChat}>
        <div className="chat-fixed-header">
          <h3>Chat</h3>
          <div className="chat-header-actions">
            <span>{isChatOpen ? '-' : '+'}</span>
          </div>
        </div>
        <div className="chat-fixed-body">
          <div className="chat-messages-placeholder">
            {allComments.map((msg, index) => (
              <div key={index} className="chat-message sent">
                {msg}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          <div className="chat-fixed-input-area" onClick={(e) => e.stopPropagation()}>
            <textarea placeholder="Deixe seu comentário" value={comment} onChange={(e) => setComment(e.target.value)} />
            <button className="send-button-fixed" onClick={handleSendComment}>Enviar</button>
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
      <div className="camera-section">
        <h2>Monitoramento em Tempo Real</h2>
        <div className="camera-grid">
          <div className="camera-card">
            <div className="video-placeholder">
              <span>Aguardando sinal da câmera...</span>
            </div>
            <div className="camera-info">
              <span>Estufa 01 - Lado Norte</span>
              <span className="live-indicator">AO VIVO</span>
            </div>
          </div>
        </div>
      </div>
      <div className={`control-card ${isPumpOn ? 'active' : ''}`}>
        <div className="controls-container">
          <div className="card-header">
            <h3>Bomba de Irrigação</h3>
          </div>
          <label className="switch">
            <input type="checkbox" checked={isPumpOn} onChange={() => setIsPumpOn(!isPumpOn)} />
            <span className="slider round"></span>
          </label>
          <div className="card-header">
            <h3>Iluminação</h3>
            <label className="switch">
              <input type="checkbox" checked={isLightOn} onChange={() => setIsLightOn(!isLightOn)} />
              <span className="slider round"></span>
            </label>
          </div>
          <div className="card-header">
            <h3>Ventilação</h3>
            <label className="switch">
              <input type="checkbox" checked={isFanOn} onChange={() => setIsFanOn(!isFanOn)} />
              <span className="slider round"></span>
            </label>
          </div>
        </div>
      </div>
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
    </>
  );
};

export default Dashboard;