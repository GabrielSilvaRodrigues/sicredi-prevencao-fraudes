"""
models.py — Modelos de dados (dataclasses) utilizados no sistema.
Representa transações, perfis de associados e resultados de análise.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Transacao:
    """Representa uma transação de cartão."""
    id: str
    associado_id: str
    valor: float                     # R$
    data_hora: datetime
    categoria: str                   # ex.: "Supermercado", "Eletrônicos"
    estabelecimento: str
    cidade: str
    estado: str
    pais: str = "Brasil"
    distancia_residencia_km: float = 0.0   # distância estimada da residência
    canal: str = "Presencial"              # Presencial / Online / App


@dataclass
class PerfilAssociado:
    """Perfil de consumo histórico fictício do associado."""
    associado_id: str
    nome: str
    valor_medio_transacao: float           # média histórica de valor
    desvio_padrao_valor: float             # variação habitual
    categorias_frequentes: list            # ex.: ["Supermercado", "Farmácia"]
    cidades_frequentes: list               # cidades onde costuma comprar
    limite_diario: float
    transacoes_por_hora_normal: float      # média de tx por hora em uso normal
    horario_habitual_inicio: int           # hora (0-23) início do padrão
    horario_habitual_fim: int              # hora (0-23) fim do padrão


@dataclass
class FatorRisco:
    """Um fator individual que contribuiu para a pontuação de risco."""
    nome: str
    descricao: str
    pontos: float          # contribuição para a pontuação total (0-100)
    nivel: str             # "baixo", "medio", "alto"


@dataclass
class ResultadoAnalise:
    """Resultado completo da análise de uma transação."""
    transacao_id: str
    associado_id: str
    pontuacao: float                     # 0-100
    nivel_risco: str                     # "baixo", "medio", "alto"
    fatores: list                        # lista de FatorRisco
    recomendacao: str
    justificativa: str
    eh_fraude_confirmada: bool = False   # nunca True sem confirmação humana
    analisado_em: datetime = field(default_factory=datetime.now)
    fonte_analise: str = "motor_local"   # "motor_local" ou "watsonx"
