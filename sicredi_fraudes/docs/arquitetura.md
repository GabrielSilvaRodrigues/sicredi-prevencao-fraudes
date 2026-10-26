# Arquitetura Técnica — Prevenção Inteligente a Fraudes

## Visão Geral

O sistema é composto por três camadas principais, separadas por responsabilidade:

```
┌─────────────────────────────────────────────────────────────┐
│                     CAMADA DE INTERFACE                      │
│               app.py (Streamlit)                            │
│   Painel │ Detalhe │ Simulador │ Histórico │ Sobre          │
└──────────────────────┬──────────────────────────────────────┘
                       │ chama
┌──────────────────────▼──────────────────────────────────────┐
│                   CAMADA DE NEGÓCIO                         │
│                                                              │
│  src/core/risk_engine.py   ←   src/core/models.py           │
│  ├── regra_valor_alto()                                      │
│  ├── regra_categoria_incomum()                               │
│  ├── regra_localizacao_incomum()                             │
│  ├── regra_horario_incomum()                                 │
│  ├── regra_velocidade_transacoes()                           │
│  ├── regra_pais_estrangeiro()                                │
│  ├── regra_canal_suspeito()                                  │
│  └── avaliar_transacao()  ← função principal                 │
│                                                              │
│  src/core/watsonx_client.py  (integração planejada)          │
└──────────────────────┬──────────────────────────────────────┘
                       │ usa
┌──────────────────────▼──────────────────────────────────────┐
│                    CAMADA DE DADOS                           │
│              src/data/generator.py                          │
│   Perfis fictícios │ Transações sintéticas │ Dataset demo   │
└─────────────────────────────────────────────────────────────┘
```

---

## Módulos

### `src/core/models.py`
Define as estruturas de dados com `dataclass`:

| Classe | Responsabilidade |
|---|---|
| `Transacao` | Representa uma transação de cartão |
| `PerfilAssociado` | Perfil histórico fictício do associado |
| `FatorRisco` | Um fator individual de risco com nome, descrição e pontuação |
| `ResultadoAnalise` | Resultado completo da análise |

### `src/core/risk_engine.py`
Motor de avaliação de risco **determinístico e auditável**:

- Cada regra é uma função independente que retorna `FatorRisco | None`
- Nenhuma regra depende das outras (baixo acoplamento)
- A pontuação final é a soma das contribuições, limitada a 100
- Nenhuma IA generativa é necessária para calcular a pontuação
- Cada fator tem uma descrição em linguagem natural

**Escala de risco:**
| Pontuação | Nível | Cor |
|---|---|---|
| 0–39 | Baixo | 🟢 Verde |
| 40–69 | Médio | 🟡 Amarelo |
| 70–100 | Alto | 🔴 Vermelho |

### `src/core/watsonx_client.py`
Ponto de integração com IBM watsonx Orchestrate:

- Detecta automaticamente se as credenciais estão configuradas
- Se disponível: solicita ao modelo de linguagem uma explicação enriquecida
- Se indisponível: sistema opera normalmente com explicações locais
- **NÃO altera a pontuação calculada** — apenas enriquece a linguagem

### `src/data/generator.py`
Gerador determinístico de dados sintéticos:

- `gerar_perfil()` — cria um perfil fictício de associado
- `gerar_transacao_normal()` — transação dentro do padrão do associado
- `gerar_transacao_suspeita()` — transação com padrão específico suspeito
- `gerar_dataset_demo()` — dataset completo para demonstração
- `transacoes_para_dataframe()` — conversão para pandas DataFrame

---

## Decisões de Design

### Por que Streamlit?
- Prototipagem rápida com Python puro
- Sem necessidade de frontend separado
- Gráficos interativos com Plotly integrado
- Facilidade de demonstração ao vivo

### Por que regras explícitas em vez de ML?
- Transparência total: cada ponto da pontuação é rastreável
- Funciona sem dados de treinamento
- Fácil de auditar e ajustar
- Base sólida para uma camada de ML posterior

### Por que `dataclasses`?
- Estruturas simples e legíveis
- Sem dependência de banco de dados (protótipo)
- Fácil serialização para JSON ou DataFrames

---

## Fluxo de Dados

```
Entrada: Transacao + PerfilAssociado + Historico[]
    │
    ▼ avaliar_transacao()
    ├── Para cada regra:
    │     regra(tx, perfil) → FatorRisco | None
    │
    ├── Soma pontuações dos fatores
    │
    ├── Classifica nível de risco
    │
    ├── Gera recomendação e justificativa
    │
    └── Retorna ResultadoAnalise
              ├── pontuacao: float [0, 100]
              ├── nivel_risco: "baixo" | "medio" | "alto"
              ├── fatores: List[FatorRisco]
              ├── recomendacao: str
              ├── justificativa: str
              └── eh_fraude_confirmada: False  ← sempre False
```

---

## Segurança

- Credenciais gerenciadas por variáveis de ambiente (`.env`)
- Nunca armazenadas no código-fonte
- `.gitignore` protege o arquivo `.env`
- Nenhum dado pessoal real é processado ou armazenado
