import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Cadastro.css';

const Cadastro = () => {
    const navigate = useNavigate();
    const [formUsuario, setFormUsuario] = useState({
        nomeFuncionario: '',
        email: '',
        senha: '',
        confirma_senha: ''
    });
    const [formEstufa, setFormEstufa] = useState({
        nomeEstufa: '',
        observacoes: ''
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleUsuarioChange = (e) => {
        const { name, value } = e.target;
        setFormUsuario(prev => ({ ...prev, [name]: value }));
        setError('');
    };

    const handleEstufaChange = (e) => {
        const { name, value } = e.target;
        setFormEstufa(prev => ({ ...prev, [name]: value }));
    };

    const handleCadastroUsuario = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        const { nomeFuncionario, email, senha, confirma_senha } = formUsuario;

        if (!nomeFuncionario || !email || !senha || !confirma_senha) {
            setError('Todos os campos são obrigatórios.');
            setLoading(false);
            return;
        }

        if (senha.length < 6) {
            setError('A senha deve ter pelo menos 6 caracteres.');
            setLoading(false);
            return;
        }

        try {
            const response = await fetch('http://127.0.0.1:8000/api/cadastro/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    usuario: nomeFuncionario,
                    email: email,
                    senha: senha,
                    confirma_senha: confirma_senha
                }),
            });

            const data = await response.json();

            if (response.ok) {
                alert('Usuário cadastrado com sucesso! Redirecionando para login...');
                setFormUsuario({
                    nomeFuncionario: '',
                    email: '',
                    senha: '',
                    confirma_senha: ''
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

    const handleCadastroEstufa = (e) => {
        e.preventDefault();
        console.log("Estufa: ", formEstufa.nomeEstufa);
        console.log("Observações: ", formEstufa.observacoes);
        alert("Cadastro de estufa realizado com sucesso!")
        setFormEstufa({
            nomeEstufa: '',
            observacoes: ''
        });
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
                            <input
                                id="nome"
                                type="text"
                                name="nomeFuncionario"
                                placeholder="Digite o nome do funcionário"
                                value={formUsuario.nomeFuncionario}
                                onChange={handleUsuarioChange}
                                required
                            />
                            <label htmlFor="email">Email</label>
                            <input
                                id="email"
                                type="email"
                                name="email"
                                placeholder="seu.email@exemplo.com"
                                value={formUsuario.email}
                                onChange={handleUsuarioChange}
                                required
                            />
                            <label htmlFor="senha">Senha</label>
                            <input
                                id="senha"
                                type="password"
                                name="senha"
                                placeholder="Digite uma senha (mín. 6 caracteres)"
                                value={formUsuario.senha}
                                onChange={handleUsuarioChange}
                                minLength={6}
                                required
                            />
                            <label htmlFor="confirma_senha">Confirmar Senha</label>
                            <input
                                id="confirma_senha"
                                type="password"
                                name="confirma_senha"
                                placeholder="Confirme sua senha"
                                value={formUsuario.confirma_senha}
                                onChange={handleUsuarioChange}
                                minLength={6}
                                required
                            />
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
            <hr className="divider" />
            <section className="registration-card">
                <h2 className="card-title">Cadastro de Estufa</h2>
                <div className="card-container">
                    <div className="form-row-flex">
                        <div className="inputs-column">
                            <div className="input-group">
                                <label htmlFor="nome-estufa">Nome da Estufa</label>
                                <input
                                    id="nome-estufa"
                                    type="text"
                                    name="nomeEstufa"
                                    placeholder="Digite o nome da estufa"
                                    value={formEstufa.nomeEstufa}
                                    onChange={handleEstufaChange}
                                />
                            </div>
                            <div className="input-group">
                                <label htmlFor="obs">Observações</label>
                                <textarea
                                    id="obs"
                                    name="observacoes"
                                    placeholder="Ex: Solo com alta umidade, quer atenção no dreno..."
                                    value={formEstufa.observacoes}
                                    onChange={handleEstufaChange}
                                    rows="4"
                                />
                            </div>
                        </div>
                        <div className="button-column">
                            <button className="button-user" onClick={handleCadastroEstufa}>Cadastrar</button>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    );
};

export default Cadastro;