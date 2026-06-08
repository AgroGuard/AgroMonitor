import React, { useCallback, useEffect, useState } from 'react';
import './Cadastro-regiao.css';

const CadastroRegiao = () => {
  const [form, setForm] = useState({
    estado: '',
  });
  const [regioes, setRegioes] = useState([]);
  const [mensagem, setMensagem] = useState('');
  const [climaPrevisto, setClimaPrevisto] = useState('');

  const baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const carregarRegioes = useCallback(async () => {
    try {
      const response = await fetch(`${baseUrl}/api/clima/api/regioes/`);
      const data = await response.json();
      if (data.sucesso) setRegioes(data.regioes || []);
    } catch (error) {
      console.error(error);
    }
  }, [baseUrl]);

  useEffect(() => {
    carregarRegioes();
  }, [carregarRegioes]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${baseUrl}/api/clima/api/regioes/cadastrar/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ estado: form.estado }),
      });
      const data = await response.json();
      if (!response.ok || !data.sucesso) {
        setMensagem(data.erro || 'Não foi possível cadastrar a região.');
        return;
      }
      setMensagem('Região cadastrada com sucesso.');
      setForm({ estado: '' });
      setClimaPrevisto(data.regiao && data.regiao.clima_tag ? data.regiao.clima_tag : '');
      carregarRegioes();
    } catch (error) {
      setMensagem('Erro ao conectar com o backend.');
      console.error(error);
    }
  };

  return (
    <div className="registration-container">
      <section className="registration-card">
        <h2 className="card-title">Cadastro de Região para Clima</h2>
        <p className="subtitle">Cadastre a região da fazenda para exibir o clima na dashboard.</p>

        <form onSubmit={handleSubmit} className="region-form-grid">
          <label>
            Estado
            <select name="estado" value={form.estado} onChange={handleChange} required>
              <option value="">-- Selecione um estado --</option>
              <option value="AC">Acre (AC)</option>
              <option value="AL">Alagoas (AL)</option>
              <option value="AP">Amapá (AP)</option>
              <option value="AM">Amazonas (AM)</option>
              <option value="BA">Bahia (BA)</option>
              <option value="CE">Ceará (CE)</option>
              <option value="DF">Distrito Federal (DF)</option>
              <option value="ES">Espírito Santo (ES)</option>
              <option value="GO">Goiás (GO)</option>
              <option value="MA">Maranhão (MA)</option>
              <option value="MT">Mato Grosso (MT)</option>
              <option value="MS">Mato Grosso do Sul (MS)</option>
              <option value="MG">Minas Gerais (MG)</option>
              <option value="PA">Pará (PA)</option>
              <option value="PB">Paraíba (PB)</option>
              <option value="PR">Paraná (PR)</option>
              <option value="PE">Pernambuco (PE)</option>
              <option value="PI">Piauí (PI)</option>
              <option value="RJ">Rio de Janeiro (RJ)</option>
              <option value="RN">Rio Grande do Norte (RN)</option>
              <option value="RS">Rio Grande do Sul (RS)</option>
              <option value="RO">Rondônia (RO)</option>
              <option value="RR">Roraima (RR)</option>
              <option value="SC">Santa Catarina (SC)</option>
              <option value="SP">São Paulo (SP)</option>
              <option value="SE">Sergipe (SE)</option>
              <option value="TO">Tocantins (TO)</option>
            </select>
          </label>
          <button type="submit" className="button-user">Salvar Região</button>
        </form>
        {climaPrevisto && <p className="form-message">Clima previsto: {climaPrevisto}</p>}

        {mensagem && <p className="form-message">{mensagem}</p>}
      </section>

      <section className="table-section">
        <h3>Regiões cadastradas</h3>
        <table className="custom-table">
          <thead>
            <tr>
              <th>Nome</th>
              <th>Estado</th>
              <th>País</th>
              <th>Latitude</th>
              <th>Longitude</th>
            </tr>
          </thead>
          <tbody>
            {regioes.length === 0 ? (
              <tr>
                <td colSpan="5">Nenhuma região cadastrada ainda.</td>
              </tr>
            ) : (
              regioes.map((item) => (
                <tr key={item.id}>
                  <td>{item.nome}</td>
                  <td>{item.estado || '—'}</td>
                  <td>{item.pais || 'Brasil'}</td>
                  <td>{item.latitude}</td>
                  <td>{item.longitude}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </section>
    </div>
  );
};

export default CadastroRegiao;
