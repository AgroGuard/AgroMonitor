import React, { useState, useEffect } from 'react'; // Adicionado useEffect
import { useNavigate } from 'react-router-dom';
import logoAgro from '../../assets/logoAgro.png';
import { Mail, Lock, Shield } from 'lucide-react';
import { Link } from 'react-router-dom';
import './Login.css';

const Login = () => {
    const navigate = useNavigate();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [verificationCode, setVerificationCode] = useState('');
    {/*const [segundos, setSegundos] = useState(0);
    const [isTimerActive, setIsTimerActive] = useState(false);

    useEffect(() => {
        let timer;
        if (isTimerActive && segundos > 0) {
            timer = setInterval(() => {
                setSegundos((prev) => prev - 1);
            }, 1000);
        } else if (segundos === 0) {
            setIsTimerActive(false);
            clearInterval(timer);
        }
        return () => clearInterval(timer);
    }, [isTimerActive, segundos]);

    const handleEnviarCodigo = () => {
        setSegundos(60);
        setIsTimerActive(true);
        console.log("Solicitando código para:", email);
    };*/}

   const handleSubmit = async (e) => {
    e.preventDefault(); 

    try {

        const response = await fetch('http://127.0.0.1:8000/api/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                password: password
            }),
        });

        // 2. Converte a resposta do servidor para JSON
        const data = await response.json();

        // 3. Verifica se o backend retornou sucesso (status 200)
        if (response.ok) {
            console.log("Login bem-sucedido:", data.message);
            localStorage.setItem('user_id', data.user_id);
            localStorage.setItem('userName', email);

            navigate('/dashboard'); // Redireciona para a tela principal das estufas
        } else {
            // 4. Caso o Django retorne erro
            alert(data.error || "Ocorreu um erro ao fazer login.");
        }
    } catch (error) {
        // 5. Caso o servidor esteja desligado ou haja erro de rede
        console.error("Erro de conexão:", error);
        alert("Não foi possível conectar ao servidor. Verifique se o Django está rodando.");
    }
};

    return (
        <div className="Login-container">
            <div className="login-form">
                <h2>Login</h2>
                <form onSubmit={handleSubmit}>
                    <div className="input-group">
                        <label htmlFor="email">E-mail</label>
                        <div className="input-with-icon">
                            <Mail className="icon" size={20} />
                            <input type="email" id="email" placeholder="exemplo@gmail.com" value={email} onChange={(e) => setEmail(e.target.value)} required />
                        </div>
                    </div>

                    <div className="input-group">
                        <label htmlFor="password">Senha</label>
                        <div className="input-with-icon">
                            <Lock className="icon" size={20} />
                            <input type="password" id="password" placeholder="Digite sua senha" value={password} onChange={(e) => setPassword(e.target.value)} required maxLength={12} minLength={6} />
                        </div>
                    </div>

                    {/*<div className="input-group">
                        <div className="label-container">
                            <label htmlFor="verificationCode">Código de Verificação</label>

                            {segundos > 0 ? (
                                <span className="resend-timer">Reenviar código em {segundos}s</span>
                            ) : (
                                <span className="resend-link" onClick={handleEnviarCodigo}>
                                    Enviar código
                                </span>
                            )}
                        </div> 

                        <div className="input-with-icon">
                            <Shield className="icon" size={20} />
                            <input
                                type="text"
                                id="verificationCode"
                                placeholder="Digite o código"
                                maxLength="6"
                                value={verificationCode}
                                onChange={(e) => setVerificationCode(e.target.value)}
                                required
                            />
                        </div>
                    </div>
                    */}

                    <Link to="/recuperar" className="forgot-password-link">Esqueci minha senha</Link>
                    <Link to="/cadastro" className="forgot-password-link">Criar conta</Link>
                    <button type="submit" className="button">Entrar</button>
                </form>
            </div>
            <div className="login-image">
                <img src={logoAgro} alt="Logo do Agromonitor" />
            </div>
        </div>
    );
};

export default Login;