# Prompt para Bob 3 — Interface e Dashboard

> **INSTRUÇÃO PARA O INTEGRANTE 3 (IBM Bob no terceiro computador)**
>
> Cole este prompt inteiro no IBM Bob para receber instruções precisas sobre sua tarefa.
> Leia completamente antes de executar qualquer comando.

---

## Contexto do Projeto

Você está contribuindo para um projeto de competição do Sicredi chamado
**"Prevenção Inteligente a Fraudes e Segurança do Associado"**.

O projeto é um protótipo de agente de IA que analisa transações fictícias de cartão
e identifica sinais suspeitos. A **interface visual** é o que os avaliadores do Sicredi
verão primeiro — seu trabalho é fundamental para a apresentação do projeto.

**Repositório:** `https://github.com/LeonCS5/sicredi-prevencao-fraudes`  
**Sua branch:** `feature/interface-dashboard`  
**Sua responsabilidade:** Interface Streamlit, painel, gráficos, simulador, UX

---

## Primeiro Passo: Configurar o Ambiente

```bash
# 1. Clone o repositório (se ainda não clonou)
git clone https://github.com/LeonCS5/sicredi-prevencao-fraudes.git
cd sicredi-prevencao-fraudes

# 2. Configure seu nome e e-mail Git
git config user.name "Seu Nome"
git config user.email "seu@email.com"

# 3. Crie e ative o ambiente virtual
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/macOS

# 4. Instale as dependências
pip install -r sicredi_fraudes/requirements.txt

# 5. Vá para sua branch
git checkout feature/interface-dashboard

# 6. Execute a aplicação para ver o estado atual
streamlit run sicredi_fraudes/app.py
```

---

## O que já está implementado (na main)

Antes de escrever código, explore o que já existe:

| Arquivo | O que contém |
|---|---|
| `sicredi_fraudes/app.py` | Interface completa: Painel, Detalhe, Simulador, Histórico, Sobre |
| `sicredi_fraudes/src/core/models.py` | Modelos de dados — **NÃO altere** |
| `sicredi_fraudes/src/core/risk_engine.py` | Motor de risco — **NÃO altere** |
| `sicredi_fraudes/src/data/generator.py` | Gerador de dados sintéticos |

**Explore a aplicação atual:**

```bash
streamlit run sicredi_fraudes/app.py
# Abra http://localhost:8501 no navegador
# Explore as 5 páginas: Painel, Detalhe, Simulador, Histórico, Sobre
```

---

## Regra Fundamental para Interface

**NUNCA reimplemente a lógica de análise de risco na interface.**

A interface deve SEMPRE importar e usar o motor existente:

```python
# CORRETO — use sempre assim
from src.core.risk_engine import avaliar_transacao
from src.core.models import Transacao, PerfilAssociado

resultado = avaliar_transacao(tx, perfil, historico_recente)
```

```python
# ERRADO — nunca faça isso na interface
def calcular_risco(valor, cidade):     # ← duplicação proibida
    if valor > 1000:
        return "alto"
```

---

## O que você deve fazer

### Tarefa 1 — Explorar a interface atual e identificar melhorias

Execute a aplicação e documente no início do seu trabalho:
- O que já funciona bem?
- O que poderia melhorar na experiência do avaliador?
- Quais informações estão faltando?

### Tarefa 2 — Série temporal de transações (alta prioridade)

Adicione na página "📊 Painel" um gráfico de linha mostrando
o valor das transações ao longo do tempo, colorido por nível de risco.

```python
# Dados disponíveis
from src.data.generator import transacoes_para_dataframe
df = transacoes_para_dataframe(transacoes)
# df tem colunas: id, associado_id, valor, data_hora, categoria,
#                 estabelecimento, cidade, estado, pais, distancia_km, canal

# Use plotly express para criar o gráfico de linha
import plotly.express as px
```

### Tarefa 3 — Mapa de calor por categoria e risco

Adicione uma tabela ou heatmap mostrando a distribuição de risco por categoria.
Isso ajuda o avaliador a entender quais tipos de compra geram mais alertas.

### Tarefa 4 — Exportar relatório em CSV

Adicione um botão para exportar as análises visíveis na tabela:

```python
import pandas as pd
csv = df_tabela.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Exportar CSV",
    data=csv,
    file_name="relatorio_fraudes.csv",
    mime="text/csv",
)
```

### Tarefa 5 — Melhorar o Simulador

No simulador, após a análise, mostre uma comparação visual entre
os valores da transação simulada e o perfil habitual do associado.

Exemplo: barra mostrando "valor da transação vs média habitual".

### Tarefa 6 — Indicador de integração watsonx mais visível

No painel lateral, torne mais visível o status do watsonx:
- Quando não configurado: exibir ícone de configuração pendente com instrução
- Quando configurado: exibir ícone de sucesso com nome do modelo

---

## Contratos que você DEVE respeitar

### Usar sempre o motor real

```python
# A interface SEMPRE usa o motor de risco
from src.core.risk_engine import avaliar_transacao

# Nunca recalcule pontuação na interface
# Nunca crie sua própria lista de regras
# Nunca interprete os fatores manualmente
```

### Campos garantidos pelo motor

A função `avaliar_transacao()` sempre retorna:

```python
resultado.pontuacao             # float 0-100
resultado.nivel_risco           # "baixo" | "medio" | "alto"
resultado.fatores               # lista (pode ser vazia)
resultado.recomendacao          # str
resultado.justificativa         # str
resultado.eh_fraude_confirmada  # False
```

### Aviso obrigatório de dados fictícios

Em toda exibição pública de análises, inclua aviso visível:

```python
st.caption("⚠️ Todos os dados são fictícios e sintéticos. Nenhum dado real de clientes é utilizado.")
```

### Identificação visual de nível de risco

Mantenha a paleta já definida:

```python
CORES_RISCO = {"baixo": "#16a34a", "medio": "#d97706", "alto": "#dc2626"}
ICONES_RISCO = {"baixo": "🟢", "medio": "🟡", "alto": "🔴"}
```

---

## Como fazer commit e enviar

```bash
# Verificar o que mudou
git diff
git status

# Testar se a aplicação ainda inicia
streamlit run sicredi_fraudes/app.py

# Executar os testes (para garantir que não quebrou o motor)
pytest sicredi_fraudes/tests/ -v

# Adicionar e commitar
git add sicredi_fraudes/app.py
git commit -m "feat(ui): adiciona grafico de serie temporal de transacoes"

# Enviar para o GitHub
git push origin feature/interface-dashboard
```

Depois, abra um **Pull Request** em:
`https://github.com/LeonCS5/sicredi-prevencao-fraudes/compare`  
(base: `main` ← compare: `feature/interface-dashboard`)

---

## Guia de Identidade Visual do Projeto

| Elemento | Valor |
|---|---|
| Cor primária (Sicredi verde) | `#1a6b3c` |
| Cor secundária (azul escuro) | `#1a3a5c` |
| Cor de perigo | `#dc2626` |
| Cor de aviso | `#d97706` |
| Cor de sucesso | `#16a34a` |
| Fonte | `'Segoe UI', sans-serif` |

---

## Perguntas frequentes

**P: Posso adicionar uma nova biblioteca de gráficos?**  
R: Sim — Plotly já está instalado e é preferível. Se precisar de outra biblioteca,
adicione ao `requirements.txt` e documente no PR.

**P: Posso criar novas páginas no painel?**  
R: Sim — adicione ao menu de navegação no sidebar. Use o mesmo padrão já existente.

**P: E se o motor retornar um resultado inesperado?**  
R: Adicione tratamento de erro amigável (`st.error()` ou `st.warning()`) sem duplicar
a lógica de cálculo.

**P: Posso usar dados reais de transações para testar?**  
R: Não. Use exclusivamente o gerador sintético (`gerar_dataset_demo()`) ou o simulador
com dados inventados. Nunca use dados reais de clientes.

**P: O avaliador vai ver a interface antes de tudo — o que priorizar?**  
R: Priorize em ordem: (1) a aplicação iniciar sem erros, (2) o Simulador funcionar
end-to-end, (3) o Painel exibir os dados claramente, (4) melhorias visuais.
