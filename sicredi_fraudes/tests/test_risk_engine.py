"""
test_risk_engine.py — Testes automatizados do motor de avaliação de risco.

Cobre os 6 cenários obrigatórios:
  1. Compra habitual de baixo valor
  2. Compra de valor elevado e fora do padrão
  3. Várias compras em sequência (alta frequência)
  4. Compra em localização incomum
  5. Transação com informações incompletas (valores mínimos)
  6. Transação com múltiplos sinais suspeitos

Além dos cenários individuais de cada regra.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime, timedelta

import pytest

from src.core.models import Transacao
from src.core.risk_engine import (
    avaliar_transacao,
    regra_canal_suspeito,
    regra_categoria_incomum,
    regra_horario_incomum,
    regra_localizacao_incomum,
    regra_pais_estrangeiro,
    regra_valor_alto,
    regra_velocidade_transacoes,
    regra_viagem_impossivel,
)
from src.data.generator import (
    gerar_dataset_demo,
    gerar_transacao_suspeita,
    transacoes_para_dataframe,
)

HORA_BASE = datetime(2025, 6, 15, 14, 30, 0)

# ===========================================================================
# Cenário 1 — Compra habitual de baixo valor
# ===========================================================================
class TestCompraHabitual:
    def test_pontuacao_baixa(self, tx_normal, perfil_padrao):
        resultado = avaliar_transacao(tx_normal, perfil_padrao)
        assert resultado.pontuacao < 40, (
            f"Compra habitual deve ter pontuação < 40, obteve {resultado.pontuacao}"
        )

    def test_nivel_baixo(self, tx_normal, perfil_padrao):
        resultado = avaliar_transacao(tx_normal, perfil_padrao)
        assert resultado.nivel_risco == "baixo"

    def test_nao_confirma_fraude(self, tx_normal, perfil_padrao):
        resultado = avaliar_transacao(tx_normal, perfil_padrao)
        assert resultado.eh_fraude_confirmada is False

    def test_recomendacao_gerada(self, tx_normal, perfil_padrao):
        resultado = avaliar_transacao(tx_normal, perfil_padrao)
        assert len(resultado.recomendacao) > 10


# ===========================================================================
# Cenário 2 — Compra de valor elevado e fora do padrão
# ===========================================================================
class TestValorElevado:
    def _tx_alto_valor(self):
        return Transacao(
            id="TX_ALTO",
            associado_id="TST001",
            valor=2000.0,   # muito acima da média de R$200 ± R$50
            data_hora=HORA_BASE,
            categoria="Supermercado",
            estabelecimento="Zaffari",
            cidade="Porto Alegre",
            estado="RS",
            pais="Brasil",
            distancia_residencia_km=5.0,
            canal="Presencial",
        )

    def test_fator_valor_alto_presente(self, perfil_padrao):
        tx = self._tx_alto_valor()
        fator = regra_valor_alto(tx, perfil_padrao)
        assert fator is not None
        assert fator.pontos > 0

    def test_pontuacao_elevada(self, perfil_padrao):
        tx = self._tx_alto_valor()
        resultado = avaliar_transacao(tx, perfil_padrao)
        assert resultado.pontuacao >= 20, (
            f"Valor muito acima do padrão deve gerar pontuação >= 20, obteve {resultado.pontuacao}"
        )

    def test_fator_ausente_para_valor_normal(self, tx_normal, perfil_padrao):
        fator = regra_valor_alto(tx_normal, perfil_padrao)
        assert fator is None


# ===========================================================================
# Cenário 3 — Várias compras em sequência (alta frequência)
# ===========================================================================
class TestAltaFrequencia:
    def _gerar_historico_rapido(self, associado_id="TST001", n=5):
        now = HORA_BASE
        return [
            Transacao(
                id=f"TX_SEQ_{i}",
                associado_id=associado_id,
                valor=50.0,
                data_hora=now - timedelta(minutes=i * 3),
                categoria="Supermercado",
                estabelecimento="Loja",
                cidade="Porto Alegre",
                estado="RS",
                pais="Brasil",
                distancia_residencia_km=5.0,
                canal="Presencial",
            )
            for i in range(1, n + 1)
        ]

    def test_fator_velocidade_detectado(self, tx_normal, perfil_padrao):
        historico = self._gerar_historico_rapido()
        fator = regra_velocidade_transacoes(tx_normal, historico)
        assert fator is not None, "Alta frequência deve ser detectada"
        assert fator.pontos > 0

    def test_pontuacao_aumenta_com_historico(self, tx_normal, perfil_padrao):
        historico = self._gerar_historico_rapido(n=6)
        resultado = avaliar_transacao(tx_normal, perfil_padrao, historico)
        resultado_sem = avaliar_transacao(tx_normal, perfil_padrao, [])
        assert resultado.pontuacao > resultado_sem.pontuacao

    def test_sem_historico_nao_penaliza(self, tx_normal, perfil_padrao):
        fator = regra_velocidade_transacoes(tx_normal, [])
        assert fator is None

    def test_historico_pequeno_nao_penaliza(self, tx_normal, perfil_padrao):
        historico = self._gerar_historico_rapido(n=2)
        fator = regra_velocidade_transacoes(tx_normal, historico)
        assert fator is None


# ===========================================================================
# Cenário 4 — Compra em localização incomum
# ===========================================================================
class TestLocalizacaoIncomum:
    def _tx_local_incomum(self):
        return Transacao(
            id="TX_LOCAL",
            associado_id="TST001",
            valor=150.0,
            data_hora=HORA_BASE,
            categoria="Supermercado",
            estabelecimento="Carrefour SP",
            cidade="São Paulo",   # fora das cidades habituais (RS)
            estado="SP",
            pais="Brasil",
            distancia_residencia_km=1100.0,
            canal="Presencial",
        )

    def test_fator_localizacao_detectado(self, perfil_padrao):
        tx = self._tx_local_incomum()
        fator = regra_localizacao_incomum(tx, perfil_padrao)
        assert fator is not None

    def test_pontuacao_mais_alta_que_normal(self, tx_normal, perfil_padrao):
        tx_incomum = self._tx_local_incomum()
        r_incomum = avaliar_transacao(tx_incomum, perfil_padrao)
        r_normal = avaliar_transacao(tx_normal, perfil_padrao)
        assert r_incomum.pontuacao > r_normal.pontuacao

    def test_cidade_habitual_sem_penalizacao(self, tx_normal, perfil_padrao):
        fator = regra_localizacao_incomum(tx_normal, perfil_padrao)
        assert fator is None


# ===========================================================================
# Cenário 5 — Transação com informações mínimas/incompletas
# ===========================================================================
class TestInformacoesMinimas:
    def test_transacao_sem_historico_funciona(self, perfil_padrao):
        """Sistema deve funcionar mesmo sem histórico disponível."""
        tx = Transacao(
            id="TX_MIN",
            associado_id="TST001",
            valor=50.0,
            data_hora=HORA_BASE,
            categoria="Farmácia",
            estabelecimento="Farmácia X",
            cidade="Porto Alegre",
            estado="RS",
            pais="Brasil",
            distancia_residencia_km=0.0,
            canal="Presencial",
        )
        resultado = avaliar_transacao(tx, perfil_padrao, historico_recente=None)
        assert resultado is not None
        assert 0 <= resultado.pontuacao <= 100
        assert resultado.nivel_risco in ("baixo", "medio", "alto")
        assert len(resultado.recomendacao) > 5

    def test_desvio_zero_nao_quebra(self, perfil_padrao):
        """Motor não deve falhar quando desvio padrão é zero."""
        perfil_padrao.desvio_padrao_valor = 0
        tx = Transacao(
            id="TX_DPZ",
            associado_id="TST001",
            valor=200.0,
            data_hora=HORA_BASE,
            categoria="Supermercado",
            estabelecimento="Loja",
            cidade="Porto Alegre",
            estado="RS",
            pais="Brasil",
            distancia_residencia_km=5.0,
            canal="Presencial",
        )
        resultado = avaliar_transacao(tx, perfil_padrao)
        assert resultado is not None


# ===========================================================================
# Cenário 6 — Múltiplos sinais suspeitos simultâneos
# ===========================================================================
class TestMultiplosSinais:
    def _tx_multiplos(self):
        return Transacao(
            id="TX_MULTI",
            associado_id="TST001",
            valor=4500.0,           # valor muito alto
            data_hora=HORA_BASE.replace(hour=3),  # madrugada
            categoria="Joalheria",  # categoria incomum
            estabelecimento="Joalheria Luxo Internacional",
            cidade="Buenos Aires",  # cidade incomum
            estado="--",
            pais="Argentina",       # país estrangeiro
            distancia_residencia_km=2500.0,
            canal="Online",         # canal suspeito + valor alto
        )

    def test_nivel_alto(self, perfil_padrao):
        tx = self._tx_multiplos()
        resultado = avaliar_transacao(tx, perfil_padrao)
        assert resultado.nivel_risco == "alto", (
            f"Múltiplos sinais devem resultar em risco alto, obteve {resultado.nivel_risco} ({resultado.pontuacao})"
        )

    def test_varios_fatores(self, perfil_padrao):
        tx = self._tx_multiplos()
        resultado = avaliar_transacao(tx, perfil_padrao)
        assert len(resultado.fatores) >= 3, (
            f"Deveria ter ao menos 3 fatores, obteve {len(resultado.fatores)}: "
            f"{[f.nome for f in resultado.fatores]}"
        )

    def test_pontuacao_maxima(self, perfil_padrao):
        tx = self._tx_multiplos()
        resultado = avaliar_transacao(tx, perfil_padrao)
        assert resultado.pontuacao >= 70

    def test_fraude_nunca_confirmada(self, perfil_padrao):
        """Mesmo com pontuação máxima, fraude nunca é confirmada automaticamente."""
        tx = self._tx_multiplos()
        resultado = avaliar_transacao(tx, perfil_padrao)
        assert resultado.eh_fraude_confirmada is False

    def test_pontuacao_limitada_a_100(self, perfil_padrao):
        tx = self._tx_multiplos()
        resultado = avaliar_transacao(tx, perfil_padrao)
        assert resultado.pontuacao <= 100


# ===========================================================================
# Testes adicionais de regras individuais
# ===========================================================================
class TestRegrasIndividuais:
    def test_pais_estrangeiro(self, perfil_padrao):
        tx = Transacao(
            id="TX_EXT",
            associado_id="TST001",
            valor=100.0,
            data_hora=HORA_BASE,
            categoria="Supermercado",
            estabelecimento="Supermercado Exterior",
            cidade="Miami",
            estado="FL",
            pais="Estados Unidos",
            distancia_residencia_km=8000.0,
            canal="Presencial",
        )
        fator = regra_pais_estrangeiro(tx, perfil_padrao)
        assert fator is not None
        assert fator.pontos > 0

    def test_brasil_sem_penalizacao_pais(self, tx_normal, perfil_padrao):
        fator = regra_pais_estrangeiro(tx_normal, perfil_padrao)
        assert fator is None

    def test_horario_incomum_madrugada(self, perfil_padrao):
        tx = Transacao(
            id="TX_MAD",
            associado_id="TST001",
            valor=100.0,
            data_hora=HORA_BASE.replace(hour=3),
            categoria="Supermercado",
            estabelecimento="Loja 24h",
            cidade="Porto Alegre",
            estado="RS",
            pais="Brasil",
            distancia_residencia_km=5.0,
            canal="Presencial",
        )
        fator = regra_horario_incomum(tx, perfil_padrao)
        assert fator is not None

    def test_categoria_incomum(self, perfil_padrao):
        tx = Transacao(
            id="TX_CAT",
            associado_id="TST001",
            valor=100.0,
            data_hora=HORA_BASE,
            categoria="Joalheria",
            estabelecimento="Joalheria X",
            cidade="Porto Alegre",
            estado="RS",
            pais="Brasil",
            distancia_residencia_km=5.0,
            canal="Presencial",
        )
        fator = regra_categoria_incomum(tx, perfil_padrao)
        assert fator is not None

    def test_categoria_habitual_sem_penalizacao(self, tx_normal, perfil_padrao):
        fator = regra_categoria_incomum(tx_normal, perfil_padrao)
        assert fator is None


# ===========================================================================
# Testes de estrutura do resultado
# ===========================================================================
class TestEstruturaResultado:
    def test_campos_obrigatorios(self, tx_normal, perfil_padrao):
        r = avaliar_transacao(tx_normal, perfil_padrao)
        assert r.transacao_id == tx_normal.id
        assert r.associado_id == tx_normal.associado_id
        assert r.nivel_risco in ("baixo", "medio", "alto")
        assert 0 <= r.pontuacao <= 100
        assert isinstance(r.fatores, list)
        assert len(r.recomendacao) > 0
        assert len(r.justificativa) > 0
        assert r.fonte_analise == "motor_local"

    def test_dataset_demo_gera_resultados(self, dataset_demo):
        perfis_lista, transacoes = dataset_demo
        perfis = {p.associado_id: p for p in perfis_lista}
        assert len(transacoes) > 0
        for tx in transacoes[:5]:
            perfil = perfis.get(tx.associado_id)
            assert perfil is not None
            resultado = avaliar_transacao(tx, perfil)
            assert resultado is not None
            assert 0 <= resultado.pontuacao <= 100


# ===========================================================================
# Tarefa 3 — Regra de viagem impossível
# ===========================================================================
class TestViagemImpossivel:
    def _tx_base(self, tx_id: str, dist_km: float, minutos_atras: int = 30):
        """Cria uma transação-fantasma para o histórico."""
        return Transacao(
            id=tx_id,
            associado_id="TST001",
            valor=100.0,
            data_hora=HORA_BASE - timedelta(minutes=minutos_atras),
            categoria="Supermercado",
            estabelecimento="Loja Origem",
            cidade="Porto Alegre",
            estado="RS",
            pais="Brasil",
            distancia_residencia_km=dist_km,
            canal="Presencial",
        )

    def test_viagem_impossivel_detectada(self, perfil_padrao):
        """Transação a 5 km, 30 min após uma a 2000 km — impossível."""
        tx_atual = Transacao(
            id="TX_ATUAL",
            associado_id="TST001",
            valor=200.0,
            data_hora=HORA_BASE,
            categoria="Eletrônicos",
            estabelecimento="Loja Remota",
            cidade="São Paulo",
            estado="SP",
            pais="Brasil",
            distancia_residencia_km=2000.0,
            canal="Presencial",
        )
        historico = [self._tx_base("TX_ANT", dist_km=5.0, minutos_atras=30)]
        fator = regra_viagem_impossivel(tx_atual, historico)
        assert fator is not None, "Viagem impossível deveria ser detectada"
        assert fator.pontos > 0
        assert "impossível" in fator.descricao.lower() or "impossivel" in fator.descricao.lower()

    def test_viagem_possivel_nao_detectada(self, perfil_padrao):
        """Transação 5 km antes e 5 km agora — sem suspeita."""
        tx_atual = Transacao(
            id="TX_PERTO",
            associado_id="TST001",
            valor=100.0,
            data_hora=HORA_BASE,
            categoria="Supermercado",
            estabelecimento="Loja Perto",
            cidade="Canoas",
            estado="RS",
            pais="Brasil",
            distancia_residencia_km=10.0,
            canal="Presencial",
        )
        historico = [self._tx_base("TX_ANT_PERTO", dist_km=8.0, minutos_atras=30)]
        fator = regra_viagem_impossivel(tx_atual, historico)
        assert fator is None, "Viagem curta não deve gerar alerta"

    def test_sem_historico_sem_alerta(self):
        """Sem histórico, a regra não deve disparar."""
        tx_atual = Transacao(
            id="TX_SEM_HIST",
            associado_id="TST001",
            valor=100.0,
            data_hora=HORA_BASE,
            categoria="Supermercado",
            estabelecimento="Loja",
            cidade="Porto Alegre",
            estado="RS",
            pais="Brasil",
            distancia_residencia_km=2000.0,
            canal="Presencial",
        )
        fator = regra_viagem_impossivel(tx_atual, [])
        assert fator is None

    def test_historico_diferente_associado_ignorado(self):
        """Transações de outro associado não devem interferir."""
        tx_atual = Transacao(
            id="TX_MINE",
            associado_id="TST001",
            valor=100.0,
            data_hora=HORA_BASE,
            categoria="Supermercado",
            estabelecimento="Loja",
            cidade="Porto Alegre",
            estado="RS",
            pais="Brasil",
            distancia_residencia_km=2000.0,
            canal="Presencial",
        )
        tx_outro = Transacao(
            id="TX_OUTRO",
            associado_id="TST999",  # associado diferente
            valor=100.0,
            data_hora=HORA_BASE - timedelta(minutes=10),
            categoria="Supermercado",
            estabelecimento="Loja Outro",
            cidade="Porto Alegre",
            estado="RS",
            pais="Brasil",
            distancia_residencia_km=5.0,
            canal="Presencial",
        )
        fator = regra_viagem_impossivel(tx_atual, [tx_outro])
        assert fator is None

    def test_viagem_impossivel_contribui_para_pontuacao(self, perfil_padrao):
        """A regra deve aumentar a pontuação total ao ser incluída no histórico."""
        tx_atual = Transacao(
            id="TX_VIAGEM",
            associado_id="TST001",
            valor=180.0,
            data_hora=HORA_BASE,
            categoria="Supermercado",
            estabelecimento="Zaffari Remoto",
            cidade="Porto Alegre",
            estado="RS",
            pais="Brasil",
            distancia_residencia_km=2000.0,
            canal="Presencial",
        )
        historico_suspeito = [
            Transacao(
                id="TX_LONGE",
                associado_id="TST001",
                valor=100.0,
                data_hora=HORA_BASE - timedelta(minutes=20),
                categoria="Supermercado",
                estabelecimento="Loja Distante",
                cidade="Miami",
                estado="FL",
                pais="Estados Unidos",
                distancia_residencia_km=5.0,
                canal="Presencial",
            )
        ]
        r_com = avaliar_transacao(tx_atual, perfil_padrao, historico_suspeito)
        r_sem = avaliar_transacao(tx_atual, perfil_padrao, [])
        assert r_com.pontuacao > r_sem.pontuacao


# ===========================================================================
# Tarefa 4 — Cobertura expandida: generator e regras adicionais
# ===========================================================================
class TestGeneratorCobertura:
    """Testes de cobertura para src/data/generator.py."""

    def test_gerar_transacao_suspeita_valor_alto(self, perfil_padrao):
        import random
        rng = random.Random(1)
        tx = gerar_transacao_suspeita("TST001", perfil_padrao, "valor_alto", rng)
        assert tx.valor > perfil_padrao.valor_medio_transacao + perfil_padrao.desvio_padrao_valor * 2

    def test_gerar_transacao_suspeita_localizacao_incomum(self, perfil_padrao):
        import random
        rng = random.Random(2)
        tx = gerar_transacao_suspeita("TST001", perfil_padrao, "localizacao_incomum", rng)
        assert tx.cidade.lower() not in [c.lower() for c in perfil_padrao.cidades_frequentes]
        assert tx.distancia_residencia_km >= 300

    def test_gerar_transacao_suspeita_horario_incomum(self, perfil_padrao):
        import random
        rng = random.Random(3)
        tx = gerar_transacao_suspeita("TST001", perfil_padrao, "horario_incomum", rng)
        assert 1 <= tx.data_hora.hour <= 4

    def test_gerar_transacao_suspeita_categoria_incomum(self, perfil_padrao):
        import random
        rng = random.Random(4)
        tx = gerar_transacao_suspeita("TST001", perfil_padrao, "categoria_incomum", rng)
        assert tx.categoria.lower() not in [c.lower() for c in perfil_padrao.categorias_frequentes]

    def test_gerar_transacao_suspeita_pais_estrangeiro(self, perfil_padrao):
        import random
        rng = random.Random(5)
        tx = gerar_transacao_suspeita("TST001", perfil_padrao, "pais_estrangeiro", rng)
        assert tx.pais.lower() not in ("brasil", "brazil")

    def test_gerar_transacao_suspeita_multiplos_sinais(self, perfil_padrao):
        import random
        rng = random.Random(6)
        tx = gerar_transacao_suspeita("TST001", perfil_padrao, "multiplos_sinais", rng)
        resultado = avaliar_transacao(tx, perfil_padrao)
        assert len(resultado.fatores) >= 2

    def test_transacoes_para_dataframe_lista_vazia(self):
        df = transacoes_para_dataframe([])
        assert len(df) == 0
        assert list(df.columns) == []  # DataFrame vazio sem colunas definidas

    def test_gerar_dataset_demo_retorna_transacoes(self):
        perfis, txs = gerar_dataset_demo(n_normais=5, n_suspeitas=2)
        assert len(txs) > 0
        assert len(perfis) > 0

    def test_gerar_dataset_demo_ordenado_por_data(self):
        _, txs = gerar_dataset_demo(n_normais=10, n_suspeitas=3)
        datas = [t.data_hora for t in txs]
        assert datas == sorted(datas)


class TestRegrasAdicionais:
    """Testes adicionais para regras não cobertas anteriormente."""

    def test_canal_suspeito_detectado(self, perfil_padrao):
        tx = Transacao(
            id="TX_ONLINE_ALTO",
            associado_id="TST001",
            valor=1500.0,
            data_hora=HORA_BASE,
            categoria="Eletrônicos",
            estabelecimento="Fast Shop Online",
            cidade="Porto Alegre",
            estado="RS",
            pais="Brasil",
            distancia_residencia_km=0.0,
            canal="Online",
        )
        fator = regra_canal_suspeito(tx)
        assert fator is not None
        assert fator.pontos > 0

    def test_canal_suspeito_valor_baixo_nao_penaliza(self, perfil_padrao):
        tx = Transacao(
            id="TX_ONLINE_BAIXO",
            associado_id="TST001",
            valor=100.0,
            data_hora=HORA_BASE,
            categoria="Supermercado",
            estabelecimento="iFood",
            cidade="Porto Alegre",
            estado="RS",
            pais="Brasil",
            distancia_residencia_km=0.0,
            canal="Online",
        )
        fator = regra_canal_suspeito(tx)
        assert fator is None

    def test_pais_brazil_ingles_sem_penalizacao(self, perfil_padrao):
        """'Brazil' (em inglês) também deve ser aceito como país doméstico."""
        tx = Transacao(
            id="TX_BRAZIL",
            associado_id="TST001",
            valor=100.0,
            data_hora=HORA_BASE,
            categoria="Supermercado",
            estabelecimento="Loja",
            cidade="Porto Alegre",
            estado="RS",
            pais="Brazil",
            distancia_residencia_km=5.0,
            canal="Presencial",
        )
        fator = regra_pais_estrangeiro(tx, perfil_padrao)
        assert fator is None
