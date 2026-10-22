# 🛡️ Prevenção Inteligente a Fraudes — Proposta para o Sicredi

> **Proposta de protótipo para a competição de inovação do Sicredi**
> Tema: *"Prevenção Inteligente a Fraudes e Segurança do Associado"*
>
> ⚠️ **Todos os dados são fictícios e sintéticos.** Nenhuma informação real de clientes ou transações bancárias é utilizada.

---

## 🎯 O Problema

Fraudes com cartões de crédito e débito causam prejuízos bilionários ao setor financeiro e geram insegurança para os associados. Identificar transações suspeitas de forma precisa é um desafio: agir tarde demais permite a fraude; agir cedo demais prejudica compras legítimas.

## 💡 A Solução

Um **agente de IA** que analisa cada transação em tempo real, calcula uma pontuação de risco, identifica os fatores que contribuíram para esse risco e recomenda ações preventivas proporcionais — sem bloquear cartões automaticamente ou confirmar fraudes sem revisão humana.

---

## 🏗️ Arquitetura do Sistema

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
   └── Regra: Canal suspeito
        │
        ▼
Pontuação 0–100 + Fatores identificados
        │
        ▼
Classificação: baixo (0–39) / médio (40–69) / alto (70–100)
        │
        ▼
Recomendação preventiva + Justificativa
        │
        ├──▶ [IBM watsonx Orchestrate — integração planejada]
        │         Enriquece a explicação em linguagem natural
        │         NÃO altera a pontuação calculada localmente
        │
        ▼
Painel Streamlit (app.py)
```

---

## 📁 Estrutura do Projeto

```
sicredi_fraudes/
├── app.py                          ← Interface principal (Streamlit)
├── requirements.txt                ← Dependências Python
├── .env.example                    ← Exemplo de configuração (sem segredos)
├── src/
│   ├── core/
│   │   ├── models.py               ← Modelos de dados (dataclasses)
│   │   ├── risk_engine.py          ← Motor de avaliação de risco
│   │   └── watsonx_client.py       ← Integração planejada com watsonx
│   └── data/
│       └── generator.py            ← Gerador de dados fictícios sintéticos
├── tests/
│   ├── conftest.py                 ← Fixtures de teste
│   └── test_risk_engine.py         ← 28 testes automatizados
└── docs/
    ├── arquitetura.md              ← Documentação técnica da arquitetura
    └── watsonx/
        ├── guia_configuracao.md    ← Como configurar o watsonx Orchestrate
        └── fluxo_agente.md         ← Descrição do fluxo do agente
```

---

## ⚙️ Instalação

### Pré-requisitos
- Python 3.10 ou superior (testado com 3.14)
- pip

### Passos

```bash
# 1. Clone o repositório
git clone https://github.com/SEU_USUARIO/sicredi-fraudes.git
cd sicredi-fraudes/sicredi_fraudes

# 2. (Recomendado) Crie um ambiente virtual
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt
```

---

## ▶️ Como Executar

```bash
# Na pasta sicredi_fraudes/
streamlit run app.py
```

O navegador abrirá automaticamente em `http://localhost:8501`.

> **Nota:** Se o comando `streamlit` não for reconhecido, use:
> ```bash
> python -m streamlit run app.py
> ```

---

## 🧪 Como Testar

```bash
# Na pasta sicredi_fraudes/
python -m pytest tests/ -v
```

Resultado esperado: **28 testes passando**.

Os testes cobrem os 6 cenários obrigatórios:
1. Compra habitual de baixo valor
2. Compra de valor elevado e fora do padrão
3. Várias compras em sequência (alta frequência)
4. Compra em localização incomum
5. Transação com informações mínimas/incompletas
6. Transação com múltiplos sinais suspeitos simultâneos

---

## 🤖 Funcionalidades Implementadas

| Funcionalidade | Status |
|---|---|
| Análise de transações (valor, data, local, categoria) | ✅ |
| Classificação em baixo / médio / alto risco | ✅ |
| Pontuação de risco (0–100) | ✅ |
| Identificação dos fatores de risco | ✅ |
| Detecção de comportamentos suspeitos | ✅ |
| Recomendações preventivas | ✅ |
| Painel de monitoramento | ✅ |
| Detalhe de transação com gauge visual | ✅ |
| Simulador de transações fictícias | ✅ |
| Histórico de análises da sessão | ✅ |
| Dados fictícios sintéticos | ✅ |
| Testes automatizados | ✅ 28/28 |
| Integração IBM watsonx Orchestrate | ⚙️ Planejada — pendente de credenciais |

---

## 🔑 Configuração do watsonx (Opcional)

Para ativar a integração com IBM watsonx Orchestrate:

1. Crie um arquivo `.env` na pasta `sicredi_fraudes/`:

```env
WATSONX_API_KEY=sua_api_key_aqui
WATSONX_PROJECT_ID=seu_project_id_aqui
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_MODEL_ID=ibm/granite-13b-instruct-v2
```

2. Instale o SDK adicional:

```bash
pip install ibm-watsonx-ai
```

3. O sistema detecta automaticamente as credenciais e ativa o enriquecimento de explicações.

> **Importante:** Nunca commite o arquivo `.env` no repositório. Ele está no `.gitignore`.

Consulte [`docs/watsonx/guia_configuracao.md`](docs/watsonx/guia_configuracao.md) para instruções detalhadas.

---

## 📤 Como Publicar no GitHub

```bash
# Na pasta raiz do projeto (sicredi_fraudes/)
git init
git add .
git commit -m "feat: protótipo de prevenção a fraudes para o Sicredi"

# Crie um repositório no GitHub e conecte:
git remote add origin https://github.com/SEU_USUARIO/sicredi-fraudes.git
git branch -M main
git push -u origin main
```

---

## 🔒 Segurança e Privacidade

- **Nenhum dado real** de clientes ou transações bancárias é utilizado.
- Credenciais e chaves de API não são armazenadas no código-fonte.
- O arquivo `.env` está protegido pelo `.gitignore`.
- Nenhuma ação irreversível (bloqueio de cartão, envio de mensagens) é executada pelo sistema.

---

## ⚠️ Declarações Importantes

- Este sistema identifica **indícios** de comportamento suspeito, **não confirma fraudes**.
- A pontuação de risco é calculada com regras determinísticas e explicáveis — não é uma caixa preta.
- Uma implantação real exigiria dados históricos reais, validação empírica e monitoramento contínuo.
- O sistema não afirma precisão real sem avaliação com dados de produção.

---

## 🛠️ Tecnologias

- **Python 3.10+** — linguagem principal
- **Streamlit** — interface web interativa
- **Pandas + NumPy** — manipulação de dados
- **Plotly** — gráficos e indicadores visuais
- **IBM watsonx Orchestrate** — IA planejada para enriquecimento de explicações
- **pytest** — testes automatizados

---

## 📄 Licença

Projeto desenvolvido como proposta para competição de inovação. Consulte a organização antes de utilizar em produção.
