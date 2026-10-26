# IBM watsonx Orchestrate — Plano de Integração

## Status Atual

> **INTEGRAÇÃO PENDENTE DE CONFIGURAÇÃO**
>
> O código de integração está implementado em `src/core/watsonx_client.py`,
> mas **não realiza chamadas reais** enquanto as credenciais não forem configuradas.
> O sistema opera completamente com o motor local quando o watsonx não está disponível.

---

## O que o watsonx faz neste projeto

O watsonx **NÃO** substitui o motor de análise de risco — ele **enriquece a explicação**:

| Componente | Responsável |
|---|---|
| Cálculo da pontuação (0-100) | Motor local (`risk_engine.py`) |
| Classificação do risco (baixo/médio/alto) | Motor local |
| Fatores identificados | Motor local |
| **Explicação em linguagem natural** | **watsonx (quando configurado)** |
| Recomendação preventiva | Motor local (fallback quando watsonx indisponível) |

---

## Fluxo Agêntico Proposto

```
┌─────────────────────────────────────────────────────────┐
│                   ENTRADA                                │
│   Dados da transação + Perfil do associado              │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  PASSO 1 — Validação dos campos de entrada              │
│  ✓ Verificar campos obrigatórios da Transacao            │
│  ✓ Verificar tipos e faixas de valores (valor ≥ 0)      │
│  ✓ Verificar data_hora não nula                         │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  PASSO 2 — Avaliação de Risco (motor local)             │
│  avaliar_transacao(tx, perfil, historico_recente)        │
│  → ResultadoAnalise com pontuação e fatores             │
└──────────────────────┬──────────────────────────────────┘
                       │
             ┌─────────┴─────────┐
             │                   │
        watsonx                sem watsonx
       habilitado?              
             │                   │
             ▼                   ▼
┌────────────────────┐  ┌────────────────────────────────┐
│  PASSO 3A —        │  │  PASSO 3B —                    │
│  Enriquecer via    │  │  Usar justificativa do motor    │
│  watsonx Granite   │  │  local (já gerada)             │
│  (LLM)             │  │                                │
└─────────┬──────────┘  └──────────────┬─────────────────┘
          │                             │
          └───────────┬─────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│  PASSO 4 — Roteamento por nível de risco                │
│                                                         │
│  baixo  →  Registrar, sem ação imediata                │
│  médio  →  Notificar associado para confirmação        │
│  alto   →  Encaminhar para fila de revisão humana      │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  PASSO 5 — Resultado estruturado                        │
│                                                         │
│  {                                                      │
│    transacao_id,                                        │
│    pontuacao,                                           │
│    nivel_risco,                                         │
│    fatores: [...],                                      │
│    explicacao_natural,                                  │
│    recomendacao,                                        │
│    requer_revisao_humana: bool,                         │
│    eh_fraude_confirmada: false                          │
│  }                                                      │
└─────────────────────────────────────────────────────────┘
```

---

## Prompt Utilizado para o Modelo Granite

O prompt atual está em `src/core/watsonx_client.py`, função `_montar_prompt()`:

```
Você é um assistente especialista em segurança financeira do Sicredi.
Analise a transação a seguir e explique em português, de forma clara e empática,
por que ela recebeu esse nível de risco. Lembre ao associado que este é um sinal
de alerta, não uma confirmação de fraude.

Dados da transação: {dados_transacao}
Pontuação de risco: {pontuacao}/100
Nível de risco: {nivel_risco}
Fatores identificados: {fatores_resumo}

Explicação (máximo 3 parágrafos):
```

---

## Requisitos para Ativar a Integração

### Credenciais necessárias

```bash
# Criar arquivo .env na raiz do projeto (NUNCA commitar)
WATSONX_API_KEY=sua-api-key-ibm-cloud
WATSONX_PROJECT_ID=seu-project-id-watsonx
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_MODEL_ID=ibm/granite-13b-instruct-v2
```

### Dependência adicional

```bash
pip install ibm-watsonx-ai
```

> A dependência `ibm-watsonx-ai` está comentada no `requirements.txt` para não
> bloquear a instalação quando a integração não está configurada.

### Verificar se está funcionando

```python
from src.core.watsonx_client import status_integracao
status = status_integracao()
print(status["habilitado"])   # deve ser True
print(status["mensagem"])
```

---

## Como Obter as Credenciais

1. Acessar [IBM Cloud](https://cloud.ibm.com) com conta IBM
2. Criar ou acessar uma instância do **Watson Machine Learning**
3. Acessar [IBM watsonx.ai](https://dataplatform.cloud.ibm.com)
4. Criar um projeto em watsonx.ai
5. Obter o **Project ID** nas configurações do projeto
6. Gerar uma **API Key** em: Gerenciar → Acesso → Chaves de API do IBM Cloud

---

## Limitações Documentadas

| Limitação | Descrição |
|---|---|
| **Sem credenciais** | Sistema funciona 100% sem watsonx — motor local assume |
| **Latência** | Chamadas ao LLM adicionam 2-5s; usar apenas para explicações |
| **Pontuação imutável** | watsonx enriquece texto — nunca altera a pontuação calculada |
| **Sem ações reais** | Sistema não bloqueia cartões reais nem envia notificações reais |
| **Dados fictícios** | Nenhum dado real de cliente é enviado ao watsonx |
| **Modelo IBM Granite** | Modelo padrão: `ibm/granite-13b-instruct-v2` (ajustável via env) |

---

## O IBM Bob não é o watsonx Orchestrate

O **IBM Bob** é uma ferramenta de desenvolvimento de software (IDE assistida por IA).
Ele foi usado para desenvolver este projeto, mas **não executa o agente em produção**.

O **watsonx Orchestrate** é a plataforma de IA da IBM para automação de fluxos de trabalho.
Este projeto está preparado para se integrar a ela, mas a integração está pendente de
acesso à plataforma e configuração das credenciais.
