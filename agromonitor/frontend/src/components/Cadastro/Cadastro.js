import React, { useState } from 'react';
import './Cadastro.css';

const Cadastro = () => {
    const [nomeFuncionario, setNomeFuncionario] = useState('');
    const [nomeEstufa, setNomeEstufa] = useState('');
    const [permissao, setPermissao] = useState('Funcionario');
    const [observacoes, setObservacoes] = useState('');
    const [telefone, setTelefone] = useState('');
    const handleCadastro = () => {
        console.log("Funcionario: ", nomeFuncionario);
        console.log("Estufa: ", nomeEstufa);
        console.log("Permissão: ", permissao);
        console.log("Observações: ", observacoes);

        alert("Cadastro realizado com sucesso!")
        setNomeEstufa('');
        setNomeFuncionario('');
        setPermissao('Funcionario');
        setObservacoes('');
    };
    return (
        <div className="registration-container">
            <section className="registration-card">
                <h2 className="card-title">Cadastro de Usuário</h2>
                <div className="form-row-flex">
                    <div className="inputs-column">
                        <div className="input-group">
                            <label htmlFor="nome">Nome Completo</label>
                            <input id="nome" type="text" placeholder="Digite o nome do funcionário" value={nomeFuncionario} onChange={(e) => setNomeFuncionario(e.target.value)} />
                            <label htmlFor="estufa">Nome da Estufa</label>
                            <input id="estufa" type="text" placeholder="Digite o nome da estufa" value={nomeEstufa} onChange={(e) => setNomeEstufa(e.target.value)} />
                            <label htmlFor="telefone">Número de Telefone</label>
                            <input id="telefone" type="text" placeholder="(xx) xxxxx-xxxx" value={telefone} onChange={(e) => setTelefone(e.target.value)} />
                        </div>

                        <div className="input-group">
                            <label htmlFor="permissao">Permissões</label>
                            <select id="permissao" value={permissao} onChange={(e) => setPermissao(e.target.value)}>
                                <option value="Funcionario">Funcionário</option>
                                <option value="Administrador">Administrador</option>
                            </select>
                        </div>
                    </div>
                    <div className="button-column">
                        <button className="button-user" onClick={handleCadastro}>Cadastrar</button>
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
                                <input id="nome-estufa" type="text" placeholder="Digite o nome da estufa" value={nomeEstufa} onChange={(e) => setNomeEstufa(e.target.value)} />
                            </div>
                            <div className="input-group">
                                <label htmlFor="obs">Observações</label>
                                <textarea id="obs" placeholder="Ex: Solo com alta umidade, quer atenção no dreno..." value={observacoes} onChange={(e) => setObservacoes(e.target.value)} rows="4" />
                            </div>
                        </div>
                        <div className="button-column">
                            <button className="button-user" onClick={handleCadastro}>Cadastrar</button>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    );
};

export default Cadastro;