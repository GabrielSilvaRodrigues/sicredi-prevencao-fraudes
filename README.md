# 🛡️ Prevenção Inteligente a Fraudes — Sicredi

> Agente de Inteligência Artificial para prevenção inteligente a fraudes em compras com cartões.  
> Proposta desenvolvida para a competição de inovação do Sicredi.

---

## 📋 Descrição

Este projeto implementa um **agente de IA** capaz de analisar transações com cartão em tempo real, identificar comportamentos suspeitos e recomendar ações preventivas — sem bloquear operações legítimas.

O sistema utiliza um **motor de avaliação de risco baseado em regras e estatística**, com interface interativa construída em Streamlit. A integração com **IBM watsonx Orchestrate** está planejada para enriquecer explicações em linguagem natural.

> ⚠️ **Todos os dados utilizados neste protótipo são 100% fictícios e sintéticos.**  
> Nenhuma informação real de clientes, transações ou associados é armazenada ou utilizada.

---

## 🏗️ Arquitetura

```
Transação recebida
        │
        ▼
Motor de Avaliação de Risco
   ├── Valor elevado
   ├── Categoria incomum
   ├── Localização incomum
   ├── Horário fora do padrão
   ├── Alta frequência
   ├── País estrangeiro
   └── Canal suspeito
        │
        ▼
Pontuação 0–100 + Classificação (baixo / médio / alto)
        │
        ▼
Recomendação preventiva + Justificativa
        │
        └──▶ [IBM watsonx Orchestrate — integração planejada]
```

---

## 📁 Estrutura do Projeto

```
sicredi_fraudes/
├── app.py                      ← Interface principal (Streamlit)
├── requirements.txt            ← Dependências Python
├── src/
│   ├── core/
│   │   ├── models.py           ← Modelos de dados (Transacao, Perfil, Resultado)
│   │   ├── risk_engine.py      ← Motor de avaliação de risco
│   │   └── watsonx_client.py   ← Integração planejada com IBM watsonx
│   ├── data/
│   │   └── generator.py        ← Gerador de dados fictícios e sintéticos
│   └── ui/
│       └── __init__.py
├── tests/
│   ├── conftest.py             ← Fixtures compartilhadas
│   └── test_risk_engine.py     ← Testes do motor de risco
└── docs/
    └── watsonx/                ← Guia de configuração IBM watsonx
```

---

## ⚙️ Tecnologias

| Componente         | Tecnologia                          |
|--------------------|-------------------------------------|
| Interface          | Python 3.11+ + Streamlit            |
| Motor de risco     | Python puro (regras + estatística)  |
| Gerador de dados   | Faker + gerador sintético próprio   |
| Gráficos           | Plotly                              |
| Testes             | Pytest                              |
| IA planejada       | IBM watsonx Orchestrate             |

---

## 🚀 Instalação

### Pré-requisitos

- Python 3.11 ou superior
- pip

### Passos

```bash
# 1. Clone o repositório
git clone https://github.com/leoncs5/sicredi-prevencao-fraudes.git
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
# Na raiz do repositório, com o ambiente virtual ativado:
streamlit run sicredi_fraudes/app.py
```

A aplicação abrirá automaticamente no navegador em `http://localhost:8501`.

---

## 🧪 Testes

```bash
# Na raiz do repositório:
pytest sicredi_fraudes/tests/ -v
```

---

## 🔐 Configuração de Credenciais (opcional)

Para habilitar a integração com IBM watsonx Orchestrate, crie o arquivo `.streamlit/secrets.toml` (**nunca versionar**):

```toml
# .streamlit/secrets.toml — NÃO commitar este arquivo
WATSONX_API_KEY = "sua-chave-aqui"
WATSONX_PROJECT_ID = "seu-project-id"
WATSONX_URL = "https://us-south.ml.cloud.ibm.com"
```

O arquivo `.gitignore` já está configurado para excluir este arquivo do controle de versão.

---

## 🤝 Colaboração — Branches

Este repositório usa o seguinte fluxo de trabalho com branches:

| Branch                     | Responsável                              |
|----------------------------|------------------------------------------|
| `main`                     | Branch principal — apenas via Pull Request |
| `feature/analise-fraudes`  | Análise de fraudes e motor de risco      |
| `feature/interface`        | Interface Streamlit e visualizações      |
| `feature/integracao-testes`| Integração watsonx, testes e documentação |

Consulte o [Fluxo de Colaboração](#fluxo-de-colaboração) abaixo.

---

## 🔄 Fluxo de Colaboração

```bash
# 1. Atualize sua referência da main
git fetch origin
git checkout main
git pull origin main

# 2. Vá para sua branch (ou crie-a)
git checkout feature/sua-branch
# ou para criar: git checkout -b feature/sua-branch

# 3. Implemente sua funcionalidade

# 4. Execute os testes
pytest sicredi_fraudes/tests/ -v

# 5. Revise o que mudou
git diff

# 6. Adicione e faça commit descritivo
git add .
git commit -m "feat(modulo): descrição clara do que foi feito"

# 7. Envie para o GitHub
git push origin feature/sua-branch

# 8. Abra um Pull Request no GitHub para a main
# 9. Aguarde revisão antes de fazer merge
```

> ❌ Nunca faça `git push --force`  
> ❌ Nunca commite diretamente na `main`  
> ❌ Nunca armazene senhas, tokens ou chaves no código

---

## 📜 Licença

Projeto desenvolvido exclusivamente para fins competitivos internos do Sicredi.  
Dados fictícios — sem uso de informações reais de clientes.
