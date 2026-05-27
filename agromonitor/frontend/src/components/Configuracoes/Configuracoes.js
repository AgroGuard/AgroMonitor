import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Configuracoes.css';


const Configuracoes = () => {
    const navigate = useNavigate();
    const [mostrarModalSair, setMostrarModalSair] = useState(false);
    const [mostrarModalExcluir, setMostrarModalExcluir] = useState(false);
    const [perfil, setPerfil] = useState({
        nome: '',
        email: '',
        nivelAcesso: '', //vincular com o backend para ter o acesso real do usuário
        foto: null
    });
    const handleChange = (e) => {
        const { name, value } = e.target;
        setPerfil(prev => ({ ...prev, [name]: value }));
    };

    const handleSalvarCampo = (campo) => {
        console.log('Salvando imagem ${campo}:', perfil[campo]);
        //integração com back aq 
    }

    const handleLogout = () => {
    localStorage.removeItem('userName');
    localStorage.removeItem('token');
    window.location.href = '/';
  };

    return (
        <div className="config-container">
            <div className="config-header">
                <h2>Perfil e Conta</h2>
                <button className="btn-sair" onClick={() => setMostrarModalSair(true)}>Sair</button>
                {mostrarModalSair && (
                    <div className="modal-overlay">

                        <div className="modal-content">
                            <h3>Tem certeza que deseja sair?</h3>
                            <div className="modal-buttons">
                                <button className="btn-confirmar" onClick={handleLogout}>Sim</button>
                                <button className="btn-cancelar" onClick={() => setMostrarModalSair(false)}>Cancelar</button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
            <div className="avatar-section">
                <div className="avatar-circle">
                    {perfil.foto ? <img src={perfil.foto} alt="perfil" /> : <div className="avatar-placeholder"></div>}
                </div>
                <button className="btn-alterar-foto">
                    Alterar foto de perfil
                </button>
            </div>
            <p className="permissao-texto">Nível de Permissão: {perfil.nivelAcesso}</p>
            <div className="config-form">
                <div className="input-row">
                    <label htmlFor="nome">Nome</label>
                    <div className="input-with-icon">
                        <input type="text" id="nome" name="nome" value={perfil.nome} placeholder="Digite seu nome" onChange={handleChange} />
                        <button className="btn-atualizar" onClick={() => handleSalvarCampo('nome')} aria-label="Salvar nome">
                            Atualizar
                        </button>
                    </div>
                </div>
                <div className="input-row">
                    <label htmlFor="email">E-mail</label>
                    <div className="input-with-icon">
                        <input type="email" id="email" name="email" value={perfil.email} placeholder="exemplo@email.com" onChange={handleChange} />
                        <button className="btn-atualizar" onClick={() => handleSalvarCampo('email')} aria-label="Salvar email">
                            Atualizar
                        </button>
                    </div>
                </div>
            </div>
            <div className="danger-zone">
                <button className="btn-excluir" onClick={() => setMostrarModalExcluir(true)}>Excluir conta</button>
                {mostrarModalExcluir && (
                    <div className="modal-overlay">
                        <div className="modal-content">
                            <h3>Tem certeza que deseja excluir sua conta?</h3>
                            <div className="modal-buttons">
                                <button className="btn-confirmar" onClick={handleLogout}>Excluir</button>
                                <button className="btn-cancelar" onClick={() => setMostrarModalExcluir(false)}>Cancelar</button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Configuracoes;