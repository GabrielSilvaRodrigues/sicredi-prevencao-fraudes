# Tarefas, Dependências e Critérios de Conclusão

## Status Geral do Projeto

| Módulo | Status | Branch | Responsável |
|---|---|---|---|
| Estrutura base | ✅ Concluído | `main` | Bob 1 |
| Modelos de dados | ✅ Concluído | `main` | Bob 1 |
| Motor antifraude | ✅ Concluído | `main` → `feature/analise-antifraude` | Bob 2 |
| Gerador de dados | ✅ Concluído | `main` → `feature/analise-antifraude` | Bob 2 |
| Interface Streamlit | ✅ Concluído | `main` → `feature/interface-dashboard` | Bob 3 |
| Testes automatizados | ✅ Concluído | `main` | Bob 1 |
| Integração watsonx | ⚙️ Pendente config | `main` | Bob 1 |
| Documentação completa | ✅ Concluído | `main` | Bob 1 |

---

## Tarefas por Integrante

---

### Bob 2 — Análise Antifraude (`feature/analise-antifraude`)

#### Tarefas Concluídas (já implementadas na `main`)

- [x] **Modelos de dados** — `src/core/models.py`
  - `Transacao`, `PerfilAssociado`, `FatorRisco`, `ResultadoAnalise`
  - Critério: dataclasses com todos os campos documentados

- [x] **Motor de avaliação de risco** — `src/core/risk_engine.py`
  - Função principal: `avaliar_transacao(tx, perfil, historico_recente)`
  - 7 regras implementadas: valor alto, categoria incomum, localização incomum,
    horário incomum, alta frequência, país estrangeiro, canal suspeito
  - Critério: `pontuacao ∈ [0,100]`, `nivel_risco ∈ {baixo,medio,alto}`, `eh_fraude_confirmada == False`

- [x] **Gerador de dados sintéticos** — `src/data/generator.py`
  - `gerar_dataset_demo()`, `gerar_perfil()`, `gerar_transacao_normal()`, `gerar_transacao_suspeita()`
  - Critério: dados 100% fictícios, reprodutíveis com semente fixada

- [x] **Testes automatizados** — `tests/test_risk_engine.py`
  - 6 cenários obrigatórios + regras individuais
  - Critério: todos os testes passam com `pytest -v`

#### Tarefas de Melhoria (opcional para Bob 2 na sua branch)

- [ ] **Nova regra: viagem impossível**
  - Detectar se o mesmo associado fez transação em duas cidades distantes em < 1 hora
  - Dependência: nenhuma — adicionar como nova função `regra_viagem_impossivel()`
  - Critério: testes cobrindo o caso positivo e negativo

- [ ] **Expandir cenários de teste**
  - Adicionar testes para `gerar_transacao_suspeita()` com cada `tipo_suspeita`
  - Testar `transacoes_para_dataframe()` com lista vazia
  - Critério: cobertura > 85% em `risk_engine.py` e `generator.py`

- [ ] **Calibração de pesos**
  - Revisar se os valores `PESO_*` produzem distribuições adequadas para os 50 registros demo
  - Critério: entre 20-40% das transações demo devem ser "médio" ou "alto" risco

---

### Bob 3 — Interface Dashboard (`feature/interface-dashboard`)

#### Tarefas Concluídas (já implementadas na `main`)

- [x] **Painel de Monitoramento** — `app.py` (página "📊 Painel")
  - KPIs: total, baixo, médio, alto
  - Gráfico pizza de distribuição de risco
  - Histograma de pontuações
  - Barras de fatores mais frequentes
  - Tabela com filtros por nível, associado e quantidade

- [x] **Detalhe da Transação** — (página "🔍 Detalhe")
  - Tabela de dados da transação
  - Gauge de pontuação de risco
  - Recomendação e justificativa
  - Fatores expandíveis com descrição

- [x] **Simulador de Transações** — (página "🧪 Simulador")
  - Formulário completo de entrada
  - Exibe perfil habitual do associado para referência
  - Análise em tempo real com gauge e fatores
  - Salva no histórico da sessão

- [x] **Histórico de Análises** — (página "📋 Histórico")
  - Lista de análises da sessão
  - Botão para limpar histórico
  - Aviso de dados fictícios

- [x] **Página Sobre** — (página "ℹ️ Sobre")
  - Arquitetura, tecnologias, declarações de limites

#### Tarefas de Melhoria (opcional para Bob 3 na sua branch)

- [ ] **Série temporal de transações**
  - Gráfico de linha: valor ao longo do tempo, colorido por nível de risco
  - Dependência: `transacoes_para_dataframe()` já disponível

- [ ] **Mapa de distribuição geográfica**
  - Tabela ou gráfico de barras com transações por cidade
  - Sem dependência externa de mapas

- [ ] **Exportação de relatório**
  - Botão para baixar as análises da sessão em CSV
  - `st.download_button()` com DataFrame serializado

- [ ] **Tratamento de erro aprimorado**
  - Mensagem amigável quando `avaliar_transacao()` retorna `nivel_risco` inesperado
  - Spinner de carregamento no simulador

---

### Bob 1 — Coordenação, Integração e Testes (`feature/integracao-testes`)

#### Tarefas Concluídas

- [x] Estrutura do repositório e branches
- [x] `README.md` completo
- [x] `docs/ARCHITECTURE.md`
- [x] `docs/INTEGRATION_CONTRACTS.md`
- [x] `docs/TEAM_WORKFLOW.md`
- [x] `docs/TASKS.md` (este arquivo)
- [x] `docs/WATSONX_ORCHESTRATE.md`
- [x] `docs/BOB_2_PROMPT.md`
- [x] `docs/BOB_3_PROMPT.md`
- [x] Configuração do GitHub (remoto, branches, push)
- [x] `conftest.py` com fixtures compartilhadas

#### Tarefas Pendentes

- [ ] **Configurar credenciais watsonx** (requer acesso à plataforma IBM Cloud)
  - Criar `.env` local com `WATSONX_API_KEY`, `WATSONX_PROJECT_ID`, `WATSONX_URL`
  - Testar `enriquecer_explicacao()` com credenciais reais
  - Critério: `status_integracao()["habilitado"] == True`

- [ ] **Executar suite de testes completa e documentar resultado**
  - `pytest sicredi_fraudes/tests/ -v --tb=short`
  - Documentar resultado em `docs/TEST_RESULTS.md`

- [ ] **Integrar branches quando publicadas**
  - Inspecionar `feature/analise-antifraude` e `feature/interface-dashboard`
  - Revisar diffs, executar testes
  - Fazer merge um por vez, resolver conflitos
  - Publicar `main` atualizada no GitHub

---

## Critérios de Conclusão do Projeto

O projeto estará pronto para avaliação quando:

- [ ] `streamlit run sicredi_fraudes/app.py` inicia sem erros
- [ ] Motor antifraude analisa transações fictícias corretamente
- [ ] Interface exibe resultados do motor real (sem duplicar lógica)
- [ ] Simulador funciona end-to-end
- [ ] Justificativas e recomendações visíveis para o avaliador
- [ ] `pytest sicredi_fraudes/tests/ -v` — todos os testes passam
- [ ] `README.md` explica instalação e execução
- [ ] watsonx: implementado e ativo **ou** claramente documentado como pendente
- [ ] Repositório sem segredos, tokens ou dados reais
- [ ] Branches mergeadas e `main` publicada no GitHub

---

## Dependências entre Tarefas

```
[Bob 2] models.py ──────────────────────────────┐
[Bob 2] risk_engine.py ─────────────────────────┤
[Bob 2] generator.py ───────────────────────────┤──▶ [Bob 3] app.py (interface)
[Bob 2] tests/ ─────────────────────────────────┘
                                                  ▲
[Bob 1] conftest.py ────────────────────────────┘
[Bob 1] watsonx_client.py ──── opcional ──────────▶ [Bob 1] integração final
```

> Todas as dependências do Bob 3 já estão implementadas e disponíveis na `main`.
> Bob 2 e Bob 3 podem trabalhar em paralelo sem bloqueios.
