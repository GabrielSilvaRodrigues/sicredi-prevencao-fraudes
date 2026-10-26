# Guia de Configuração — IBM watsonx Orchestrate

## Status Atual

⚙️ **Integração planejada — pendente de credenciais e acesso à plataforma.**

O sistema funciona completamente sem essa integração. O watsonx Orchestrate é
utilizado para **enriquecer as explicações** com linguagem natural, mas não
para calcular a pontuação de risco (que é determinística e local).

---

## O que o watsonx Orchestrate faz neste projeto

| Responsabilidade | Motor Local | watsonx Orchestrate |
|---|---|---|
| Calcular pontuação de risco | ✅ | ❌ (não interfere) |
| Identificar fatores de risco | ✅ | ❌ |
| Gerar recomendação preventiva | ✅ | ❌ |
| Enriquecer explicação em linguagem natural | ⚙️ básico | ✅ avançado |
| Orquestrar o fluxo do agente | ❌ | ✅ |

---

## Pré-requisitos

1. Conta IBM Cloud ativa
2. Projeto criado no IBM watsonx.ai
3. API Key com permissões de leitura/escrita no projeto
4. URL do endpoint (ex.: `https://us-south.ml.cloud.ibm.com`)

---

## Passo 1 — Obter Credenciais

1. Acesse [https://cloud.ibm.com](https://cloud.ibm.com)
2. Navegue até **Manage → Access (IAM) → API Keys**
3. Crie uma nova API Key e **copie imediatamente** (não é exibida novamente)
4. Anote o **Project ID** do seu projeto watsonx.ai (visível nas configurações do projeto)

---

## Passo 2 — Configurar o Arquivo `.env`

Na pasta `sicredi_fraudes/`, crie um arquivo chamado `.env`:

```env
WATSONX_API_KEY=sua_api_key_aqui
WATSONX_PROJECT_ID=seu_project_id_aqui
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_MODEL_ID=ibm/granite-13b-instruct-v2
```

> ⚠️ **NUNCA commite este arquivo.** Ele está no `.gitignore`.
> Se você acidentalmente o commitar, revogue a API Key imediatamente.

---

## Passo 3 — Instalar o SDK

```bash
pip install ibm-watsonx-ai
```

---

## Passo 4 — Verificar a Integração

Execute a aplicação:

```bash
streamlit run app.py
```

Na barra lateral, o indicador de status deve mostrar:
> ✅ watsonx Orchestrate configurado e ativo.

---

## Configuração no watsonx Orchestrate (Fluxo)

Para configurar o agente completo na plataforma:

1. Acesse [https://www.ibm.com/products/watsonx-orchestrate](https://www.ibm.com/products/watsonx-orchestrate)
2. Crie um novo **Agente**
3. Importe as ferramentas descritas em `docs/watsonx/fluxo_agente.md`
4. Configure o modelo base: **IBM Granite 13B Instruct**
5. Defina o prompt do sistema (exemplo abaixo)

### Prompt do Sistema Recomendado

```
Você é um assistente especialista em segurança financeira do Sicredi.
Seu papel é analisar resultados de avaliação de risco de transações
e explicar, de forma clara e empática em português do Brasil, por que
uma transação recebeu determinada pontuação.

Regras importantes:
- Nunca confirme uma fraude sem revisão humana
- Nunca bloqueie cartões automaticamente
- Sempre deixe claro que se trata de um sinal de alerta, não uma certeza
- Use linguagem simples e acessível para o associado
- Baseie-se APENAS nos fatores fornecidos pelo motor de risco
- Não invente dados ou fatores adicionais
```

---

## Arquivos Relevantes

| Arquivo | Função |
|---|---|
| `src/core/watsonx_client.py` | Código de integração |
| `docs/watsonx/fluxo_agente.md` | Diagrama e descrição do fluxo |
| `.env` (criar manualmente) | Credenciais locais (não commitar) |

---

## Modelos Disponíveis no watsonx.ai

| Modelo | Uso Recomendado |
|---|---|
| `ibm/granite-13b-instruct-v2` | Explicações e recomendações |
| `ibm/granite-8b-code-instruct` | Geração de código auxiliar |
| `meta-llama/llama-3-70b-instruct` | Raciocínio mais complexo |

---

## Suporte

- Documentação oficial: [https://ibm.github.io/watsonx-ai-python-sdk/](https://ibm.github.io/watsonx-ai-python-sdk/)
- Console IBM Cloud: [https://cloud.ibm.com](https://cloud.ibm.com)
