# 🛡️ Prevenção Inteligente a Fraudes — Sicredi

> Protótipo desenvolvido como proposta para a competição de inovação do Sicredi  
> Tema: **"Prevenção Inteligente a Fraudes e Segurança do Associado"**
>
> ⚠️ **Todos os dados são fictícios e sintéticos.** Nenhuma informação real de clientes ou transações bancárias é utilizada.

---

## 📋 Sumário

1. [O Problema](#o-problema)
2. [A Solução](#a-solução)
3. [Arquitetura](#arquitetura)
4. [Estrutura do Projeto](#estrutura-do-projeto)
5. [Pré-requisitos](#pré-requisitos)
6. [Instalação — Passo a Passo](#instalação--passo-a-passo)
7. [Configuração do `.env`](#configuração-do-env)
8. [Como obter as credenciais do watsonx](#como-obter-as-credenciais-do-watsonx)
9. [Como Executar](#como-executar)
10. [Como Testar](#como-testar)
11. [Funcionalidades](#funcionalidades)
12. [Tecnologias](#tecnologias)
13. [Segurança e Privacidade](#segurança-e-privacidade)
14. [Declarações Importantes](#declarações-importantes)

---

## O Problema

Fraudes com cartões de crédito e débito causam prejuízos bilionários ao setor financeiro e geram insegurança para os associados. Identificar transações suspeitas de forma precisa é um desafio: agir tarde demais permite a fraude; agir cedo demais prejudica compras legítimas.

---

## A Solução

Um **agente de IA** que analisa cada transação em tempo real, calcula uma pontuação de risco (0–100), identifica os fatores que contribuíram para esse risco e recomenda ações preventivas proporcionais — sem bloquear cartões automaticamente ou confirmar fraudes sem revisão humana.

---

## Arquitetura

```
Transação recebida
        │
        ▼
Validação de entrada
        │
        ▼
Motor de Avaliação de Risco (src/core/risk_engine.py)
   ├── Regra: Valor elevado
   ├── Regra: Categoria incomum
   ├── Regra: Localização incomum
   ├── Regra: Horário incomum
   ├── Regra: Alta frequência
   ├── Regra: País estrangeiro
   ├── Regra: Canal suspeito
   └── Regra: Viagem impossível
        │
        ▼
Pontuação 0–100 + Fatores identificados
        │
        ▼
Classificação: baixo (0–39) / médio (40–69) / alto (60–100)
        │
        ▼
Recomendação preventiva + Justificativa
        │
        ├──▶ [IBM watsonx Orchestrate — integração opcional]
        │         Enriquece a explicação em linguagem natural
        │         NÃO altera a pontuação calculada localmente
        │
        ▼
Painel Streamlit (app.py)
```

---

## Estrutura do Projeto

```
sicredi-prevencao-fraudes/
├── README.md                           ← Este arquivo
├── COLABORACAO.md
├── LICENSE
├── docs/
│   ├── ARCHITECTURE.md
│   ├── INTEGRATION_CONTRACTS.md
│   ├── TASKS.md
│   ├── TEAM_WORKFLOW.md
│   ├── BOB_2_PROMPT.md
│   ├── BOB_3_PROMPT.md
│   └── WATSONX_ORCHESTRATE.md
└── sicredi_fraudes/                    ← Pasta principal da aplicação
    ├── app.py                          ← Interface principal (Streamlit)
    ├── requirements.txt                ← Dependências Python
    ├── .gitignore
    ├── src/
    │   ├── core/
    │   │   ├── models.py               ← Modelos de dados (dataclasses)
    │   │   ├── risk_engine.py          ← Motor de avaliação de risco
    │   │   └── watsonx_client.py       ← Integração opcional com watsonx
    │   └── data/
    │       └── generator.py            ← Gerador de dados fictícios sintéticos
    ├── tests/
    │   ├── conftest.py                 ← Fixtures de teste
    │   └── test_risk_engine.py         ← 28 testes automatizados
    └── docs/
        ├── arquitetura.md
        └── watsonx/
            ├── guia_configuracao.md    ← Guia detalhado do watsonx
            └── fluxo_agente.md         ← Descrição do fluxo do agente
```

---

## Pré-requisitos

| Requisito | Versão mínima | Obrigatório |
|---|---|---|
| Python | 3.10 | ✅ Sim |
| pip | qualquer | ✅ Sim |
| Git | qualquer | Recomendado |
| Conta IBM Cloud | — | ⚙️ Apenas para watsonx |

---

## Instalação — Passo a Passo

### 1. Clone o repositório

```bash
git clone https://github.com/SEU_USUARIO/sicredi-prevencao-fraudes.git
cd sicredi-prevencao-fraudes
```

### 2. Crie um ambiente virtual (recomendado)

```bash
python -m venv .venv
```

Ative o ambiente:

```bash
# Linux / macOS
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (cmd)
.venv\Scripts\activate.bat
```

### 3. Instale as dependências

```bash
cd sicredi_fraudes
pip install -r requirements.txt
```

### 4. (Opcional) Instale o SDK do watsonx

Necessário apenas se quiser ativar o enriquecimento de explicações com IBM watsonx.

```bash
pip install ibm-watsonx-ai
```

### 5. Configure o `.env` (opcional — veja seção abaixo)

### 6. Execute a aplicação

```bash
streamlit run app.py
```

O navegador abrirá automaticamente em `http://localhost:8501`.

---

## Configuração do `.env`

O arquivo `.env` **não é obrigatório** para rodar a aplicação. Sem ele, o sistema funciona completamente com o motor de risco local.

O `.env` é necessário **apenas para ativar** o enriquecimento de explicações com IBM watsonx Orchestrate.

### Localização

Crie o arquivo na pasta `sicredi_fraudes/` (mesma pasta do `app.py`):

```
sicredi_fraudes/
├── app.py
├── .env          ← criar aqui
└── requirements.txt
```

### Conteúdo do `.env`

```env
# ============================================================
# IBM watsonx — Credenciais de integração
# Todas as variáveis são opcionais.
# Sem elas, o sistema usa apenas o motor local.
# ============================================================

# Chave de API da IBM Cloud (obrigatória para ativar watsonx)
WATSONX_API_KEY=sua_api_key_aqui

# ID do projeto watsonx.ai (obrigatório para ativar watsonx)
WATSONX_PROJECT_ID=seu_project_id_aqui

# URL do endpoint regional (padrão: us-south)
WATSONX_URL=https://us-south.ml.cloud.ibm.com

# Modelo de linguagem a utilizar (padrão já configurado abaixo)
WATSONX_MODEL_ID=ibm/granite-13b-instruct-v2
```

### Variáveis explicadas

| Variável | Obrigatória para watsonx | Descrição | Onde obter |
|---|---|---|---|
| `WATSONX_API_KEY` | ✅ Sim | Chave de API da IBM Cloud | IBM Cloud → IAM → API Keys |
| `WATSONX_PROJECT_ID` | ✅ Sim | ID do projeto no watsonx.ai | watsonx.ai → Configurações do projeto |
| `WATSONX_URL` | Não (tem padrão) | Endpoint regional da API | Veja tabela de regiões abaixo |
| `WATSONX_MODEL_ID` | Não (tem padrão) | Modelo de linguagem | Veja modelos disponíveis abaixo |

### Regiões disponíveis

| Região | URL |
|---|---|
| EUA (Dallas) — padrão | `https://us-south.ml.cloud.ibm.com` |
| Europa (Frankfurt) | `https://eu-de.ml.cloud.ibm.com` |
| Reino Unido (Londres) | `https://eu-gb.ml.cloud.ibm.com` |
| Japão (Tóquio) | `https://jp-tok.ml.cloud.ibm.com` |

### Modelos disponíveis

| Modelo | Uso recomendado |
|---|---|
| `ibm/granite-13b-instruct-v2` | Explicações e recomendações (padrão) |
| `ibm/granite-8b-code-instruct` | Geração de código auxiliar |
| `meta-llama/llama-3-70b-instruct` | Raciocínio mais complexo |

> ⚠️ **NUNCA commite o arquivo `.env`** no repositório. Ele já está no `.gitignore`.  
> Se você acidentalmente o commitar, **revogue a API Key imediatamente** no console IBM Cloud.

---

## Como obter as credenciais do watsonx

Esta seção é um guia passo a passo para criar uma conta e obter as credenciais necessárias.

### Passo 1 — Criar conta na IBM Cloud

1. Acesse [https://cloud.ibm.com/registration](https://cloud.ibm.com/registration)
2. Preencha o formulário de cadastro (e-mail, senha, nome)
3. Confirme o e-mail recebido
4. Faça login em [https://cloud.ibm.com](https://cloud.ibm.com)

> A IBM Cloud oferece um plano gratuito (_Lite_) suficiente para testes.

---

### Passo 2 — Obter a API Key (`WATSONX_API_KEY`)

1. No console IBM Cloud, clique no menu superior em **Manage → Access (IAM)**
2. No menu lateral, clique em **API keys**
3. Clique em **Create an IBM Cloud API key**
4. Dê um nome (ex.: `sicredi-fraudes-key`) e clique em **Create**
5. **Copie ou baixe a chave imediatamente** — ela não será exibida novamente
6. Cole o valor em `WATSONX_API_KEY=` no seu `.env`

---

### Passo 3 — Criar um projeto no watsonx.ai

1. Acesse [https://dataplatform.cloud.ibm.com](https://dataplatform.cloud.ibm.com)
   - Ou via IBM Cloud: **Navigation menu → watsonx**
2. Clique em **New project → Create an empty project**
3. Dê um nome ao projeto (ex.: `sicredi-fraudes`)
4. Clique em **Create**

---

### Passo 4 — Obter o Project ID (`WATSONX_PROJECT_ID`)

1. Abra o projeto recém-criado
2. Vá até a aba **Manage** (no topo do projeto)
3. Em **General**, o **Project ID** está listado abaixo do nome do projeto
4. Copie o valor (formato UUID: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)
5. Cole em `WATSONX_PROJECT_ID=` no seu `.env`

---

### Passo 5 — Verificar a integração

Execute a aplicação normalmente:

```bash
cd sicredi_fraudes
streamlit run app.py
```

Na **barra lateral** da interface, o indicador de status deve exibir:

> ✅ watsonx Orchestrate configurado e ativo.

Se aparecer `⚙️ watsonx não configurado`, revise os valores do `.env`.

---

## Como Executar

```bash
# Certifique-se de estar na pasta sicredi_fraudes/
cd sicredi_fraudes

# Inicie o servidor Streamlit
streamlit run app.py
```

A aplicação abre automaticamente em `http://localhost:8501`.

Se o comando `streamlit` não for reconhecido:

```bash
python -m streamlit run app.py
```

### Páginas disponíveis na aplicação

| Página | Descrição |
|---|---|
| 📊 Painel | Visão geral com KPIs, gráficos e lista de transações |
| 🔍 Detalhe da Transação | Análise individual com gauge de risco e fatores |
| 🧪 Simulador | Crie uma transação fictícia e veja a análise em tempo real |
| 📋 Histórico | Registro das análises realizadas no simulador durante a sessão |
| ℹ️ Sobre | Arquitetura, tecnologias e declarações do projeto |

---

## Como Testar

```bash
# Na pasta sicredi_fraudes/
python -m pytest tests/ -v
```

Resultado esperado: **28 testes passando**.

Os testes cobrem os 6 cenários obrigatórios:

| # | Cenário |
|---|---|
| 1 | Compra habitual de baixo valor |
| 2 | Compra de valor elevado e fora do padrão |
| 3 | Várias compras em sequência (alta frequência) |
| 4 | Compra em localização incomum |
| 5 | Transação com informações mínimas/incompletas |
| 6 | Transação com múltiplos sinais suspeitos simultâneos |

---

## Funcionalidades

| Funcionalidade | Status |
|---|---|
| Análise de transações (valor, data, local, categoria) | ✅ Implementado |
| Classificação em baixo / médio / alto risco | ✅ Implementado |
| Pontuação de risco (0–100) | ✅ Implementado |
| Identificação dos fatores de risco | ✅ Implementado |
| Detecção de viagem impossível (clonagem) | ✅ Implementado |
| Detecção de alta frequência (múltiplas transações rápidas) | ✅ Implementado |
| Recomendações preventivas automáticas | ✅ Implementado |
| Painel de monitoramento com KPIs e gráficos | ✅ Implementado |
| Detalhe de transação com gauge visual | ✅ Implementado |
| Simulador de transações fictícias | ✅ Implementado |
| Histórico de análises da sessão | ✅ Implementado |
| Dados fictícios sintéticos (sem dados reais) | ✅ Implementado |
| Testes automatizados | ✅ 28/28 |
| Integração IBM watsonx Orchestrate | ⚙️ Opcional — requer credenciais |

---

## Tecnologias

| Componente | Tecnologia | Versão mínima |
|---|---|---|
| Interface web | Streamlit | 1.40.0 |
| Linguagem | Python | 3.10 |
| Manipulação de dados | Pandas | 3.1.0 |
| Cálculo numérico | NumPy | 2.5.0 |
| Gráficos | Plotly | 7.1.0 |
| Geração de dados fictícios | Faker | 33.0.0 |
| Testes | pytest | 8.0.0 |
| Variáveis de ambiente | python-dotenv | 1.0.0 |
| IA (opcional) | ibm-watsonx-ai | última |

---

## Segurança e Privacidade

- **Nenhum dado real** de clientes ou transações bancárias é utilizado.
- Credenciais e chaves de API não são armazenadas no código-fonte.
- O arquivo `.env` está protegido pelo `.gitignore`.
- Nenhuma ação irreversível (bloqueio de cartão, envio de mensagens reais) é executada pelo sistema.
- O histórico de análises existe apenas na sessão atual e é apagado ao recarregar a página.

---

## Declarações Importantes

- Este sistema identifica **indícios** de comportamento suspeito, **não confirma fraudes**.
- A pontuação de risco é calculada com regras determinísticas e explicáveis — não é uma caixa preta.
- Uma implantação real exigiria dados históricos reais, validação empírica e monitoramento contínuo.
- O sistema não afirma precisão real sem avaliação com dados de produção.
- A integração com watsonx Orchestrate enriquece **apenas a explicação em linguagem natural** — não altera a pontuação calculada pelo motor local.

---

## Publicação no GitHub

```bash
# Na pasta raiz do projeto
git init
git add .
git commit -m "feat: protótipo de prevenção a fraudes para o Sicredi"

# Crie um repositório no GitHub e conecte:
git remote add origin https://github.com/SEU_USUARIO/sicredi-prevencao-fraudes.git
git branch -M main
git push -u origin main
```

---

## Licença

Projeto desenvolvido como proposta para competição de inovação. Consulte a organização antes de utilizar em produção.
