"""
watsonx_client.py — Ponto de integração com o IBM watsonx Orchestrate.

STATUS: INTEGRAÇÃO PENDENTE DE CONFIGURAÇÃO
-------------------------------------------
Este módulo prepara a interface de comunicação com o watsonx Orchestrate,
mas NÃO realiza chamadas reais enquanto as credenciais não forem configuradas.

Quando habilitado, o watsonx enriquece a *explicação* da análise com
linguagem natural, mas NÃO altera a pontuação calculada pelo motor local.

Para ativar: defina as variáveis no arquivo .env (veja docs/watsonx/).
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

# Tenta carregar variáveis de ambiente de um arquivo .env local
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

WATSONX_ENABLED = (
    os.getenv("WATSONX_API_KEY") is not None
    and os.getenv("WATSONX_PROJECT_ID") is not None
    and os.getenv("WATSONX_URL") is not None
)


@dataclass
class WatsonxConfig:
    api_key: str
    project_id: str
    url: str
    model_id: str = "meta-llama/llama-3-3-70b-instruct"


def _get_config() -> Optional[WatsonxConfig]:
    api_key = os.getenv("WATSONX_API_KEY", "")
    project_id = os.getenv("WATSONX_PROJECT_ID", "")
    url = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
    model_id = os.getenv("WATSONX_MODEL_ID", "meta-llama/llama-3-3-70b-instruct")
    if api_key and project_id:
        return WatsonxConfig(api_key=api_key, project_id=project_id, url=url, model_id=model_id)
    return None


def enriquecer_explicacao(
    pontuacao: float,
    nivel_risco: str,
    fatores_resumo: str,
    dados_transacao: str,
) -> str:
    """
    Solicita ao watsonx uma explicação em linguagem natural para o resultado.

    Se as credenciais não estiverem configuradas, retorna None e o sistema
    usa apenas a justificativa gerada localmente.

    Parâmetros
    ----------
    pontuacao : float
        Pontuação de risco calculada pelo motor local (0-100).
    nivel_risco : str
        "baixo", "medio" ou "alto".
    fatores_resumo : str
        Texto com os fatores de risco identificados.
    dados_transacao : str
        Resumo da transação (sem dados pessoais reais).

    Retorna
    -------
    str ou None
        Explicação gerada pelo modelo, ou None se indisponível.
    """
    config = _get_config()
    if config is None:
        return None  # Motor local assume o controle

    # -----------------------------------------------------------------------
    # Integração real com ibm-watsonx-ai SDK
    # O SDK não está instalado por padrão para evitar dependências desnecessárias
    # quando a integração ainda não está configurada.
    # -----------------------------------------------------------------------
    try:
        from ibm_watsonx_ai import APIClient, Credentials  # type: ignore
        from ibm_watsonx_ai.foundation_models import ModelInference  # type: ignore
    except ImportError:
        return None

    prompt = _montar_prompt(pontuacao, nivel_risco, fatores_resumo, dados_transacao)

    try:
        credentials = Credentials(url=config.url, api_key=config.api_key)
        client = APIClient(credentials)
        model = ModelInference(
            model_id=config.model_id,
            api_client=client,
            project_id=config.project_id,
        )
        # Usa a API de chat (não depreciada) quando disponível, com fallback para generate_text
        try:
            messages = [{"role": "user", "content": prompt}]
            resposta = model.chat(messages=messages, params={"max_tokens": 300, "temperature": 0.2})
            return str(resposta["choices"][0]["message"]["content"]).strip()
        except Exception:
            resposta = model.generate_text(
                prompt=prompt,
                params={"max_new_tokens": 300, "temperature": 0.2},
            )
            return str(resposta).strip()
    except Exception as exc:  # noqa: BLE001
        # Falha silenciosa: o sistema continua com a explicação local
        print(f"[watsonx] Aviso: não foi possível obter explicação ({exc})")
        return None


def _montar_prompt(
    pontuacao: float,
    nivel_risco: str,
    fatores_resumo: str,
    dados_transacao: str,
) -> str:
    """Monta o prompt enviado ao modelo de linguagem."""
    return f"""Você é um assistente especialista em segurança financeira do Sicredi.
Analise a transação a seguir e explique em português, de forma clara e empática,
por que ela recebeu esse nível de risco. Lembre ao associado que este é um sinal
de alerta, não uma confirmação de fraude.

Dados da transação: {dados_transacao}
Pontuação de risco: {pontuacao}/100
Nível de risco: {nivel_risco}
Fatores identificados: {fatores_resumo}

Explicação (máximo 3 parágrafos):"""


def status_integracao() -> dict:
    """Retorna o status atual da integração com o watsonx."""
    config = _get_config()
    return {
        "habilitado": WATSONX_ENABLED,
        "mensagem": (
            "✅ watsonx Orchestrate configurado e ativo."
            if WATSONX_ENABLED
            else "⚙️ watsonx não configurado — sistema operando com motor local."
        ),
        "modelo": config.model_id if config else "—",
    }
