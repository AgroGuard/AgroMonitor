import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Configuracoes.css';

const API_URL = 'http://127.0.0.1:8000/api';

const Configuracoes = () => {
    const navigate = useNavigate();
    const [mostrarModalSair, setMostrarModalSair] = useState(false);
    const [mostrarModalExcluir, setMostrarModalExcluir] = useState(false);
    const [perfil, setPerfil] = useState({
        nome: '',
        email: '',
        nivelAcesso: '',
        foto: null
    });
    const [previewUrl, setPreviewUrl] = useState(null);
    const [selectedPhoto, setSelectedPhoto] = useState(null);
    const [mensagem, setMensagem] = useState('');
    const [erro, setErro] = useState('');
    const [isSuperAdmin, setIsSuperAdmin] = useState(false);

    const getAuthToken = () => localStorage.getItem('authToken') || localStorage.getItem('token');

    const carregarPerfil = async () => {
        const token = getAuthToken();
        if (!token) {
            setErro('Usuário não autenticado.');
            return;
        }

        try {
            const response = await fetch(`${API_URL}/perfil/`, {
                headers: {
                    Authorization: `Token ${token}`
                }
            });
            const data = await response.json();

            if (!response.ok) {
                setErro(data.error || 'Não foi possível carregar o perfil.');
                return;
            }

            setPerfil({
                nome: data.usuario || '',
                email: data.email || '',
                nivelAcesso: data.role || '',
                foto: data.foto_url || null
            });
            setPreviewUrl(data.foto_url || null);
            setIsSuperAdmin(Boolean(data.is_super_admin));
        } catch (err) {
            console.error('Erro ao carregar perfil:', err);
            setErro('Erro ao carregar o perfil.');
        }
    };

    useEffect(() => {
        carregarPerfil();
    }, []);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setPerfil(prev => ({ ...prev, [name]: value }));
    };

    const handleChangeFoto = (e) => {
        const file = e.target.files && e.target.files[0];
        if (file) {
            setSelectedPhoto(file);
            setPreviewUrl(URL.createObjectURL(file));
        }
    };

    const handleSalvarPerfil = async () => {
        const token = getAuthToken();
        if (!token) {
            setErro('Usuário não autenticado.');
            return;
        }

        try {
            let body;
            const headers = {
                Authorization: `Token ${token}`
            };

            if (selectedPhoto) {
                body = new FormData();
                body.append('nome', perfil.nome);
                body.append('email', perfil.email);
                body.append('foto', selectedPhoto);
            } else {
                body = JSON.stringify({ nome: perfil.nome, email: perfil.email });
                headers['Content-Type'] = 'application/json';
            }

            const method = 'PATCH';
            const response = await fetch(`${API_URL}/perfil/`, {
                method,
                headers,
                body
            });
            const data = await response.json();

            if (!response.ok) {
                setMensagem('');
                setErro(data.error || 'Não foi possível atualizar o perfil.');
                return;
            }

            setErro('');
            setMensagem(data.message || 'Dados atualizados com sucesso.');
            setPerfil(prev => ({
                ...prev,
                nome: data.usuario || prev.nome,
                email: data.email || prev.email,
                nivelAcesso: data.role || prev.nivelAcesso,
                foto: data.foto_url || prev.foto
            }));
            setPreviewUrl(data.foto_url || previewUrl);
            if (data.foto_url) {
                setSelectedPhoto(null);
            }

            localStorage.setItem('userName', data.usuario || perfil.nome);
        } catch (err) {
            console.error('Erro ao atualizar o perfil:', err);
            setMensagem('');
            setErro('Erro ao atualizar o perfil.');
        }
    };

    const handleLogout = () => {
        localStorage.removeItem('user_id');
        localStorage.removeItem('userName');
        localStorage.removeItem('userRole');
        localStorage.removeItem('authToken');
        localStorage.removeItem('token');
        navigate('/');
    };

    const handleExcluirConta = async () => {
        const token = getAuthToken();
        if (!token) {
            setErro('Usuário não autenticado.');
            return;
        }

        try {
            const response = await fetch(`${API_URL}/perfil/`, {
                method: 'DELETE',
                headers: {
                    Authorization: `Token ${token}`
                }
            });
            const data = await response.json();

            if (!response.ok) {
                // Mensagem específica para super-admin
                if (response.status === 403 && data.error && data.error.toLowerCase().includes('super-admin')) {
                    setErro('Não é possível excluir o usuário super-admin.');
                } else {
                    setErro(data.error || 'Não foi possível excluir a conta.');
                }
                setMostrarModalExcluir(false);
                return;
            }

            // sucesso: limpar storage e redirecionar
            localStorage.removeItem('user_id');
            localStorage.removeItem('userName');
            localStorage.removeItem('userRole');
            localStorage.removeItem('authToken');
            localStorage.removeItem('token');
            navigate('/');
        } catch (err) {
            console.error('Erro ao excluir conta:', err);
            setErro('Erro ao excluir a conta.');
        }
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

            {mensagem && <p className="success-message">{mensagem}</p>}
            {erro && <p className="error-message">{erro}</p>}

            <div className="avatar-section">
                <div className="avatar-circle">
                    {previewUrl ? <img src={previewUrl} alt="perfil" /> : perfil.foto ? <img src={perfil.foto} alt="perfil" /> : <div className="avatar-placeholder"></div>}
                </div>
                <input
                    id="fotoPerfil"
                    type="file"
                    accept="image/*"
                    onChange={handleChangeFoto}
                    hidden
                />
                <label htmlFor="fotoPerfil" className="btn-alterar-foto">
                    Alterar foto de perfil
                </label>
            </div>
            <p className="permissao-texto">Nível de Permissão: {perfil.nivelAcesso}</p>
            <div className="config-form">
                <div className="input-row">
                    <label htmlFor="nome">Nome</label>
                    <div className="input-with-icon">
                        <input type="text" id="nome" name="nome" value={perfil.nome} placeholder="Digite seu nome" onChange={handleChange} />
                    </div>
                </div>
                <div className="input-row">
                    <label htmlFor="email">E-mail</label>
                    <div className="input-with-icon">
                        <input type="email" id="email" name="email" value={perfil.email} placeholder="exemplo@email.com" onChange={handleChange} />
                    </div>
                </div>
                <div className="input-row save-row">
                    <button className="btn-atualizar" type="button" onClick={handleSalvarPerfil}>
                        Salvar alterações
                    </button>
                </div>
            </div>
            <div className="danger-zone">
                {isSuperAdmin && (
                    <p className="super-admin-warning">Não é possível excluir o usuário super-admin.</p>
                )}
                <button className="btn-excluir" type="button" onClick={() => setMostrarModalExcluir(true)}>Excluir conta</button>
                {mostrarModalExcluir && (
                    <div className="modal-overlay">
                        <div className="modal-content">
                            <h3>Tem certeza que deseja excluir sua conta?</h3>
                            <div className="modal-buttons">
                                <button className="btn-confirmar" onClick={handleExcluirConta}>Excluir</button>
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
