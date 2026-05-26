import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Cadastro-estufa.css';

const CadastroEstufa = () => {

    const [formEstufa, setFormEstufa] = useState({
        nomeEstufa: '',
        observacoes: ''
    });

    const handleCadastroEstufa = async (e) => {
        e.preventDefault();
        console.log("Estufa: ", formEstufa.nomeEstufa);
        console.log("Observações: ", formEstufa.observacoes);

    };

    const handleEstufaChange = (e) => {
        const { name, value } = e.target;
        setFormEstufa(prev => ({ ...prev, [name]: value }));
    };


    return (

        <div className="registration-container">
            <section className="registration-card">
                <h2 className="card-title">Cadastro de Estufa</h2>

                <div className="form-row-flex">
                    <div className="inputs-column">
                        <div className="input-group">
                            <label htmlFor="nomeEstufa">Nome da Estufa</label>
                            <input
                                id="nomeEstufa"
                                type="text"
                                name="nomeEstufa"
                                placeholder="Digite o nome ou número da estufa"
                                value={formEstufa.nomeEstufa}
                                onChange={handleEstufaChange}
                                required
                            />

                            <label htmlFor="observacoes">Observações</label>
                            <textarea
                                id="observacoes"
                                name="observacoes"
                                placeholder="Adicione observações sobre a estufa (ex: tipo de cultura, localização)"
                                value={formEstufa.observacoes}
                                onChange={handleEstufaChange}
                                rows="4"
                            />
                        </div>
                    </div>

                    <div className="button-column">
                        <button
                            className="button-user"
                            onClick={handleCadastroEstufa}
                        >
                            Cadastrar
                        </button>
                    </div>
                </div>
            </section>

            <section className="table-section">
                <table className="custom-table">
                    <thead>
                        <tr>
                            <th>Nome da Estufa</th>
                            <th>Observações</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                           <td>Exemplo Nome</td>
                            <td>Tipo de cultura: Tomate, Localização: Setor A</td>
                        </tr>
                    </tbody>
                </table>
            </section>
        </div>
    );
};

export default CadastroEstufa;
