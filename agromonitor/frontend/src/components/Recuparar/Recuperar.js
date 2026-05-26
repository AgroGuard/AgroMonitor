import React from 'react';
import logoAgro from '../../assets/logoAgro.png';
import { useNavigate } from 'react-router-dom';
import { Mail } from 'lucide-react';
import '../Login/Login.css';

const Recuperar = () => {
    const navigate = useNavigate();

    return (
        <div className="Login-container">
            <div className="login-form">
                <h2>Recuperar Senha</h2>
                <p>Insira seu e-mail.</p>
                <form onSubmit={() => navigate('/')}>
                    <div className="input-group">
                        <label>E-mail</label>
                        <div className="input-with-icon">
                            <Mail className="icon" size={20} />
                            <input type="email" placeholder="seuemail@exemplo.com" required />
                        </div>
                    </div>
                    <button type="submit" className="button">Enviar Link</button>
                    <button type="button" onClick={() => navigate('/')} className="forgot-password-link" style={{ border: 'none', background: 'none', cursor: 'pointer' }}>Voltar para o Login</button>
                </form>
            </div>
            <div className="login-image">
                <img src={logoAgro} alt="Logo do Agromonitor" />
            </div>
        </div>
    );
};

export default Recuperar;