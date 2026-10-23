# 🛡️ Prevenção Inteligente a Fraudes e Segurança do Associado — Sicredi

> Protótipo de agente de IA para análise de transações fictícias com cartão,
> identificação de comportamentos suspeitos e recomendação de ações preventivas.  
> Proposta desenvolvida para a competição de inovação do Sicredi.

---

## ⚠️ Aviso Importante

> **Todos os dados utilizados neste protótipo são 100% fictícios e sintéticos.**  
> Nenhuma informação real de clientes, transações ou associados é armazenada ou utilizada.  
> Este sistema identifica *indícios* de comportamento suspeito — **não confirma fraudes.**  
> Nenhuma ação irreversível (bloqueio de cartão, envio de mensagens reais) é executada.

---

## 🎯 O que o sistema faz

1. **Analisa transações fictícias** de cartão em tempo real
2. **Pontua o risco** de 0 a 100 usando 7 regras auditáveis
3. **Classifica o nível** de risco: baixo / médio / alto
4. **Explica os fatores** que contribuíram para a pontuação
5. **Recomenda ações** preventivas proporcionais ao risco
6. **Nunca bloqueia** — sempre recomenda revisão humana para casos suspeitos

---

## 🏗️ Arquitetura

```
Interface (Streamlit — app.py)
        │
        ▼
Motor Antifraude (risk_engine.py)
   ├── Valor elevado (z-score)
   ├── Categoria incomum
   ├── Localização incomum
   ├── Horário fora do padrão
   ├── Alta frequência (janela 30min)
   ├── País estrangeiro
   └── Canal suspeito
        │
        ▼
ResultadoAnalise → pontuação, nível, fatores, recomendação
        │
        └──▶ [IBM watsonx Orchestrate — integração pendente]
                Enriquece a explicação em linguagem natural
                NÃO altera a pontuação calculada
```

Documentação detalhada: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)

---

## 📁 Estrutura do Projeto

```
sicredi-prevencao-fraudes/
├── README.md                           ← Este arquivo
├── COLABORACAO.md                      ← Guia de colaboração Git
├── LICENSE
├── docs/
│   ├── ARCHITECTURE.md                 ← Arquitetura e responsabilidades
│   ├── INTEGRATION_CONTRACTS.md        ← Contratos de interface entre módulos
│   ├── TEAM_WORKFLOW.md                ← Fluxo de trabalho da equipe
│   ├── TASKS.md                        ← Tarefas, dependências, critérios
│   ├── WATSONX_ORCHESTRATE.md          ← Plano de integração IBM watsonx
│   ├── BOB_2_PROMPT.md                 ← Instruções para o Bob 2 (antifraude)
│   └── BOB_3_PROMPT.md                 ← Instruções para o Bob 3 (interface)
└── sicredi_fraudes/
    ├── app.py                          ← Interface Streamlit principal
    ├── requirements.txt
    ├── src/
    │   ├── core/
    │   │   ├── models.py               ← Transacao, PerfilAssociado, ResultadoAnalise
    │   │   ├── risk_engine.py          ← Motor de avaliação de risco
    │   │   └── watsonx_client.py       ← Integração IBM watsonx (pendente)
    │   └── data/
    │       └── generator.py            ← Gerador de dados sintéticos
    └── tests/
        ├── conftest.py                 ← Fixtures compartilhadas
        └── test_risk_engine.py         ← 6 cenários + regras individuais
```

---

## ⚙️ Tecnologias

| Componente         | Tecnologia                           |
|--------------------|--------------------------------------|
| Interface          | Python 3.11+ · Streamlit             |
| Motor de risco     | Python puro (regras + estatística)   |
| Gráficos           | Plotly                               |
| Dados sintéticos   | Faker + gerador próprio              |
| Testes             | Pytest                               |
| IA planejada       | IBM watsonx Orchestrate (pendente)   |
| Modelo LLM         | IBM Granite 13B Instruct v2          |

---

## 🚀 Instalação

### Pré-requisitos

- Python 3.11 ou superior
- Git
- pip

### Passos

```bash
# 1. Clone o repositório
git clone https://github.com/LeonCS5/sicredi-prevencao-fraudes.git
cd sicredi-prevencao-fraudes

# 2. Crie e ative o ambiente virtual
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

# 3. Instale as dependências
pip install -r sicredi_fraudes/requirements.txt
```

---

## ▶️ Execução

```bash
# Na raiz do repositório, com ambiente virtual ativado:
streamlit run sicredi_fraudes/app.py
```

A aplicação abrirá automaticamente em `http://localhost:8501`

### Páginas disponíveis

| Página | Descrição |
|---|---|
| 📊 Painel | Monitoramento geral — KPIs, gráficos, lista de transações |
| 🔍 Detalhe | Análise detalhada de uma transação específica |
| 🧪 Simulador | Criar e analisar transações fictícias em tempo real |
| 📋 Histórico | Registro das análises realizadas na sessão |
| ℹ️ Sobre | Arquitetura, tecnologias e declarações de limites |

---

## 🧪 Testes

```bash
# Executar todos os testes
pytest sicredi_fraudes/tests/ -v

# Com relatório de cobertura
pytest sicredi_fraudes/tests/ -v --tb=short
```

### Cenários testados

1. ✅ Compra habitual de baixo valor → risco baixo
2. ✅ Compra de valor muito elevado → fator detectado
3. ✅ Várias compras em sequência → alta frequência detectada
4. ✅ Compra em localização incomum → fator localização
5. ✅ Transação com dados mínimos → sistema não falha
6. ✅ Múltiplos sinais simultâneos → risco alto

---

## 🔐 Configuração do watsonx (opcional)

Para habilitar a explicação via IBM watsonx Orchestrate:

```bash
# Crie o arquivo .env na raiz (NUNCA commitar)
WATSONX_API_KEY=sua-api-key
WATSONX_PROJECT_ID=seu-project-id
WATSONX_URL=https://us-south.ml.cloud.ibm.com

# Instale o SDK
pip install ibm-watsonx-ai
```

Sem credenciais, o sistema opera completamente com o motor local.

---

## 🤝 Colaboração — Branches

| Branch | Responsável | Foco |
|---|---|---|
| `main` | Todos (via PR) | Branch principal |
| `feature/analise-antifraude` | Bob 2 | Motor de risco, dados, testes |
| `feature/interface-dashboard` | Bob 3 | Interface, painel, UX |
| `feature/integracao-testes` | Bob 1 | Integração, watsonx, docs |

Fluxo detalhado: [`docs/TEAM_WORKFLOW.md`](docs/TEAM_WORKFLOW.md)

---

## 📊 Limitações Documentadas

- O sistema usa **dados 100% fictícios** — sem avaliação com dados reais
- As pontuações **não são probabilidades estatisticamente calibradas**
- A integração com IBM watsonx Orchestrate está **planejada mas pendente**
- Nenhuma ação real (bloqueio, notificação) é executada
- O IBM Bob é uma ferramenta de desenvolvimento — não executa o agente em produção

---

## 📜 Licença

Projeto desenvolvido para fins competitivos internos do Sicredi.  
Dados fictícios — sem uso de informações reais de clientes.
