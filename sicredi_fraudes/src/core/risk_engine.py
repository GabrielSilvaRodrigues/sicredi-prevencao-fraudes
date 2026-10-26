"""
risk_engine.py — Motor de avaliação de risco modular e transparente.

Cada regra retorna um FatorRisco com sua contribuição individual.
A pontuação final é a soma ponderada dos fatores, limitada a 0-100.

Níveis de risco:
  0 – 39  → baixo
  40 – 69 → médio
  70 – 100 → alto

Este módulo NÃO depende de modelos generativos. Qualquer integração
com IA (watsonx) é realizada em camada separada (watsonx_client.py)
e pode enriquecer a explicação, mas não altera a pontuação calculada.
"""
from __future__ import annotations

import math
from datetime import datetime, timedelta
from typing import List

from src.core.models import FatorRisco, PerfilAssociado, ResultadoAnalise, Transacao

# ---------------------------------------------------------------------------
# Constantes de peso (ajustáveis sem alterar a lógica de cada regra)
# ---------------------------------------------------------------------------
PESO_VALOR_ALTO = 30
PESO_CATEGORIA_INCOMUM = 20
PESO_LOCALIZACAO_INCOMUM = 25
PESO_HORARIO_INCOMUM = 15
PESO_VELOCIDADE_TRANSACOES = 25
PESO_PAIS_ESTRANGEIRO = 25
PESO_CANAL_SUSPEITO = 15
PESO_VIAGEM_IMPOSSIVEL = 30


def _nivel_por_pontos(pontos: float) -> str:
    if pontos >= 10:
        return "alto"
    if pontos >= 5:
        return "medio"
    return "baixo"


# ---------------------------------------------------------------------------
# Regras individuais
# ---------------------------------------------------------------------------

def regra_valor_alto(tx: Transacao, perfil: PerfilAssociado) -> FatorRisco | None:
    """Penaliza valores muito acima do padrão histórico do associado."""
    if perfil.desvio_padrao_valor == 0:
        return None
    z = (tx.valor - perfil.valor_medio_transacao) / perfil.desvio_padrao_valor
    if z <= 1.5:
        return None
    # Escala: z=1.5 → ~5 pts; z=4 → 25 pts
    pontos = min(PESO_VALOR_ALTO, round((z - 1.5) / 2.5 * PESO_VALOR_ALTO, 1))
    return FatorRisco(
        nome="Valor elevado",
        descricao=(
            f"O valor R$ {tx.valor:,.2f} é {z:.1f} desvios-padrão acima da "
            f"média habitual do associado (R$ {perfil.valor_medio_transacao:,.2f})."
        ),
        pontos=pontos,
        nivel=_nivel_por_pontos(pontos),
    )


def regra_categoria_incomum(tx: Transacao, perfil: PerfilAssociado) -> FatorRisco | None:
    """Penaliza categorias raramente usadas pelo associado."""
    categorias = [c.lower() for c in perfil.categorias_frequentes]
    if tx.categoria.lower() in categorias:
        return None
    pontos = PESO_CATEGORIA_INCOMUM
    return FatorRisco(
        nome="Categoria incomum",
        descricao=(
            f"A categoria '{tx.categoria}' não faz parte do perfil habitual "
            f"do associado ({', '.join(perfil.categorias_frequentes)})."
        ),
        pontos=pontos,
        nivel=_nivel_por_pontos(pontos),
    )


def regra_localizacao_incomum(tx: Transacao, perfil: PerfilAssociado) -> FatorRisco | None:
    """Penaliza transações em cidades fora do histórico."""
    cidades = [c.lower() for c in perfil.cidades_frequentes]
    if tx.cidade.lower() in cidades:
        return None
    # Distância adiciona peso
    base = PESO_LOCALIZACAO_INCOMUM
    extra = min(5, tx.distancia_residencia_km / 200)
    pontos = round(base + extra, 1)
    return FatorRisco(
        nome="Localização incomum",
        descricao=(
            f"Transação em {tx.cidade}/{tx.estado}, distante ~{tx.distancia_residencia_km:.0f} km "
            f"da residência do associado. Cidades habituais: {', '.join(perfil.cidades_frequentes)}."
        ),
        pontos=pontos,
        nivel=_nivel_por_pontos(pontos),
    )


def regra_horario_incomum(tx: Transacao, perfil: PerfilAssociado) -> FatorRisco | None:
    """Penaliza transações fora do horário habitual do associado."""
    hora = tx.data_hora.hour
    inicio = perfil.horario_habitual_inicio
    fim = perfil.horario_habitual_fim
    # Intervalo pode cruzar meia-noite
    if inicio <= fim:
        dentro = inicio <= hora <= fim
    else:
        dentro = hora >= inicio or hora <= fim
    if dentro:
        return None
    pontos = PESO_HORARIO_INCOMUM
    return FatorRisco(
        nome="Horário incomum",
        descricao=(
            f"Transação realizada às {hora:02d}h, fora do horário habitual "
            f"({inicio:02d}h–{fim:02d}h) do associado."
        ),
        pontos=pontos,
        nivel=_nivel_por_pontos(pontos),
    )


def regra_velocidade_transacoes(
    tx: Transacao,
    historico_recente: List[Transacao],
    janela_minutos: int = 30,
) -> FatorRisco | None:
    """Penaliza muitas transações em curto intervalo de tempo."""
    limite = tx.data_hora - timedelta(minutes=janela_minutos)
    recentes = [
        t for t in historico_recente
        if t.id != tx.id and t.associado_id == tx.associado_id and t.data_hora >= limite
    ]
    quantidade = len(recentes)
    if quantidade < 3:
        return None
    pontos = min(PESO_VELOCIDADE_TRANSACOES, round(quantidade * 4, 1))
    return FatorRisco(
        nome="Alta frequência",
        descricao=(
            f"{quantidade} transações nos últimos {janela_minutos} minutos. "
            "Padrão incomum que pode indicar uso não autorizado do cartão."
        ),
        pontos=pontos,
        nivel=_nivel_por_pontos(pontos),
    )


def regra_pais_estrangeiro(tx: Transacao, perfil: PerfilAssociado) -> FatorRisco | None:
    """Penaliza transações fora do país de residência."""
    if tx.pais.lower() in ("brasil", "brazil"):
        return None
    pontos = PESO_PAIS_ESTRANGEIRO
    return FatorRisco(
        nome="País estrangeiro",
        descricao=f"Transação registrada em '{tx.pais}', fora do país de residência.",
        pontos=pontos,
        nivel=_nivel_por_pontos(pontos),
    )


def regra_canal_suspeito(tx: Transacao) -> FatorRisco | None:
    """Leve penalização para transações online de alto valor."""
    if tx.canal.lower() != "online":
        return None
    if tx.valor < 500:
        return None
    pontos = PESO_CANAL_SUSPEITO
    return FatorRisco(
        nome="Compra online de alto valor",
        descricao=(
            f"Transação online de R$ {tx.valor:,.2f}. "
            "Compras online de alto valor merecem atenção adicional."
        ),
        pontos=pontos,
        nivel=_nivel_por_pontos(pontos),
    )


def regra_viagem_impossivel(
    tx: Transacao,
    historico_recente: List[Transacao],
    velocidade_maxima_kmh: float = 800.0,  # avião comercial
) -> FatorRisco | None:
    """
    Detecta transações geograficamente impossíveis em curto intervalo.

    Se o mesmo associado realizou uma transação anterior em local com
    distância_residencia_km diferente da atual, calcula se seria fisicamente
    possível deslocar-se entre os dois pontos no tempo disponível.
    Usa distancia_residencia_km como proxy de localização (sem coordenadas exatas).
    """
    for tx_ant in historico_recente:
        if tx_ant.id == tx.id or tx_ant.associado_id != tx.associado_id:
            continue
        # Só avalia transações anteriores à atual
        if tx_ant.data_hora >= tx.data_hora:
            continue
        delta_segundos = (tx.data_hora - tx_ant.data_hora).total_seconds()
        if delta_segundos <= 0:
            continue
        delta_horas = delta_segundos / 3600.0
        # Distância entre os pontos (diferença das distâncias à residência como proxy)
        dist_estimada_km = abs(tx.distancia_residencia_km - tx_ant.distancia_residencia_km)
        if dist_estimada_km < 100:
            continue  # Pontos próximos — sem suspeita
        velocidade_necessaria = dist_estimada_km / delta_horas
        if velocidade_necessaria > velocidade_maxima_kmh:
            pontos = PESO_VIAGEM_IMPOSSIVEL
            return FatorRisco(
                nome="Viagem impossível",
                descricao=(
                    f"Transação em local ~{dist_estimada_km:.0f} km distante da anterior "
                    f"({tx_ant.cidade}, {delta_horas * 60:.0f} min atrás). "
                    f"Velocidade necessária: {velocidade_necessaria:.0f} km/h — "
                    "fisicamente impossível sem uso simultâneo do cartão."
                ),
                pontos=pontos,
                nivel=_nivel_por_pontos(pontos),
            )
    return None


# ---------------------------------------------------------------------------
# Função principal de avaliação
# ---------------------------------------------------------------------------

def avaliar_transacao(
    tx: Transacao,
    perfil: PerfilAssociado,
    historico_recente: List[Transacao] | None = None,
) -> ResultadoAnalise:
    """
    Avalia uma transação e retorna um ResultadoAnalise completo.
    A pontuação é calculada de forma determinística e auditável.
    """
    if historico_recente is None:
        historico_recente = []

    fatores: List[FatorRisco] = []

    # Aplica todas as regras
    regras_simples = [
        regra_valor_alto(tx, perfil),
        regra_categoria_incomum(tx, perfil),
        regra_localizacao_incomum(tx, perfil),
        regra_horario_incomum(tx, perfil),
        regra_pais_estrangeiro(tx, perfil),
        regra_canal_suspeito(tx),
    ]
    for r in regras_simples:
        if r is not None:
            fatores.append(r)

    r_velocidade = regra_velocidade_transacoes(tx, historico_recente)
    if r_velocidade is not None:
        fatores.append(r_velocidade)

    r_viagem = regra_viagem_impossivel(tx, historico_recente)
    if r_viagem is not None:
        fatores.append(r_viagem)

    # Pontuação total limitada a 0-100
    pontuacao = min(100.0, round(sum(f.pontos for f in fatores), 1))

    # Nível de risco
    if pontuacao >= 60:
        nivel = "alto"
    elif pontuacao >= 15:
        nivel = "medio"
    else:
        nivel = "baixo"

    # Recomendação e justificativa
    recomendacao, justificativa = _gerar_recomendacao(nivel, fatores, tx)

    return ResultadoAnalise(
        transacao_id=tx.id,
        associado_id=tx.associado_id,
        pontuacao=pontuacao,
        nivel_risco=nivel,
        fatores=fatores,
        recomendacao=recomendacao,
        justificativa=justificativa,
        eh_fraude_confirmada=False,  # nunca confirmada automaticamente
        fonte_analise="motor_local",
    )


# ---------------------------------------------------------------------------
# Geração de recomendação
# ---------------------------------------------------------------------------

def _gerar_recomendacao(
    nivel: str,
    fatores: List[FatorRisco],
    tx: Transacao,
) -> tuple[str, str]:
    nomes_fatores = [f.nome for f in fatores]

    if nivel == "alto":
        recomendacao = (
            "🔴 Solicitar confirmação imediata ao associado via app/SMS antes "
            "de autorizar a transação. Encaminhar para revisão humana."
        )
        justificativa = (
            f"A transação de R$ {tx.valor:,.2f} em '{tx.estabelecimento}' apresentou "
            f"{len(fatores)} indicador(es) de risco: {', '.join(nomes_fatores)}. "
            "A combinação desses fatores resulta em pontuação elevada. "
            "⚠️ Isso é um sinal de alerta — não uma confirmação de fraude."
        )
    elif nivel == "medio":
        recomendacao = (
            "🟡 Monitorar a transação e registrar para análise posterior. "
            "Considerar notificação ao associado para confirmação voluntária."
        )
        justificativa = (
            f"A transação de R$ {tx.valor:,.2f} em '{tx.estabelecimento}' apresentou "
            f"{len(fatores)} indicador(es): {', '.join(nomes_fatores)}. "
            "O nível médio requer atenção, mas a transação pode ser legítima."
        )
    else:
        recomendacao = "🟢 Transação dentro do padrão esperado. Nenhuma ação necessária."
        if fatores:
            justificativa = (
                f"Um ou mais indicadores foram observados ({', '.join(nomes_fatores)}), "
                "porém a pontuação total permanece baixa. A transação é considerada normal."
            )
        else:
            justificativa = (
                f"A transação de R$ {tx.valor:,.2f} em '{tx.estabelecimento}' "
                "está completamente dentro do perfil habitual do associado."
            )

    return recomendacao, justificativa
