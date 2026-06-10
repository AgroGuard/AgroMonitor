import React, { useEffect, useState } from 'react';
import logoAgro from '../../assets/logoAgro.png';
import { useNavigate, useLocation, useParams } from 'react-router-dom';
import { Mail, Lock } from 'lucide-react';
import '../Login/Login.css';

const API_URL = 'http://127.0.0.1:8000/api';

const Recuperar = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const { token: tokenParam } = useParams();
    const params = new URLSearchParams(location.search);
    const token = tokenParam || params.get('token');

    const [email, setEmail] = useState('');
    const [novaSenha, setNovaSenha] = useState('');
    const [confirmaSenha, setConfirmaSenha] = useState('');
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const [tokenValido, setTokenValido] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (token) {
            validarToken();
        }
    }, [token]);

    const validarToken = async () => {
        setLoading(true);
        setError('');
        try {
            const response = await fetch(`${API_URL}/recuperar/validar/?token=${encodeURIComponent(token)}`);
            const data = await response.json();
            if (response.ok && data.valid) {
                setTokenValido(true);
            } else {
                setTokenValido(false);
                setError(data.error || 'Token inválido ou expirado.');
            }
        } catch (err) {
            setTokenValido(false);
            setError('Erro ao validar o token. Tente novamente mais tarde.');
        } finally {
            setLoading(false);
        }
    };

    const handleEnviarLink = async (e) => {
        e.preventDefault();
        setError('');
        setMessage('');
        setLoading(true);

        try {
            const response = await fetch(`${API_URL}/recuperar/solicitar/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email }),
            });

            const data = await response.json();
            if (response.ok) {
                setMessage(data.message || 'Verifique seu email para o link de recuperação.');
            } else {
                setError(data.error || 'Erro ao solicitar recuperação.');
            }
        } catch (err) {
            setError('Erro de conexão. Verifique o servidor.');
        } finally {
            setLoading(false);
        }
    };

    const handleResetarSenha = async (e) => {
        e.preventDefault();
        setError('');
        setMessage('');

        if (novaSenha !== confirmaSenha) {
            setError('As senhas não coincidem.');
            return;
        }

        if (novaSenha.length < 6) {
            setError('A senha deve ter pelo menos 6 caracteres.');
            return;
        }

        setLoading(true);
        try {
            const response = await fetch(`${API_URL}/recuperar/confirmar/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ token, nova_senha: novaSenha, confirma_senha: confirmaSenha }),
            });
            const data = await response.json();
            if (response.ok) {
                setMessage(data.message || 'Senha alterada com sucesso!');
                setTimeout(() => navigate('/'), 2000);
            } else {
                setError(data.error || 'Erro ao resetar senha.');
            }
        } catch (err) {
            setError('Erro de conexão. Verifique o servidor.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="Login-container">
            <div className="login-form">
                <h2>Recuperar Senha</h2>
                {token ? (
                    <>
                        {loading && <p>Validando token...</p>}
                        {tokenValido === false && (
                            <>
                                <p className="error-message">{error}</p>
                                <button type="button" onClick={() => navigate('/recuperar')} className="button">
                                    Voltar para solicitações
                                </button>
                            </>
                        )}
                        {tokenValido === true && (
                            <form onSubmit={handleResetarSenha}>
                                <div className="input-group">
                                    <label>Nova senha</label>
                                    <div className="input-with-icon">
                                        <Lock className="icon" size={20} />
                                        <input
                                            type="password"
                                            placeholder="Digite a nova senha"
                                            value={novaSenha}
                                            onChange={(e) => setNovaSenha(e.target.value)}
                                            required
                                            minLength={6}
                                        />
                                    </div>
                                </div>
                                <div className="input-group">
                                    <label>Confirmar senha</label>
                                    <div className="input-with-icon">
                                        <Lock className="icon" size={20} />
                                        <input
                                            type="password"
                                            placeholder="Confirme a nova senha"
                                            value={confirmaSenha}
                                            onChange={(e) => setConfirmaSenha(e.target.value)}
                                            required
                                            minLength={6}
                                        />
                                    </div>
                                </div>
                                <button type="submit" className="button" disabled={loading}>
                                    {loading ? 'Enviando...' : 'Redefinir senha'}
                                </button>
                            </form>
                        )}
                    </>
                ) : (
                    <form onSubmit={handleEnviarLink}>
                        <p>Insira seu e-mail para receber o link de recuperação.</p>
                        <div className="input-group">
                            <label>E-mail</label>
                            <div className="input-with-icon">
                                <Mail className="icon" size={20} />
                                <input
                                    type="email"
                                    placeholder="seuemail@exemplo.com"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                />
                            </div>
                        </div>
                        <button type="submit" className="button" disabled={loading}>
                            {loading ? 'Enviando...' : 'Enviar Link'}
                        </button>
                    </form>
                )}

                {message && <p className="success-message">{message}</p>}
                {error && <p className="error-message">{error}</p>}

                <button type="button" onClick={() => navigate('/')} className="forgot-password-link" style={{ border: 'none', background: 'none', cursor: 'pointer' }}>
                    Voltar para o Login
                </button>
            </div>
            <div className="login-image">
                <img src={logoAgro} alt="Logo do Agromonitor" />
            </div>
        </div>
    );
};

export default Recuperar;
