import React from 'react';
import './Termos.css';

const Termos = () => {
    return(
        <div className="termos-container">
            <section className="termos-section">
                <h2>Políticas de Privacidade</h2>
                <p>
1. Informações Gerais

A presente Política de Privacidade tem como finalidade estabelecer, de forma clara e transparente, as regras referentes à coleta, ao uso, ao armazenamento, ao tratamento e à proteção dos dados pessoais dos usuários que acessam o sistema Agro Monitor, solução desenvolvida para monitoramento e automação de estufas agrícolas utilizando tecnologia IoT baseada no microcontrolador ESP32. O documento busca garantir conformidade com a Lei Geral de Proteção de Dados Pessoais (Lei nº 13.709/2018), bem como com o Marco Civil da Internet (Lei nº 12.965/2014), assegurando aos usuários seus direitos e a adequada proteção dos dados.

Esta política integra a documentação técnica do Projeto Integrado de Segurança da Informação e aplica-se a todos os usuários que realizarem cadastro, login ou acessarem o dashboard web do Agro Monitor, por meio do qual são exibidas as informações coletadas pelos sensores instalados na estufa.

2. Formas de Coleta de Dados Pessoais

O Agro Monitor coleta dados pessoais das seguintes formas:

a) Fornecimento direto pelo usuário: no momento do cadastro, mediante fornecimento de e-mail, nome de usuário e senha.
b) Registros técnicos do sistema: logs vinculados ao usuário logado, associados a ações realizadas na plataforma, como alterações de parâmetros e acionamento manual de automações.

Nenhum dado sensível é coletado ou solicitado pelo sistema.

3. Dados Pessoais Coletados

O Agro Monitor poderá coletar e armazenar:

Dados de identificação: e-mail e nome de usuário;

Credenciais: senha protegida por hashing seguro com salt;

Dados de auditoria: registros técnicos ligados às ações do usuário durante o uso da plataforma.

Dados ambientais coletados pelos sensores não constituem dados pessoais.

4. Finalidade do Tratamento dos Dados

Os dados pessoais coletados pelo Agro Monitor têm finalidade exclusiva de:

Permitir autenticação segura no sistema;

Garantir controle de acesso e níveis de permissão;

Registrar histórico de ações para auditoria e segurança;

Aperfeiçoar o funcionamento e a estabilidade da aplicação;

Assegurar rastreabilidade de eventos e operações do sistema.

Os tratamentos respeitam os princípios de finalidade, necessidade, adequação, segurança e transparência previstos na LGPD.

5. Armazenamento, Retenção e Exclusão dos Dados

Os dados pessoais são armazenados em banco de dados protegido, acessível somente a usuários autorizados com perfil administrativo. As informações permanecem armazenadas enquanto a conta do usuário estiver ativa ou enquanto houver necessidade técnica ou legal.

A exclusão dos dados poderá ser solicitada pelo usuário. Após a exclusão, somente permanecerão armazenados dados cuja retenção seja obrigatória por lei ou essenciais para segurança e auditoria, conforme prevê a LGPD.

6. Medidas de Segurança Adotadas

O Agro Monitor adota as seguintes medidas de segurança:

Criptografia TLS/HTTPS na comunicação;

Hashing de senhas com salt (bcrypt, Argon2 ou equivalente);

Autenticação em dois fatores para perfis administrativos;

Controle de acesso baseado em papéis;

Registro completo de logs de auditoria;

Bloqueio temporário após tentativas excessivas de login;

Proteção física da unidade ESP32 e demais componentes.

Não nos responsabilizamos por incidentes decorrentes de compartilhamento voluntário de credenciais pelo usuário.

7. Compartilhamento dos Dados Pessoais

Os dados pessoais tratados pelo Agro Monitor não são compartilhados com terceiros.
Somente haverá compartilhamento mediante obrigação legal, determinação judicial ou solicitação expressa do titular.

8. Cookies e Dados de Navegação

O dashboard utiliza cookies estritamente funcionais para manter a sessão ativa durante o uso. Eles não armazenam dados sensíveis. A desativação desses cookies pode prejudicar o funcionamento correto da plataforma.

9. Consentimento

Ao criar uma conta e utilizar o Agro Monitor, o usuário manifesta seu consentimento com esta Política de Privacidade e autoriza o tratamento de seus dados pessoais, conforme descrito neste documento.

O usuário pode solicitar revisão, correção, atualização ou exclusão de seus dados a qualquer momento.

10. Alterações desta Política

A Política de Privacidade poderá ser atualizada conforme mudanças no sistema, exigências legais ou melhorias de segurança. Recomenda-se consulta periódica a esta seção.

11. Jurisdição

Para dirimir eventuais controvérsias relacionadas a esta política, aplica-se a legislação brasileira, sendo eleito o foro da comarca vinculada à instituição responsável pelo desenvolvimento do Agro Monitor.</p>
            </section>
            <section className="termos-section">
                <h2>Termos de Uso</h2>
                <p>O AgroMonitor é uma plataforma desenvolvida para monitoramento inteligente de ambientes agrícolas por meio de tecnologias de Internet das Coisas (IoT), permitindo o acompanhamento em tempo real de sensores ambientais, automação de equipamentos e gerenciamento remoto de estufas agrícolas. 

Ao acessar ou utilizar o sistema AgroMonitor, o usuário declara ter lido, compreendido e aceitado integralmente este Termo de Uso e a Política de Privacidade da plataforma. 

O sistema possui como finalidade oferecer uma plataforma acessível para monitoramento ambiental em tempo real, controle de sensores e atuadores, automação de irrigação, ventilação e iluminação, registro histórico de dados, geração de alertas e notificações, gerenciamento remoto de estufas agrícolas e apoio à tomada de decisão agrícola baseada em dados. 

A plataforma disponibiliza funcionalidades como cadastro e autenticação de usuários, criação e gerenciamento de estufas, painel de monitoramento em tempo real, controle manual de atuadores, configuração personalizada de parâmetros ambientais, criação de subusuários com diferentes permissões, histórico de leituras dos sensores, alertas de falhas e manutenção preventiva, área de comentários e registros operacionais, integração com sensores e dispositivos IoT e integração com APIs externas de dados agrícolas e climáticos. 

O usuário compromete-se a fornecer informações verdadeiras, manter o sigilo de suas credenciais de acesso, utilizar o sistema apenas para fins lícitos e não realizar tentativas de invasão ou exploração de vulnerabilidades. 

O AgroMonitor compromete-se a tratar os dados pessoais em conformidade com a Lei Geral de Proteção de Dados Pessoais (Lei nº 13.709/2018) e com o Marco Civil da Internet (Lei nº 12.965/2014). O sistema adota medidas técnicas e administrativas para proteção dos dados, incluindo comunicação criptografada via HTTPS/TLS, controle de acesso por permissões, registro de logs e monitoramento de segurança. 

O sistema utiliza tecnologias como React, Django, PostgreSQL, Supabase, Vercel, Render, comunicação MQTT e dispositivos ESP32 configurados com MicroPython. 

Este Termo poderá ser alterado a qualquer momento para atualização de funcionalidades, adequação legal ou melhorias na plataforma. 

2 POLÍTICA DE PRIVACIDADE 

POLÍTICA DE PRIVACIDADE – AGRO MONITOR 
1. Informações Gerais 

A presente Política de Privacidade tem como finalidade estabelecer, de forma clara e transparente, as regras referentes à coleta, ao uso, ao armazenamento, ao tratamento e à proteção dos dados pessoais dos usuários que acessam o sistema Agro Monitor, solução desenvolvida para monitoramento e automação de estufas agrícolas utilizando tecnologia IoT baseada no microcontrolador ESP32. O documento busca garantir conformidade com a Lei Geral de Proteção de Dados Pessoais (Lei nº 13.709/2018), bem como com o Marco Civil da Internet (Lei nº 12.965/2014), assegurando aos usuários seus direitos e a adequada proteção dos dados. 

Esta política integra a documentação técnica do Projeto Integrado de Segurança da Informação e aplica-se a todos os usuários que realizarem cadastro, login ou acessarem o dashboard web do Agro Monitor, por meio do qual são exibidas as informações coletadas pelos sensores instalados na estufa. 

2. Formas de Coleta de Dados Pessoais 

O Agro Monitor coleta dados pessoais das seguintes formas: 

a) Fornecimento direto pelo usuário: no momento do cadastro, mediante fornecimento de e-mail, nome de usuário e senha. 
b) Registros técnicos do sistema: logs vinculados ao usuário logado, associados a ações realizadas na plataforma, como alterações de parâmetros e acionamento manual de automações. 

Nenhum dado sensível é coletado ou solicitado pelo sistema. 

3. Dados Pessoais Coletados 

O Agro Monitor poderá coletar e armazenar: 

Dados de identificação: e-mail e nome de usuário; 

Credenciais: senha protegida por hashing seguro com salt; 

Dados de auditoria: registros técnicos ligados às ações do usuário durante o uso da plataforma. 

Dados ambientais coletados pelos sensores não constituem dados pessoais. 

4. Finalidade do Tratamento dos Dados 

Os dados pessoais coletados pelo Agro Monitor têm finalidade exclusiva de: 

Permitir autenticação segura no sistema; 

Garantir controle de acesso e níveis de permissão; 

Registrar histórico de ações para auditoria e segurança; 

Aperfeiçoar o funcionamento e a estabilidade da aplicação; 

Assegurar rastreabilidade de eventos e operações do sistema. 

Os tratamentos respeitam os princípios de finalidade, necessidade, adequação, segurança e transparência previstos na LGPD. 

5. Armazenamento, Retenção e Exclusão dos Dados 

Os dados pessoais são armazenados em banco de dados protegido, acessível somente a usuários autorizados com perfil administrativo. As informações permanecem armazenadas enquanto a conta do usuário estiver ativa ou enquanto houver necessidade técnica ou legal. 

A exclusão dos dados poderá ser solicitada pelo usuário. Após a exclusão, somente permanecerão armazenados dados cuja retenção seja obrigatória por lei ou essenciais para segurança e auditoria, conforme prevê a LGPD. 

6. Medidas de Segurança Adotadas 

O Agro Monitor adota as seguintes medidas de segurança: 

Criptografia TLS/HTTPS na comunicação; 

Hashing de senhas com salt (bcrypt, Argon2 ou equivalente); 

Autenticação em dois fatores para perfis administrativos; 

Controle de acesso baseado em papéis; 

Registro completo de logs de auditoria; 

Bloqueio temporário após tentativas excessivas de login; 

Proteção física da unidade ESP32 e demais componentes. 

Não nos responsabilizamos por incidentes decorrentes de compartilhamento voluntário de credenciais pelo usuário. 

7. Compartilhamento dos Dados Pessoais 

Os dados pessoais tratados pelo Agro Monitor não são compartilhados com terceiros. 
Somente haverá compartilhamento mediante obrigação legal, determinação judicial ou solicitação expressa do titular. 

8. Cookies e Dados de Navegação 

O dashboard utiliza cookies estritamente funcionais para manter a sessão ativa durante o uso. Eles não armazenam dados sensíveis. A desativação desses cookies pode prejudicar o funcionamento correto da plataforma. 

9. Consentimento 

Ao criar uma conta e utilizar o Agro Monitor, o usuário manifesta seu consentimento com esta Política de Privacidade e autoriza o tratamento de seus dados pessoais, conforme descrito neste documento. 

O usuário pode solicitar revisão, correção, atualização ou exclusão de seus dados a qualquer momento. 

10. Alterações desta Política 

A Política de Privacidade poderá ser atualizada conforme mudanças no sistema, exigências legais ou melhorias de segurança. Recomenda-se consulta periódica a esta seção. 

11. Jurisdição 

Para dirimir eventuais controvérsias relacionadas a esta política, aplica-se a legislação brasileira, sendo eleito o foro da comarca vinculada à instituição responsável pelo desenvolvimento do Agro Monitor. </p>
            </section>

        </div>
    )
}
export default Termos;