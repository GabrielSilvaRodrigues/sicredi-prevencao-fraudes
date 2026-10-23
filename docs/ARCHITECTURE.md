# Arquitetura do Sistema — Prevenção Inteligente a Fraudes (Sicredi)

## Visão Geral

O sistema é um **protótipo de agente de IA** para análise de transações fictícias com cartão.
A arquitetura segue o princípio de separação de responsabilidades: o motor de risco é
independente da interface e de qualquer serviço de IA externo.

```
┌─────────────────────────────────────────────────────────┐
│                  Interface (Streamlit)                   │
│   app.py — Painel / Detalhe / Simulador / Histórico      │
└───────────────────────┬─────────────────────────────────┘
                        │ chama
                        ▼
┌─────────────────────────────────────────────────────────┐
│             Motor de Análise Antifraude                  │
│   src/core/risk_engine.py — avaliar_transacao()          │
│                                                          │
│   Regras:                                                │
│   ├── Valor elevado (z-score vs perfil)                  │
│   ├── Categoria incomum (fora do histórico)              │
│   ├── Localização incomum (cidade + distância)           │
│   ├── Horário fora do padrão                             │
│   ├── Alta frequência (janela de 30 min)                 │
│   ├── País estrangeiro                                   │
│   └── Canal suspeito (online + alto valor)               │
│                                                          │
│   Saída: ResultadoAnalise (pontuação 0-100, nível,       │
│          fatores, recomendação, justificativa)           │
└───────────┬──────────────────────┬──────────────────────┘
            │                      │ opcional
            ▼                      ▼
┌───────────────────┐   ┌──────────────────────────────────┐
│   Modelos de dados │   │   IBM watsonx Orchestrate        │
│   src/core/models  │   │   src/core/watsonx_client.py     │
│                    │   │                                  │
│   - Transacao      │   │   STATUS: pendente de config.    │
│   - PerfilAssociado│   │   Enriquece explicação em        │
│   - FatorRisco     │   │   linguagem natural — NÃO altera │
│   - ResultadoAnalise│  │   a pontuação calculada          │
└───────────────────┘   └──────────────────────────────────┘
            ▲
            │ gera
┌───────────────────┐
│  Gerador de Dados │
│  src/data/generator│
│  (dados sintéticos)│
└───────────────────┘
```

---

## Módulos e Responsabilidades

### `sicredi_fraudes/app.py`
- Ponto de entrada da aplicação Streamlit
- Gerencia o estado da sessão
- Chama `avaliar_transacao()` — nunca reimplementa lógica de risco
- Responsável pelo integrante de Interface (Bob 3)

### `sicredi_fraudes/src/core/models.py`
- **Contrato estável** entre todos os módulos
- Define: `Transacao`, `PerfilAssociado`, `FatorRisco`, `ResultadoAnalise`
- **Nenhum integrante deve alterar os campos sem consenso da equipe**

### `sicredi_fraudes/src/core/risk_engine.py`
- Implementa `avaliar_transacao(tx, perfil, historico_recente) → ResultadoAnalise`
- Motor determinístico e auditável — sem dependências externas
- Cada regra é uma função pura e testável individualmente
- Responsável pelo integrante de Análise Antifraude (Bob 2)

### `sicredi_fraudes/src/core/watsonx_client.py`
- Camada de integração opcional com IBM watsonx
- Expõe `enriquecer_explicacao()` e `status_integracao()`
- **Falha silenciosamente** — o sistema funciona sem ela
- Responsável pelo integrante de Integração/Testes (Bob 1 / Coordenador)

### `sicredi_fraudes/src/data/generator.py`
- Gera dados 100% fictícios e sintéticos para demonstração
- Expõe: `gerar_dataset_demo()`, `gerar_perfil()`, `gerar_transacao_normal()`,
  `gerar_transacao_suspeita()`, `transacoes_para_dataframe()`
- Responsável pelo integrante de Análise Antifraude (Bob 2)

### `sicredi_fraudes/tests/`
- Testes automatizados com pytest
- `conftest.py` — fixtures compartilhadas
- `test_risk_engine.py` — 6 cenários obrigatórios + regras individuais
- Responsável pelo integrante de Integração/Testes (Bob 1 / Coordenador)

---

## Contrato Principal

```python
# Importação
from src.core.risk_engine import avaliar_transacao
from src.core.models import Transacao, PerfilAssociado, ResultadoAnalise

# Chamada
resultado: ResultadoAnalise = avaliar_transacao(
    tx=transacao,               # Transacao
    perfil=perfil_associado,    # PerfilAssociado
    historico_recente=lista     # List[Transacao] | None
)

# Campos garantidos no resultado
resultado.transacao_id          # str
resultado.associado_id          # str
resultado.pontuacao             # float 0-100
resultado.nivel_risco           # "baixo" | "medio" | "alto"
resultado.fatores               # List[FatorRisco]
resultado.recomendacao          # str
resultado.justificativa         # str
resultado.eh_fraude_confirmada  # bool — sempre False no motor local
resultado.fonte_analise         # "motor_local" | "watsonx"
```

---

## Princípios de Design

1. **Transparência**: cada fator de risco tem nome, descrição e pontuação individual
2. **Determinismo**: mesma entrada → mesmo resultado (sem aleatoriedade na análise)
3. **Separação de responsabilidades**: interface nunca duplica lógica de risco
4. **Graceful degradation**: watsonx indisponível → sistema continua funcionando
5. **Dados fictícios**: nenhum dado real de clientes em nenhuma camada
6. **Revisão humana**: `eh_fraude_confirmada` nunca é `True` automaticamente

---

## Fluxo de uma Análise

```
1. Transação recebida (app.py ou simulador)
2. Perfil do associado carregado (gerador ou cache)
3. Histórico recente filtrado
4. avaliar_transacao() invocada
5. 7 regras executadas em sequência
6. Pontuação somada e limitada a 0-100
7. Nível de risco classificado (baixo/médio/alto)
8. Recomendação e justificativa geradas
9. [Opcional] watsonx enriquece a explicação
10. ResultadoAnalise retornado para a interface
11. Interface exibe painel, gauge e fatores
```
