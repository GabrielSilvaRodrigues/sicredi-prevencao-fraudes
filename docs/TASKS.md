# Tarefas, Dependências e Critérios de Conclusão

## Estado Atual do Projeto

| Módulo | Status | Branch | Responsável |
|---|---|---|---|
| Estrutura base + docs | ✅ Concluído | `main` | Bob 1 |
| Modelos de dados | ✅ Concluído | `main` | Bob 1 |
| Motor antifraude (7 regras) | ✅ Concluído | `feature/analise-fraudes` | Bob 1 |
| Regra viagem impossível (8ª regra) | ✅ Concluído | `feature/analise-fraudes` | Bob 1 |
| Gerador de dados sintéticos | ✅ Concluído | `feature/analise-fraudes` | Bob 1 |
| Testes automatizados (45 testes) | ✅ Concluído | `feature/analise-fraudes` | Bob 1 |
| Interface Streamlit | ✅ Concluído | `main` (base) | Bob 1 |
| Integração watsonx | ⚙️ Pendente config | — | Bob 3 |

> **Branches ativas no GitHub:**
> - `feature/analise-fraudes` — Bob 1 ✅ publicada, aguardando PR
> - `feature/interface` — Bob 2 ⏳ ainda no commit inicial
> - `feature/integracao-testes` — Bob 3 ⏳ ainda no commit inicial

---

## Bob 1 — Motor Antifraude (`feature/analise-fraudes`)

### ✅ Concluído

- [x] **Modelos de dados** — `sicredi_fraudes/src/core/models.py`
  - `Transacao`, `PerfilAssociado`, `FatorRisco`, `ResultadoAnalise`

- [x] **Motor de avaliação de risco** — `sicredi_fraudes/src/core/risk_engine.py`
  - 8 regras: valor alto, categoria incomum, localização incomum, horário incomum,
    alta frequência, país estrangeiro, canal suspeito, **viagem impossível**
  - Pesos calibrados: distribuição adequada de risco nos dados demo

- [x] **Gerador de dados sintéticos** — `sicredi_fraudes/src/data/generator.py`
  - `gerar_dataset_demo()`, `gerar_perfil()`, `gerar_transacao_normal()`, `gerar_transacao_suspeita()`

- [x] **Testes automatizados** — `sicredi_fraudes/tests/test_risk_engine.py`
  - 45 testes, 6 cenários obrigatórios + cobertura expandida
  - `pytest sicredi_fraudes/tests/ -v` → **45/45 passando**

- [x] **Push da branch** — `feature/analise-fraudes` publicada no GitHub

### ⏳ Próximo passo

- [ ] **Abrir Pull Request** no GitHub
  - URL: https://github.com/LeonCS5/sicredi-prevencao-fraudes/compare/main...feature/analise-fraudes
  - Título sugerido: `feat(analise): motor antifraude com 8 regras e 45 testes`
  - Aguardar revisão de Bob 2 ou Bob 3 antes do merge

---

## Bob 2 — Interface Dashboard (`feature/interface`)

### Contexto

O `app.py` base já existe na `main`. Sua tarefa é trabalhar na branch
`feature/interface`, trazer o código da `main` e **adicionar melhorias** à interface.

### Como começar

```bash
git fetch origin
git checkout feature/interface
git merge main   # traz todo o código base
```

### Tarefas obrigatórias

- [ ] **Série temporal de transações**
  - Gráfico de linha no Painel: eixo X = data/hora, eixo Y = valor, cor = nível de risco
  - Usar `transacoes_para_dataframe()` já disponível em `src/data/generator.py`
  - Arquivo: `sicredi_fraudes/app.py` — seção `PÁGINA 1 — Painel`
  - Critério: gráfico visível e funcional com dados do dataset demo

- [ ] **Exportação de relatório CSV**
  - Botão na página "📋 Histórico" para baixar as análises da sessão
  - Usar `st.download_button()` com DataFrame serializado em CSV
  - Critério: arquivo CSV gerado com colunas: timestamp, associado, estabelecimento, valor, pontuação, risco

- [ ] **Spinner de carregamento no Simulador**
  - Envolver o bloco de análise com `with st.spinner("Analisando transação...")`
  - Arquivo: `sicredi_fraudes/app.py` — seção `PÁGINA 3 — Simulador`
  - Critério: spinner aparece durante o processamento

### Tarefas opcionais (se houver tempo)

- [ ] **Distribuição geográfica**
  - Gráfico de barras com contagem de transações por cidade
  - Filtros: somente risco alto/médio, ou todas

- [ ] **Tratamento de erro aprimorado**
  - Mensagem amigável se `nivel_risco` vier com valor inesperado
  - Critério: `st.error()` ou `st.warning()` em vez de crash

### Critério de conclusão da branch

```bash
# 1. Testes devem passar
pytest sicredi_fraudes/tests/ -v

# 2. App deve iniciar sem erros
streamlit run sicredi_fraudes/app.py

# 3. Push e PR
git push origin feature/interface
# Abrir PR: base=main, compare=feature/interface
```

---

## Bob 3 — Integração e Testes (`feature/integracao-testes`)

### Contexto

Sua branch cuida de dois temas independentes:
1. **Integração com IBM watsonx** — enriquecer a explicação gerada pelo motor local
2. **Documentação de resultados dos testes**

O `watsonx_client.py` base já existe na `main` com a estrutura pronta.

### Como começar

```bash
git fetch origin
git checkout feature/integracao-testes
git merge main   # traz todo o código base
```

### Tarefas obrigatórias

- [ ] **Documentar resultado dos testes**
  - Executar `pytest sicredi_fraudes/tests/ -v --tb=short` após o merge
  - Criar `docs/TEST_RESULTS.md` com:
    - Data de execução
    - Total de testes, passando, falhando
    - Lista de cenários cobertos
  - Critério: arquivo criado e commitado na branch

- [ ] **Integrar explicação watsonx no Simulador**
  - No `app.py`, após calcular `resultado_sim`, chamar `enriquecer_explicacao()` de `watsonx_client.py`
  - Se retornar `None` (sem credenciais), manter comportamento atual — **sem quebrar nada**
  - Se retornar string, exibir abaixo da justificativa com label "💡 Explicação watsonx:"
  - Arquivo: `sicredi_fraudes/app.py` — seção `PÁGINA 3 — Simulador`
  - Critério: funciona com e sem credenciais; testes continuam passando

- [ ] **Integrar explicação watsonx no Detalhe da Transação**
  - Mesma lógica da tarefa anterior, mas na página "🔍 Detalhe da Transação"
  - Critério: exibição condicional — só aparece se `enriquecer_explicacao()` retornar string

### Tarefas opcionais (se houver tempo)

- [ ] **Configurar credenciais watsonx** (requer acesso IBM Cloud)
  - Criar `.env` local com:
    ```
    WATSONX_API_KEY=sua-chave
    WATSONX_PROJECT_ID=seu-project-id
    WATSONX_URL=https://us-south.ml.cloud.ibm.com
    ```
  - Testar `enriquecer_explicacao()` com chamada real
  - Critério: `status_integracao()["habilitado"] == True` no sidebar

- [ ] **Testes de integração watsonx (modo mock)**
  - Adicionar em `tests/test_watsonx_client.py`:
    - `test_status_sem_credenciais()` — `habilitado == False`
    - `test_enriquecer_sem_credenciais_retorna_none()`
  - Critério: testes passam sem credenciais reais (mock da env var)

### Critério de conclusão da branch

```bash
# 1. Testes devem passar
pytest sicredi_fraudes/tests/ -v

# 2. App deve iniciar sem erros (watsonx não configurado é OK)
streamlit run sicredi_fraudes/app.py

# 3. Push e PR
git push origin feature/integracao-testes
# Abrir PR: base=main, compare=feature/integracao-testes
```

---

## Dependências entre Tarefas

```
[Bob 1] feature/analise-fraudes ──── PR ──▶ main ─────────────────┐
                                                                    │
[Bob 2] feature/interface ─── merge main ──▶ melhorias ─ PR ──▶ main
                                                                    │
[Bob 3] feature/integracao-testes ── merge main ─▶ watsonx ─ PR ──▶ main
```

> Bob 2 e Bob 3 podem trabalhar em **paralelo** — não há dependência entre eles.
> Ambos devem fazer `git merge main` ao começar para obter o código do Bob 1.

---

## Critérios de Conclusão do Projeto

O projeto estará pronto para avaliação quando:

- [ ] `streamlit run sicredi_fraudes/app.py` inicia sem erros
- [ ] Motor antifraude analisa transações fictícias corretamente (8 regras)
- [ ] Interface exibe gráfico de série temporal e exportação CSV
- [ ] Simulador integrado com watsonx (ou claramente documentado como pendente)
- [ ] `pytest sicredi_fraudes/tests/ -v` → todos os testes passam
- [ ] `docs/TEST_RESULTS.md` documenta os resultados dos testes
- [ ] Branches mergeadas e `main` publicada no GitHub
- [ ] Repositório sem segredos, tokens ou dados reais
