"""
app.py — Interface principal da aplicação Streamlit.
Prevenção Inteligente a Fraudes — Proposta para o Sicredi (dados fictícios).
"""
from __future__ import annotations

import sys
import os

# Garante que o diretório raiz do projeto está no path
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import uuid
from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.core.models import Transacao
from src.core.risk_engine import avaliar_transacao
from src.core.watsonx_client import status_integracao
from src.data.generator import (
    CATEGORIAS,
    CIDADES_BRASIL,
    gerar_dataset_demo,
    gerar_perfil,
    transacoes_para_dataframe,
)

# ---------------------------------------------------------------------------
# Configuração da página
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Prevenção a Fraudes — Sicredi",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# CSS personalizado — identidade visual de painel de segurança
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Fundo e tipografia geral */
    .main { background-color: #f0f4f8; }
    h1, h2, h3 { color: #1a3a5c; font-family: 'Segoe UI', sans-serif; }

    /* Cartões de métrica */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #d0dce8;
        border-radius: 10px;
        padding: 12px 18px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }

    /* Botão primário */
    .stButton > button {
        background-color: #1a6b3c;
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: 600;
        padding: 0.45em 1.2em;
    }
    .stButton > button:hover { background-color: #145530; }

    /* Barra lateral */
    section[data-testid="stSidebar"] { background-color: #1a3a5c; }
    section[data-testid="stSidebar"] * { color: #e8eef5 !important; }
    section[data-testid="stSidebar"] .stSelectbox label { color: #b0c4d8 !important; }

    /* Tabelas */
    .stDataFrame { border-radius: 8px; overflow: hidden; }

    /* Badges de risco */
    .badge-alto   { background:#dc2626; color:white; padding:3px 10px; border-radius:12px; font-weight:700; font-size:0.85em; }
    .badge-medio  { background:#d97706; color:white; padding:3px 10px; border-radius:12px; font-weight:700; font-size:0.85em; }
    .badge-baixo  { background:#16a34a; color:white; padding:3px 10px; border-radius:12px; font-weight:700; font-size:0.85em; }

    /* Aviso de dados fictícios */
    .aviso-ficticio {
        background:#fffbeb; border:1px solid #fbbf24; border-radius:8px;
        padding:8px 14px; font-size:0.82em; color:#92400e; margin-bottom:8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Estado da sessão
# ---------------------------------------------------------------------------
def _init_session():
    if "perfis" not in st.session_state or "transacoes" not in st.session_state:
        perfis, transacoes = gerar_dataset_demo(n_normais=40, n_suspeitas=10)
        st.session_state["perfis"] = {p.associado_id: p for p in perfis}
        st.session_state["transacoes"] = transacoes

    if "historico_analises" not in st.session_state:
        st.session_state["historico_analises"] = []

    if "resultados_cache" not in st.session_state:
        # Pré-analisa todas as transações do dataset
        resultados = {}
        perfis = st.session_state["perfis"]
        txs = st.session_state["transacoes"]
        for tx in txs:
            perfil = perfis.get(tx.associado_id)
            if perfil:
                historico = [t for t in txs if t.associado_id == tx.associado_id and t.id != tx.id]
                resultado = avaliar_transacao(tx, perfil, historico)
                resultados[tx.id] = resultado
        st.session_state["resultados_cache"] = resultados


_init_session()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
CORES_RISCO = {"baixo": "#16a34a", "medio": "#d97706", "alto": "#dc2626"}
ICONES_RISCO = {"baixo": "🟢", "medio": "🟡", "alto": "🔴"}


def _badge(nivel: str) -> str:
    return f'<span class="badge-{nivel}">{nivel.upper()}</span>'


def _cor_nivel(nivel: str) -> str:
    return CORES_RISCO.get(nivel, "#6b7280")


# ---------------------------------------------------------------------------
# Barra lateral — navegação
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🛡️ Prevenção a Fraudes")
    st.markdown("**Proposta para o Sicredi**")
    st.markdown("---")
    pagina = st.radio(
        "Navegação",
        ["📊 Painel", "🔍 Detalhe da Transação", "🧪 Simulador", "📋 Histórico", "ℹ️ Sobre"],
        label_visibility="collapsed",
    )
    st.markdown("---")

    # Status watsonx — indicador aprimorado
    status = status_integracao()
    if status["habilitado"]:
        st.markdown(
            f'<div style="background:#0f4c25;border:1px solid #16a34a;border-radius:8px;padding:8px 12px;margin-bottom:4px;">'
            f'<span style="font-size:1.1em;">✅</span> <strong>watsonx ativo</strong><br>'
            f'<span style="font-size:0.78em;color:#86efac;">Modelo: {status.get("modelo", "granite")}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div style="background:#4a1a0a;border:1px solid #d97706;border-radius:8px;padding:8px 12px;margin-bottom:4px;">'
            '<span style="font-size:1.1em;">⚙️</span> <strong>watsonx não configurado</strong><br>'
            '<span style="font-size:0.78em;color:#fcd34d;">Configure o .env com WATSONX_API_KEY e WATSONX_PROJECT_ID para ativar</span>'
            '</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div style="font-size:0.75em;margin-top:12px;color:#8facc8;">'
        "Todos os dados são fictícios e sintéticos.<br>"
        "Nenhuma informação real de clientes é utilizada.</div>",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# PÁGINA 1 — Painel de Monitoramento
# ---------------------------------------------------------------------------
if pagina == "📊 Painel":
    st.title("📊 Painel de Monitoramento de Fraudes")
    st.markdown(
        '<div class="aviso-ficticio">⚠️ <strong>Dados fictícios e sintéticos</strong> — '
        "Este protótipo utiliza exclusivamente dados gerados artificialmente para fins de demonstração.</div>",
        unsafe_allow_html=True,
    )

    resultados = st.session_state["resultados_cache"]
    transacoes = st.session_state["transacoes"]

    # --- KPIs principais ---
    total = len(resultados)
    por_nivel = {"baixo": 0, "medio": 0, "alto": 0}
    for r in resultados.values():
        por_nivel[r.nivel_risco] = por_nivel.get(r.nivel_risco, 0) + 1

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total analisadas", total)
    c2.metric("🟢 Baixo risco", por_nivel["baixo"])
    c3.metric("🟡 Risco médio", por_nivel["medio"])
    c4.metric("🔴 Alto risco", por_nivel["alto"])

    st.markdown("---")

    col_esq, col_dir = st.columns([1, 1])

    # --- Gráfico de distribuição de risco ---
    with col_esq:
        st.subheader("Distribuição por Nível de Risco")
        df_pizza = pd.DataFrame({
            "Nível": ["Baixo", "Médio", "Alto"],
            "Quantidade": [por_nivel["baixo"], por_nivel["medio"], por_nivel["alto"]],
        })
        fig_pizza = px.pie(
            df_pizza, values="Quantidade", names="Nível",
            color="Nível",
            color_discrete_map={"Baixo": "#16a34a", "Médio": "#d97706", "Alto": "#dc2626"},
            hole=0.4,
        )
        fig_pizza.update_layout(margin=dict(t=20, b=20, l=0, r=0), height=300)
        st.plotly_chart(fig_pizza, width="stretch")

    # --- Gráfico de pontuações ---
    with col_dir:
        st.subheader("Distribuição das Pontuações de Risco")
        pontuacoes = [r.pontuacao for r in resultados.values()]
        fig_hist = px.histogram(
            x=pontuacoes, nbins=20,
            labels={"x": "Pontuação (0-100)", "y": "Quantidade"},
            color_discrete_sequence=["#1a6b3c"],
        )
        fig_hist.update_layout(margin=dict(t=20, b=20, l=0, r=0), height=300)
        st.plotly_chart(fig_hist, width="stretch")

    st.markdown("---")

    # --- Indicadores de risco mais frequentes ---
    st.subheader("Principais Fatores de Risco Identificados")
    contagem_fatores: dict[str, int] = {}
    for r in resultados.values():
        for f in r.fatores:
            contagem_fatores[f.nome] = contagem_fatores.get(f.nome, 0) + 1

    if contagem_fatores:
        df_fatores = (
            pd.DataFrame(list(contagem_fatores.items()), columns=["Fator", "Ocorrências"])
            .sort_values("Ocorrências", ascending=True)
        )
        fig_bar = px.bar(
            df_fatores, x="Ocorrências", y="Fator", orientation="h",
            color_discrete_sequence=["#1a3a5c"],
        )
        fig_bar.update_layout(margin=dict(t=10, b=10, l=0, r=0), height=280)
        st.plotly_chart(fig_bar, width="stretch")

    st.markdown("---")

    # --- Série temporal de transações ---
    st.subheader("Valor das Transações ao Longo do Tempo")
    df_ts = transacoes_para_dataframe(transacoes)
    # Adiciona nível de risco ao dataframe
    df_ts["nivel_risco"] = df_ts["id"].apply(
        lambda tid: resultados[tid].nivel_risco.capitalize() if tid in resultados else "baixo"
    )
    df_ts["pontuacao"] = df_ts["id"].apply(
        lambda tid: resultados[tid].pontuacao if tid in resultados else 0
    )
    fig_ts = px.scatter(
        df_ts,
        x="data_hora",
        y="valor",
        color="nivel_risco",
        color_discrete_map={"Baixo": "#16a34a", "Medio": "#d97706", "Alto": "#dc2626"},
        hover_data={"associado_id": True, "categoria": True, "pontuacao": True, "cidade": True},
        labels={"data_hora": "Data/Hora", "valor": "Valor (R$)", "nivel_risco": "Risco"},
        size="pontuacao",
        size_max=18,
    )
    # Linha de tendência do valor
    fig_ts.add_traces(
        px.line(df_ts.sort_values("data_hora"), x="data_hora", y="valor",
                color_discrete_sequence=["#94a3b8"]).data
    )
    fig_ts.update_traces(selector=dict(mode="lines"), line=dict(width=1, dash="dot"), showlegend=False)
    fig_ts.update_layout(margin=dict(t=10, b=10, l=0, r=0), height=320, legend_title_text="Nível de Risco")
    st.plotly_chart(fig_ts, width="stretch")

    st.markdown("---")

    # --- Mapa de calor: categoria × nível de risco ---
    st.subheader("Distribuição de Risco por Categoria")
    df_heat = df_ts.copy()
    heat_pivot = (
        df_heat.groupby(["categoria", "nivel_risco"])
        .size()
        .reset_index(name="qtd")
        .pivot(index="categoria", columns="nivel_risco", values="qtd")
        .fillna(0)
        .astype(int)
    )
    # Garante colunas na ordem certa
    for col in ["Baixo", "Medio", "Alto"]:
        if col not in heat_pivot.columns:
            heat_pivot[col] = 0
    heat_pivot = heat_pivot[["Baixo", "Medio", "Alto"]]
    fig_heat = px.imshow(
        heat_pivot,
        color_continuous_scale=[[0, "#f0fdf4"], [0.5, "#fef9c3"], [1, "#fef2f2"]],
        labels={"x": "Nível de Risco", "y": "Categoria", "color": "Qtd"},
        text_auto=True,
        aspect="auto",
    )
    fig_heat.update_layout(margin=dict(t=10, b=10, l=0, r=0), height=350,
                           coloraxis_showscale=False)
    st.plotly_chart(fig_heat, width="stretch")

    st.markdown("---")

    # --- Lista de transações com filtros ---
    st.subheader("Transações Recentes")

    col_f1, col_f2, col_f3 = st.columns(3)
    filtro_nivel = col_f1.multiselect(
        "Filtrar por risco",
        ["baixo", "medio", "alto"],
        default=["baixo", "medio", "alto"],
    )
    filtro_associado = col_f2.selectbox(
        "Filtrar por associado",
        ["Todos"] + list(st.session_state["perfis"].keys()),
    )
    n_exibir = col_f3.slider("Exibir últimas N transações", 5, 50, 20)

    # Monta tabela
    linhas = []
    for tx in reversed(transacoes):
        r = resultados.get(tx.id)
        if r is None:
            continue
        if r.nivel_risco not in filtro_nivel:
            continue
        if filtro_associado != "Todos" and tx.associado_id != filtro_associado:
            continue
        linhas.append({
            "ID": tx.id,
            "Associado": tx.associado_id,
            "Data/Hora": tx.data_hora.strftime("%d/%m/%Y %H:%M"),
            "Estabelecimento": tx.estabelecimento,
            "Categoria": tx.categoria,
            "Valor (R$)": f"{tx.valor:,.2f}",
            "Cidade": tx.cidade,
            "Pontuação": r.pontuacao,
            "Risco": r.nivel_risco.upper(),
        })
        if len(linhas) >= n_exibir:
            break

    if linhas:
        df_tabela = pd.DataFrame(linhas)

        def _cor_linha(val):
            mapa = {"BAIXO": "background-color:#f0fdf4", "MÉDIO": "background-color:#fffbeb", "ALTO": "background-color:#fef2f2"}
            return mapa.get(val, "")

        st.dataframe(
            df_tabela.style.map(lambda v: _cor_linha(v), subset=["Risco"]),
            width="stretch",
            hide_index=True,
        )

        # --- Exportar CSV ---
        csv_bytes = df_tabela.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Exportar tabela como CSV",
            data=csv_bytes,
            file_name="relatorio_fraudes_sicredi.csv",
            mime="text/csv",
        )
    else:
        st.info("Nenhuma transação encontrada com os filtros selecionados.")

# ---------------------------------------------------------------------------
# PÁGINA 2 — Detalhe da Transação
# ---------------------------------------------------------------------------
elif pagina == "🔍 Detalhe da Transação":
    st.title("🔍 Detalhe da Transação")

    resultados = st.session_state["resultados_cache"]
    transacoes = st.session_state["transacoes"]
    perfis = st.session_state["perfis"]

    ids = [tx.id for tx in transacoes]
    tx_id = st.selectbox("Selecione o ID da transação:", ids)

    tx_sel = next((t for t in transacoes if t.id == tx_id), None)
    resultado_sel = resultados.get(tx_id)

    if tx_sel and resultado_sel:
        perfil = perfis.get(tx_sel.associado_id)

        col1, col2 = st.columns([1.2, 1])

        with col1:
            st.subheader("Dados da Transação")
            st.markdown(f"""
| Campo | Valor |
|---|---|
| **ID** | `{tx_sel.id}` |
| **Associado** | {tx_sel.associado_id} {('— ' + perfil.nome) if perfil else ''} |
| **Data/Hora** | {tx_sel.data_hora.strftime('%d/%m/%Y às %H:%M:%S')} |
| **Estabelecimento** | {tx_sel.estabelecimento} |
| **Categoria** | {tx_sel.categoria} |
| **Valor** | R$ {tx_sel.valor:,.2f} |
| **Cidade/Estado** | {tx_sel.cidade} — {tx_sel.estado} |
| **País** | {tx_sel.pais} |
| **Distância da residência** | {tx_sel.distancia_residencia_km:.0f} km |
| **Canal** | {tx_sel.canal} |
""")

        with col2:
            st.subheader("Avaliação de Risco")
            nivel = resultado_sel.nivel_risco
            cor = _cor_nivel(nivel)
            st.markdown(
                f'<h2 style="color:{cor}">{ICONES_RISCO[nivel]} {nivel.upper()}</h2>',
                unsafe_allow_html=True,
            )

            # Gauge de pontuação
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=resultado_sel.pontuacao,
                number={"suffix": "/100", "font": {"size": 28}},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": cor},
                    "steps": [
                        {"range": [0, 40], "color": "#dcfce7"},
                        {"range": [40, 70], "color": "#fef9c3"},
                        {"range": [70, 100], "color": "#fee2e2"},
                    ],
                    "threshold": {"line": {"color": cor, "width": 4}, "thickness": 0.75, "value": resultado_sel.pontuacao},
                },
            ))
            fig_gauge.update_layout(height=220, margin=dict(t=10, b=10, l=20, r=20))
            st.plotly_chart(fig_gauge, width="stretch")

        # Recomendação
        st.markdown("---")
        st.subheader("Recomendação Preventiva")
        st.info(resultado_sel.recomendacao)
        st.markdown(f"**Justificativa:** {resultado_sel.justificativa}")

        # Fatores de risco
        if resultado_sel.fatores:
            st.markdown("---")
            st.subheader("Fatores de Risco Identificados")
            for fator in resultado_sel.fatores:
                cor_f = _cor_nivel(fator.nivel)
                with st.expander(f"{ICONES_RISCO[fator.nivel]} {fator.nome} — {fator.pontos:.0f} pts"):
                    st.markdown(f"<span style='color:{cor_f}'>{fator.descricao}</span>", unsafe_allow_html=True)
        else:
            st.success("✅ Nenhum fator de risco relevante identificado.")

        # Aviso
        st.markdown("---")
        st.caption(
            "⚠️ **Atenção:** Este sistema identifica *indícios* de comportamento suspeito, "
            "não confirma fraudes. Toda decisão final deve envolver revisão humana. "
            "Os dados são completamente fictícios."
        )

# ---------------------------------------------------------------------------
# PÁGINA 3 — Simulador
# ---------------------------------------------------------------------------
elif pagina == "🧪 Simulador":
    st.title("🧪 Simulador de Análise de Transação")
    st.markdown("Insira os dados de uma transação fictícia e veja como o agente de IA a avalia.")

    perfis = st.session_state["perfis"]
    transacoes = st.session_state["transacoes"]

    st.subheader("Dados da Transação")
    col1, col2, col3 = st.columns(3)

    associado_id = col1.selectbox("Associado", list(perfis.keys()))
    perfil_sim = perfis[associado_id]

    valor = col2.number_input("Valor (R$)", min_value=1.0, max_value=50000.0, value=150.0, step=10.0)
    canal = col3.selectbox("Canal", ["Presencial", "Online", "App"])

    col4, col5, col6 = st.columns(3)
    categoria = col4.selectbox("Categoria", CATEGORIAS)
    cidade = col5.selectbox("Cidade", CIDADES_BRASIL + ["Outra cidade"])
    estado = col6.text_input("Estado (sigla)", value="RS")

    col7, col8, col9 = st.columns(3)
    pais = col7.text_input("País", value="Brasil")
    distancia = col8.number_input("Distância da residência (km)", min_value=0.0, max_value=20000.0, value=10.0, step=5.0)
    hora_tx = col9.slider("Hora da transação", 0, 23, 14)

    estabelecimento = st.text_input("Nome do estabelecimento", value="Loja Exemplo Fictícia")

    # Perfil atual para referência
    with st.expander("ℹ️ Ver perfil habitual do associado selecionado"):
        st.markdown(f"""
- **Nome:** {perfil_sim.nome}
- **Valor médio:** R$ {perfil_sim.valor_medio_transacao:,.2f} (±{perfil_sim.desvio_padrao_valor:,.2f})
- **Categorias frequentes:** {', '.join(perfil_sim.categorias_frequentes)}
- **Cidades frequentes:** {', '.join(perfil_sim.cidades_frequentes)}
- **Horário habitual:** {perfil_sim.horario_habitual_inicio:02d}h – {perfil_sim.horario_habitual_fim:02d}h
""")

    if st.button("🔍 Analisar transação"):
        with st.spinner("Analisando transação..."):
            tx_sim = Transacao(
                id=str(uuid.uuid4())[:12],
                associado_id=associado_id,
                valor=valor,
                data_hora=datetime.now().replace(hour=hora_tx, minute=0, second=0, microsecond=0),
                categoria=categoria,
                estabelecimento=estabelecimento,
                cidade=cidade,
                estado=estado,
                pais=pais,
                distancia_residencia_km=distancia,
                canal=canal,
            )
            historico = [t for t in transacoes if t.associado_id == associado_id]
            resultado_sim = avaliar_transacao(tx_sim, perfil_sim, historico)

        # Salva no histórico
        st.session_state["historico_analises"].append({
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "transacao_id": tx_sim.id,
            "associado": associado_id,
            "estabelecimento": estabelecimento,
            "valor": f"R$ {valor:,.2f}",
            "pontuacao": resultado_sim.pontuacao,
            "nivel_risco": resultado_sim.nivel_risco,
            "recomendacao": resultado_sim.recomendacao,
            "fatores": [f.nome for f in resultado_sim.fatores],
        })

        # Exibe resultado
        st.markdown("---")
        st.subheader("Resultado da Análise")

        nivel = resultado_sim.nivel_risco
        cor = _cor_nivel(nivel)

        colr1, colr2 = st.columns([1, 1.5])
        with colr1:
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=resultado_sim.pontuacao,
                title={"text": f"Risco {nivel.upper()}", "font": {"color": cor}},
                number={"suffix": "/100"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": cor},
                    "steps": [
                        {"range": [0, 40], "color": "#dcfce7"},
                        {"range": [40, 70], "color": "#fef9c3"},
                        {"range": [70, 100], "color": "#fee2e2"},
                    ],
                },
            ))
            fig_gauge.update_layout(height=250, margin=dict(t=30, b=10, l=20, r=20))
            st.plotly_chart(fig_gauge, width="stretch")

        with colr2:
            st.markdown(f"**Recomendação:** {resultado_sim.recomendacao}")
            st.markdown(f"**Justificativa:** {resultado_sim.justificativa}")

            if resultado_sim.fatores:
                st.markdown("**Fatores identificados:**")
                for f in resultado_sim.fatores:
                    st.markdown(f"- {ICONES_RISCO[f.nivel]} **{f.nome}** (+{f.pontos:.0f} pts): {f.descricao}")
            else:
                st.success("Nenhum fator de risco identificado.")

        # --- Comparação visual: valor simulado vs perfil habitual ---
        st.markdown("---")
        st.subheader("Comparação com Perfil Habitual")
        media = perfil_sim.valor_medio_transacao
        desvio = perfil_sim.desvio_padrao_valor
        limite_normal = media + 2 * desvio

        df_comp = pd.DataFrame({
            "Referência": ["Valor simulado", "Média habitual", "Limite normal (+2σ)"],
            "Valor (R$)": [valor, media, limite_normal],
            "Cor": [cor, "#1a3a5c", "#6b7280"],
        })
        fig_comp = px.bar(
            df_comp, x="Referência", y="Valor (R$)",
            color="Referência",
            color_discrete_map={
                "Valor simulado": cor,
                "Média habitual": "#1a3a5c",
                "Limite normal (+2σ)": "#6b7280",
            },
            text_auto=".2f",
        )
        fig_comp.update_layout(height=260, margin=dict(t=10, b=10, l=0, r=0),
                               showlegend=False)
        st.plotly_chart(fig_comp, width="stretch")

        st.caption("⚠️ Simulação com dados fictícios. Não representa operação real.")

# ---------------------------------------------------------------------------
# PÁGINA 4 — Histórico de Análises
# ---------------------------------------------------------------------------
elif pagina == "📋 Histórico":
    st.title("📋 Histórico de Análises do Simulador")

    historico = st.session_state.get("historico_analises", [])

    if not historico:
        st.info("Nenhuma análise realizada ainda. Use o Simulador para gerar análises.")
    else:
        st.markdown(f"**{len(historico)} análise(s) registrada(s) nesta sessão.**")

        for i, item in enumerate(reversed(historico), 1):
            nivel = item["nivel_risco"]
            cor = _cor_nivel(nivel)
            with st.expander(
                f"{ICONES_RISCO[nivel]} [{item['timestamp']}] {item['estabelecimento']} — "
                f"{item['valor']} — Risco {nivel.upper()} ({item['pontuacao']:.0f} pts)"
            ):
                st.markdown(f"- **Associado:** {item['associado']}")
                st.markdown(f"- **ID da transação:** `{item['transacao_id']}`")
                st.markdown(f"- **Pontuação:** {item['pontuacao']:.0f}/100")
                st.markdown(f"- **Recomendação:** {item['recomendacao']}")
                if item["fatores"]:
                    st.markdown(f"- **Fatores:** {', '.join(item['fatores'])}")
                else:
                    st.markdown("- **Fatores:** Nenhum")

        if st.button("🗑️ Limpar histórico desta sessão"):
            st.session_state["historico_analises"] = []
            st.rerun()

    st.caption(
        "ℹ️ O histórico existe apenas na sessão atual e não armazena dados pessoais reais. "
        "Ao recarregar a página, o histórico é apagado."
    )

# ---------------------------------------------------------------------------
# PÁGINA 5 — Sobre
# ---------------------------------------------------------------------------
elif pagina == "ℹ️ Sobre":
    st.title("ℹ️ Sobre o Projeto")

    st.markdown("""
## 🛡️ Prevenção Inteligente a Fraudes — Proposta para o Sicredi

Este protótipo foi desenvolvido como proposta para a competição de inovação do Sicredi,
com o tema **"Prevenção Inteligente a Fraudes e Segurança do Associado"**.

---

### 🎯 Objetivo
Demonstrar como um agente de IA pode ajudar a identificar transações suspeitas,
explicar os fatores de risco e recomendar ações preventivas — **sem prejuízo às compras legítimas**.

---

### 🏗️ Arquitetura do Agente

```
Transação recebida
        │
        ▼
Validação de entrada
        │
        ▼
Motor de Avaliação de Risco (motor_local)
   ├── Regra: Valor elevado
   ├── Regra: Categoria incomum
   ├── Regra: Localização incomum
   ├── Regra: Horário incomum
   ├── Regra: Alta frequência
   ├── Regra: País estrangeiro
   └── Regra: Canal suspeito
        │
        ▼
Pontuação 0-100 + Fatores identificados
        │
        ▼
Classificação: baixo / médio / alto
        │
        ▼
Recomendação preventiva + Justificativa
        │
        ├──▶ [watsonx Orchestrate — integração planejada]
        │         Enriquece a explicação em linguagem natural
        │         NÃO altera a pontuação calculada
        │
        ▼
Resultado apresentado no painel
```

---

### ⚙️ Tecnologias
| Componente | Tecnologia |
|---|---|
| Interface | Python + Streamlit |
| Motor de risco | Python puro (regras + estatística) |
| Dados fictícios | Gerador sintético (sem dados reais) |
| Gráficos | Plotly |
| IA planejada | IBM watsonx Orchestrate (pendente de credenciais) |

---

### ⚠️ Declarações importantes
- **Todos os dados são fictícios e sintéticos.** Nenhuma informação real de clientes ou transações bancárias é utilizada.
- Este sistema identifica *indícios* de comportamento suspeito, **não confirma fraudes**.
- Nenhuma ação irreversível (bloqueio de cartão, envio de mensagens reais) é executada.
- A integração com watsonx Orchestrate está **planejada mas pendente de configuração**.
- O sistema não afirma precisão real sem avaliação empírica com dados reais.

---

### 📁 Estrutura do Projeto
```
sicredi_fraudes/
├── app.py                     ← Interface principal
├── requirements.txt
├── src/
│   ├── core/
│   │   ├── models.py          ← Modelos de dados
│   │   ├── risk_engine.py     ← Motor de avaliação de risco
│   │   └── watsonx_client.py  ← Integração planejada com watsonx
│   └── data/
│       └── generator.py       ← Gerador de dados fictícios
├── tests/                     ← Testes automatizados
└── docs/                      ← Documentação e guias
    └── watsonx/               ← Guia de configuração watsonx
```
""")
