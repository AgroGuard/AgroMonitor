import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Cadastro.css';

const Cadastro = () => {
    const navigate = useNavigate();
    const [formUsuario, setFormUsuario] = useState({
        nomeFuncionario: '',
        email: '',
        confirmaEmail: '', 
        cargo: 'Funcionario'
    });
    
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleUsuarioChange = (e) => {
        const { name, value } = e.target;
        setFormUsuario(prev => ({ ...prev, [name]: value }));
        setError('');
    };

    const handleCadastroUsuario = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        const { nomeFuncionario, email, confirmaEmail, cargo } = formUsuario;

        if (!nomeFuncionario || !email || !confirmaEmail || !cargo) {
            setError('Todos os campos são obrigatórios.');
            setLoading(false);
            return;
        }

        if (email !== confirmaEmail) {
            setError('Os e-mails informados não coincidem.');
            setLoading(false);
            return;
        }

        try {
            // Enviando os dados atualizados incluindo o cargo para o Django
            const response = await fetch('http://127.0.0.1:8000/api/cadastro/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    usuario: nomeFuncionario,
                    email: email,
                    cargo: cargo
                }),
            });

            const data = await response.json();

            if (response.ok) {
                alert('Usuário cadastrado com sucesso! Redirecionando para login...');
                setFormUsuario({
                    nomeFuncionario: '',
                    email: '',
                    confirmaEmail: '',
                    cargo: 'Funcionario'
                });
                setTimeout(() => navigate('/'), 2000);
            } else {
                setError(data.error || 'Erro ao cadastrar usuário.');
            }
        } catch (err) {
            console.error('Erro:', err);
            setError('Erro ao conectar com o servidor. Verifique se o Django está rodando.');
        } finally {
            setLoading(false);
        }
    };

    

    return (
        <div className="registration-container">
            <section className="registration-card">
                <h2 className="card-title">Cadastro de Usuário</h2>
                {error && <div className="error-message">{error}</div>}
                <div className="form-row-flex">
                    <div className="inputs-column">
                        <div className="input-group">
                            <label htmlFor="nome">Nome Completo</label>
                            <input id="nome" type="text" name="nomeFuncionario" placeholder="Digite o nome do funcionário" value={formUsuario.nomeFuncionario} onChange={handleUsuarioChange} required />
                            
                            <label htmlFor="email">Email</label>
                            <input id="email" type="email" name="email" placeholder="seu.email@exemplo.com" value={formUsuario.email} onChange={handleUsuarioChange} required />
                            
                            <label htmlFor="confirmaEmail">Confirmar Email</label>
                            <input id="confirmaEmail" type="email" name="confirmaEmail" placeholder="Confirme seu email" value={formUsuario.confirmaEmail} onChange={handleUsuarioChange} required />
                            
                            {/* NOVO CAMPO: SELEÇÃO DE CARGO */}
                            <label htmlFor="cargo">Cargo</label>
                            <select id="cargo" name="cargo" value={formUsuario.cargo} onChange={handleUsuarioChange} required>
                                <option value="Funcionario">Funcionário</option>
                                <option value="Supervisor">Supervisor</option>
                                <option value="Administrador">Administrador</option>
                            </select>
                        </div>
                    </div>
                    <div className="button-column">
                        <button
                            className="button-user"
                            onClick={handleCadastroUsuario}
                            disabled={loading}
                        >
                            {loading ? 'Cadastrando...' : 'Cadastrar'}
                        </button>
                    </div>
                </div>
            </section>
            
            <section className="table-section">
                <table className="custom-table">
                    <thead>
                        <tr>
                            <th>Nome</th>
                            <th>E-mail</th>
                            <th>Cargo</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Exemplo Nome</td>
                            <td>exemplo@email.com</td>
                            <td>Supervisor</td>
                        </tr>
                    </tbody>
                </table>
            </section>
        </div>
    );
};

export default Cadastro;