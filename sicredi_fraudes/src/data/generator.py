"""
generator.py — Gerador de dados fictícios sintéticos para demonstração.

Todos os nomes, documentos e transações são completamente inventados.
Nenhum dado real de clientes ou transações bancárias é utilizado.
"""
from __future__ import annotations

import random
import uuid
from datetime import datetime, timedelta
from typing import List, Tuple

import pandas as pd

from src.core.models import PerfilAssociado, Transacao

# Semente para reprodutibilidade nos testes
RANDOM_SEED = 42

CATEGORIAS = [
    "Supermercado", "Farmácia", "Posto de Combustível", "Restaurante",
    "Eletrônicos", "Vestuário", "Viagem", "Educação", "Saúde",
    "Entretenimento", "Transferência", "E-commerce", "Joalheria",
]

CIDADES_BRASIL = [
    "Porto Alegre", "Canoas", "Gravataí", "Novo Hamburgo",
    "São Paulo", "Curitiba", "Florianópolis", "Caxias do Sul",
    "Santa Maria", "Pelotas", "Passo Fundo", "Lajeado",
]

ESTABELECIMENTOS = {
    "Supermercado": ["Zaffari", "Big", "Nacional", "Carrefour", "Mercado Gaúcho"],
    "Farmácia": ["Panvel", "RaiaDrogasil", "Farmácia Popular", "São João"],
    "Posto de Combustível": ["Ipiranga", "Shell", "Petrobras", "Texaco"],
    "Restaurante": ["Churrascaria Sul", "Cantina Italiana", "Saborosa", "Bar do Zé"],
    "Eletrônicos": ["Fast Shop", "Magazine Luiza", "Americanas", "TechStore"],
    "Vestuário": ["Renner", "Riachuelo", "C&A", "Zara"],
    "Viagem": ["Latam", "Gol", "CVC Viagens", "Decolar"],
    "Educação": ["Universidade XYZ", "Curso Online ABC", "Colégio Modelo"],
    "Saúde": ["Clínica Bem-Estar", "Hospital Modelo", "Laboratório Vida"],
    "Entretenimento": ["Cinema Sul", "Shows & Eventos", "Parque Aquático"],
    "Transferência": ["Transferência TEF", "PIX Automático"],
    "E-commerce": ["Mercado Livre", "Amazon BR", "Shopee", "AliExpress"],
    "Joalheria": ["Joalheria Ouro Velho", "H.Stern", "Vivara"],
}

NOMES_FICTÍCIOS = [
    "Ana Souza", "Carlos Pereira", "Juliana Lima", "Rafael Oliveira",
    "Fernanda Santos", "Marcelo Costa", "Patrícia Rocha", "Diego Mendes",
    "Isabela Martins", "Rodrigo Alves",
]


def _rand() -> random.Random:
    r = random.Random(RANDOM_SEED)
    return r


def gerar_perfil(associado_id: str | None = None, rng: random.Random | None = None) -> PerfilAssociado:
    """Gera um perfil fictício de associado."""
    if rng is None:
        rng = random.Random()
    if associado_id is None:
        associado_id = str(uuid.uuid4())[:8]

    nome = rng.choice(NOMES_FICTÍCIOS)
    valor_medio = rng.uniform(80, 400)
    desvio = rng.uniform(30, 120)
    n_categorias = rng.randint(3, 5)
    n_cidades = rng.randint(1, 3)

    return PerfilAssociado(
        associado_id=associado_id,
        nome=nome,
        valor_medio_transacao=round(valor_medio, 2),
        desvio_padrao_valor=round(desvio, 2),
        categorias_frequentes=rng.sample(CATEGORIAS[:8], n_categorias),
        cidades_frequentes=rng.sample(CIDADES_BRASIL[:6], n_cidades),
        limite_diario=round(rng.uniform(2000, 10000), 2),
        transacoes_por_hora_normal=round(rng.uniform(0.1, 0.5), 2),
        horario_habitual_inicio=rng.randint(7, 9),
        horario_habitual_fim=rng.randint(20, 23),
    )


def gerar_transacao_normal(
    associado_id: str,
    perfil: PerfilAssociado,
    base_time: datetime | None = None,
    rng: random.Random | None = None,
) -> Transacao:
    """Gera uma transação dentro do padrão habitual do associado."""
    if rng is None:
        rng = random.Random()
    if base_time is None:
        base_time = datetime.now() - timedelta(days=rng.randint(1, 30))

    categoria = rng.choice(perfil.categorias_frequentes)
    cidade = rng.choice(perfil.cidades_frequentes)
    valor = max(5.0, rng.gauss(perfil.valor_medio_transacao, perfil.desvio_padrao_valor / 2))
    hora = rng.randint(perfil.horario_habitual_inicio, perfil.horario_habitual_fim)

    dt = base_time.replace(
        hour=hora,
        minute=rng.randint(0, 59),
        second=rng.randint(0, 59),
        microsecond=0,
    )

    estabelecimentos = ESTABELECIMENTOS.get(categoria, ["Loja Genérica"])
    return Transacao(
        id=str(uuid.uuid4())[:12],
        associado_id=associado_id,
        valor=round(valor, 2),
        data_hora=dt,
        categoria=categoria,
        estabelecimento=rng.choice(estabelecimentos),
        cidade=cidade,
        estado="RS",
        pais="Brasil",
        distancia_residencia_km=round(rng.uniform(0, 30), 1),
        canal=rng.choice(["Presencial", "Presencial", "App"]),
    )


def gerar_transacao_suspeita(
    associado_id: str,
    perfil: PerfilAssociado,
    tipo_suspeita: str = "valor_alto",
    rng: random.Random | None = None,
) -> Transacao:
    """
    Gera transações com padrões suspeitos específicos.

    Tipos disponíveis:
    - valor_alto: valor muito acima da média
    - localizacao_incomum: cidade fora do histórico + distância grande
    - horario_incomum: madrugada
    - categoria_incomum: categoria rara para o perfil
    - pais_estrangeiro: transação fora do Brasil
    - multiplos_sinais: combinação de fatores suspeitos
    """
    if rng is None:
        rng = random.Random()

    base = gerar_transacao_normal(associado_id, perfil, rng=rng)

    if tipo_suspeita == "valor_alto":
        base.valor = round(perfil.valor_medio_transacao + perfil.desvio_padrao_valor * rng.uniform(3, 6), 2)
        base.categoria = "Joalheria"
        base.estabelecimento = rng.choice(ESTABELECIMENTOS["Joalheria"])

    elif tipo_suspeita == "localizacao_incomum":
        cidades_fora = [c for c in CIDADES_BRASIL if c not in perfil.cidades_frequentes]
        base.cidade = rng.choice(cidades_fora) if cidades_fora else "São Paulo"
        base.estado = "SP"
        base.distancia_residencia_km = round(rng.uniform(300, 1500), 1)

    elif tipo_suspeita == "horario_incomum":
        base.data_hora = base.data_hora.replace(hour=rng.randint(1, 4))

    elif tipo_suspeita == "categoria_incomum":
        cats_incomuns = [c for c in CATEGORIAS if c not in perfil.categorias_frequentes]
        base.categoria = rng.choice(cats_incomuns) if cats_incomuns else "Joalheria"
        base.estabelecimento = rng.choice(ESTABELECIMENTOS.get(base.categoria, ["Loja Incomum"]))

    elif tipo_suspeita == "pais_estrangeiro":
        base.pais = rng.choice(["Argentina", "Paraguai", "Estados Unidos", "Portugal"])
        base.cidade = rng.choice(["Buenos Aires", "Assunção", "Miami", "Lisboa"])
        base.distancia_residencia_km = round(rng.uniform(1000, 10000), 1)

    elif tipo_suspeita == "multiplos_sinais":
        # Combina vários fatores de risco
        base.valor = round(perfil.valor_medio_transacao + perfil.desvio_padrao_valor * 5, 2)
        base.categoria = "Joalheria"
        base.estabelecimento = "Joalheria Luxo Internacional"
        cidades_fora = [c for c in CIDADES_BRASIL if c not in perfil.cidades_frequentes]
        base.cidade = rng.choice(cidades_fora) if cidades_fora else "São Paulo"
        base.estado = "SP"
        base.distancia_residencia_km = 900.0
        base.data_hora = base.data_hora.replace(hour=3)
        base.canal = "Online"
        base.pais = "Brasil"

    return base


def gerar_dataset_demo(n_normais: int = 40, n_suspeitas: int = 10) -> Tuple[
    List[PerfilAssociado], List[Transacao]
]:
    """
    Gera um dataset completo de demonstração com associados e transações.
    Retorna (perfis, transacoes).
    """
    rng = _rand()
    ids_associados = [f"ASS{i:03d}" for i in range(1, 6)]
    perfis = {aid: gerar_perfil(aid, rng) for aid in ids_associados}

    transacoes: List[Transacao] = []
    base_time = datetime.now() - timedelta(days=30)

    # Transações normais distribuídas entre os associados
    for i in range(n_normais):
        aid = rng.choice(ids_associados)
        dt = base_time + timedelta(hours=rng.uniform(0, 720))
        tx = gerar_transacao_normal(aid, perfis[aid], dt, rng)
        transacoes.append(tx)

    # Transações suspeitas
    tipos = [
        "valor_alto", "localizacao_incomum", "horario_incomum",
        "categoria_incomum", "pais_estrangeiro", "multiplos_sinais",
    ]
    for i in range(n_suspeitas):
        aid = rng.choice(ids_associados)
        tipo = tipos[i % len(tipos)]
        dt = base_time + timedelta(hours=rng.uniform(0, 720))
        tx = gerar_transacao_suspeita(aid, perfis[aid], tipo, rng)
        tx.data_hora = dt.replace(
            hour=tx.data_hora.hour,
            minute=tx.data_hora.minute,
        )
        transacoes.append(tx)

    # Ordena por data_hora
    transacoes.sort(key=lambda t: t.data_hora)
    return list(perfis.values()), transacoes


def transacoes_para_dataframe(transacoes: List[Transacao]) -> pd.DataFrame:
    """Converte lista de Transacao para DataFrame do pandas."""
    return pd.DataFrame([
        {
            "id": t.id,
            "associado_id": t.associado_id,
            "valor": t.valor,
            "data_hora": t.data_hora,
            "categoria": t.categoria,
            "estabelecimento": t.estabelecimento,
            "cidade": t.cidade,
            "estado": t.estado,
            "pais": t.pais,
            "distancia_km": t.distancia_residencia_km,
            "canal": t.canal,
        }
        for t in transacoes
    ])
