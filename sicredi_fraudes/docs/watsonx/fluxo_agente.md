# Fluxo do Agente — IBM watsonx Orchestrate

## Visão Geral

Este documento descreve como o fluxo do agente de prevenção a fraudes
deve ser configurado no IBM watsonx Orchestrate.

**Status:** Arquitetura definida — integração pendente de credenciais e acesso à plataforma.

---

## Diagrama do Fluxo

```
┌────────────────────────────────────────────────────────────────┐
│                    IBM watsonx Orchestrate                      │
│                                                                  │
│  Entrada                                                         │
│  ┌──────────────────────────────────┐                           │
│  │  Dados da transação (JSON)       │                           │
│  │  - valor, data_hora, categoria   │                           │
│  │  - cidade, pais, canal           │                           │
│  │  - associado_id                  │                           │
│  └────────────┬─────────────────────┘                           │
│               │                                                  │
│               ▼                                                  │
│  ┌────────────────────────────────────┐                         │
│  │  Etapa 1: Validar Entrada          │                         │
│  │  Ferramenta: validar_transacao     │                         │
│  │  - Verifica campos obrigatórios    │                         │
│  │  - Normaliza formatos              │                         │
│  └────────────┬───────────────────────┘                         │
│               │                                                  │
│               ▼                                                  │
│  ┌────────────────────────────────────┐                         │
│  │  Etapa 2: Buscar Perfil            │                         │
│  │  Ferramenta: buscar_perfil_associado│                        │
│  │  - Recupera histórico do associado │                         │
│  │  - Retorna PerfilAssociado (JSON)  │                         │
│  └────────────┬───────────────────────┘                         │
│               │                                                  │
│               ▼                                                  │
│  ┌────────────────────────────────────┐                         │
│  │  Etapa 3: Calcular Risco           │                         │
│  │  Ferramenta: calcular_risco        │                         │
│  │  - Executa motor local (risk_engine)│                        │
│  │  - Retorna pontuação + fatores     │                         │
│  └────────────┬───────────────────────┘                         │
│               │                                                  │
│               ▼                                                  │
│  ┌────────────────────────────────────┐                         │
│  │  Etapa 4: Interpretar Resultado    │                         │
│  │  Modelo: IBM Granite               │                         │
│  │  - Recebe pontuação + fatores      │                         │
│  │  - Gera explicação em linguagem    │                         │
│  │    natural (português do Brasil)   │                         │
│  │  - NÃO altera a pontuação          │                         │
│  └────────────┬───────────────────────┘                         │
│               │                                                  │
│               ▼                                                  │
│  ┌────────────────────────────────────┐                         │
│  │  Etapa 5: Gerar Recomendação       │                         │
│  │  Ferramenta: gerar_recomendacao    │                         │
│  │  - Seleciona ação baseada no nível │                         │
│  │  - baixo → monitorar               │                         │
│  │  - medio → notificar associado     │                         │
│  │  - alto  → solicitar confirmação + │                         │
│  │            encaminhar para humano  │                         │
│  └────────────┬───────────────────────┘                         │
│               │                                                  │
│               ▼                                                  │
│  Saída                                                           │
│  ┌──────────────────────────────────┐                           │
│  │  Resposta estruturada (JSON)     │                           │
│  │  - nivel_risco                   │                           │
│  │  - pontuacao                     │                           │
│  │  - fatores[]                     │                           │
│  │  - recomendacao                  │                           │
│  │  - explicacao_ia                 │                           │
│  │  - eh_fraude_confirmada: false   │                           │
│  └──────────────────────────────────┘                           │
└────────────────────────────────────────────────────────────────┘
```

---

## Ferramentas do Agente

### `validar_transacao`
**Entrada:**
```json
{
  "id": "string",
  "associado_id": "string",
  "valor": "number",
  "data_hora": "string (ISO 8601)",
  "categoria": "string",
  "estabelecimento": "string",
  "cidade": "string",
  "estado": "string",
  "pais": "string",
  "distancia_residencia_km": "number",
  "canal": "Presencial | Online | App"
}
```
**Saída:** `{ "valido": true/false, "erros": [] }`

---

### `buscar_perfil_associado`
**Entrada:** `{ "associado_id": "string" }`
**Saída:**
```json
{
  "associado_id": "string",
  "valor_medio_transacao": "number",
  "desvio_padrao_valor": "number",
  "categorias_frequentes": ["string"],
  "cidades_frequentes": ["string"],
  "horario_habitual_inicio": "number",
  "horario_habitual_fim": "number"
}
```

---

### `calcular_risco`
**Entrada:** `{ "transacao": {...}, "perfil": {...}, "historico_recente": [...] }`
**Saída:**
```json
{
  "pontuacao": 0-100,
  "nivel_risco": "baixo | medio | alto",
  "fatores": [
    { "nome": "string", "descricao": "string", "pontos": "number" }
  ]
}
```

---

### `gerar_recomendacao`
**Entrada:** `{ "nivel_risco": "string", "fatores": [...], "transacao": {...} }`
**Saída:**
```json
{
  "recomendacao": "string",
  "justificativa": "string",
  "acao_requerida": "nenhuma | notificar | confirmar | revisar_humano"
}
```

---

## Decisões de Segurança do Agente

1. **Nunca bloqueia cartões automaticamente** — essa ação exige integração separada e autorizada.
2. **Nunca confirma fraude** — `eh_fraude_confirmada` é sempre `false` no protótipo.
3. **Nunca envia mensagens reais** — as recomendações são texto para revisão humana.
4. **Não altera a pontuação** — o modelo de linguagem só interpreta, não recalcula.
5. **Não inventa dados** — se o perfil do associado não existir, retorna erro explícito.

---

## Exemplo de Dados para Teste

### Transação de baixo risco
```json
{
  "id": "TESTE001",
  "associado_id": "ASS001",
  "valor": 120.00,
  "data_hora": "2025-06-15T14:30:00",
  "categoria": "Supermercado",
  "estabelecimento": "Zaffari",
  "cidade": "Porto Alegre",
  "estado": "RS",
  "pais": "Brasil",
  "distancia_residencia_km": 5.0,
  "canal": "Presencial"
}
```
**Resultado esperado:** pontuação < 40, nível "baixo"

---

### Transação de alto risco (múltiplos sinais)
```json
{
  "id": "TESTE002",
  "associado_id": "ASS001",
  "valor": 4500.00,
  "data_hora": "2025-06-15T03:15:00",
  "categoria": "Joalheria",
  "estabelecimento": "Joalheria Luxo Internacional",
  "cidade": "Buenos Aires",
  "estado": "--",
  "pais": "Argentina",
  "distancia_residencia_km": 2500.0,
  "canal": "Online"
}
```
**Resultado esperado:** pontuação >= 70, nível "alto", múltiplos fatores
