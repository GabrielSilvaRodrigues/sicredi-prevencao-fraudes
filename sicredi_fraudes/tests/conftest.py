"""
conftest.py — Fixtures compartilhadas para os testes.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from datetime import datetime
from src.core.models import PerfilAssociado, Transacao
from src.data.generator import gerar_perfil, gerar_dataset_demo

HORA_BASE = datetime(2025, 6, 15, 14, 30, 0)


@pytest.fixture
def perfil_padrao():
    """Perfil fictício reprodutível."""
    import random
    rng = random.Random(99)
    p = gerar_perfil("TST001", rng)
    # Força valores determinísticos para os testes
    p.valor_medio_transacao = 200.0
    p.desvio_padrao_valor = 50.0
    p.categorias_frequentes = ["Supermercado", "Farmácia", "Restaurante"]
    p.cidades_frequentes = ["Porto Alegre", "Canoas"]
    p.horario_habitual_inicio = 8
    p.horario_habitual_fim = 22
    return p


@pytest.fixture
def tx_normal(perfil_padrao):
    """Transação completamente dentro do padrão."""
    return Transacao(
        id="TX_NORMAL",
        associado_id="TST001",
        valor=180.0,
        data_hora=HORA_BASE,
        categoria="Supermercado",
        estabelecimento="Zaffari",
        cidade="Porto Alegre",
        estado="RS",
        pais="Brasil",
        distancia_residencia_km=5.0,
        canal="Presencial",
    )


@pytest.fixture
def dataset_demo():
    """Dataset completo de demonstração."""
    return gerar_dataset_demo(n_normais=20, n_suspeitas=6)
