# painel_recorrencia_streamlit.py

import streamlit as st
import pandas as pd

from recorrencia_basicos import (
    carregar_bases,
    painel_recorrencia_basicos,
)
from visualizacoes_recorrencia import (
    plot_top_itens_recorrencia_mensal,
    plot_recorrencia_mensal_por_obra,
    plot_itens_reqs_subsequentes,
    plot_recorrencia_semanal_heatmap,
    plot_intervalo_medio_scatter,
    plot_itens_pingados,
)


st.set_page_config(
    page_title="Painel de Recorrência - Materiais Básicos",
    page_icon="📦",
    layout="wide",
)

st.title("📦 Recorrência de Materiais Básicos")
st.caption("Análise de padrões de consumo por obra, item e tempo.")


@st.cache_data
def carregar_painel(ano: int):
    df = carregar_bases()
    painel = painel_recorrencia_basicos(df, ano=ano)
    return df, painel


# ---------------- Barra lateral ----------------
st.sidebar.header("Filtros")

ano = st.sidebar.number_input("Ano da análise", min_value=2015, max_value=2100, value=2025, step=1)

df_erp, painel = carregar_painel(ano)

df_mes = painel["basicos_reqs_mes"]
df_subseq = painel["basicos_reqs_subsequentes"]
df_semana = painel["basicos_semanal_por_obra"]
df_interval = painel["intervalo_medio_entre_pedidos"]
df_pingados = painel["itens_pequena_qtd_alta_freq"]
resumo = painel["resumo_indicadores"]

# Lista de obras para filtro em algumas visões
obras_disp = sorted(df_mes["EMPRD"].unique()) if not df_mes.empty else []
obra_sel = st.sidebar.selectbox("Obra para detalhamento de recorrência mensal", options=obras_disp) if obras_disp else None

st.sidebar.markdown("---")
st.sidebar.write("**Indicadores brutos**")
st.sidebar.json(resumo)


# ---------------- Resumo no topo ----------------
col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Itens com 2+ REQs/mês",
    resumo.get("qtd_itens_2plus_reqs_mes", 0),
)
col2.metric(
    "Itens com REQs subsequentes",
    resumo.get("qtd_itens_com_reqs_subsequentes", 0),
)
col3.metric(
    "Itens com recorrência semanal",
    resumo.get("qtd_itens_semanal_obra", 0),
)
col4.metric(
    "Itens com intervalo médio calculado",
    resumo.get("qtd_itens_com_intervalo_calculado", 0),
)
col5.metric(
    "Itens pingados (alta freq / baixa qtd)",
    resumo.get("qtd_itens_pequena_qtd_alta_freq", 0),
)

st.markdown("---")

# ---------------- Abas principais ----------------
tab_resumo, tab_mensal, tab_subseq, tab_semanal, tab_intervalo, tab_pingados = st.tabs([
    "Visão Geral",
    "Recorrência Mensal",
    "REQs Subsequentes",
    "Recorrência Semanal",
    "Intervalo Médio",
    "Itens Pingados",
])

# --- Aba: Visão Geral ---
with tab_resumo:
    st.subheader("Top itens recorrentes (mensal)")
    st.caption(
        "Itens básicos que aparecem com maior frequência em requisições ao longo dos meses. "
        "Esse gráfico mostra quantas vezes cada item foi solicitado ao longo do ano, "
        "somando a recorrência mensal consolidada."
    )
    fig1 = plot_top_itens_recorrencia_mensal(df_mes)
    st.pyplot(fig1)

    st.subheader("Itens em REQs subsequentes")
    st.caption(
        "Itens que foram pedidos novamente na requisição seguinte da mesma obra. "
        "É útil para identificar padrões de reposição contínua ou falha no planejamento de compras."
    )
    fig2 = plot_itens_reqs_subsequentes(df_subseq)
    st.pyplot(fig2)

    st.subheader("Itens pingados (alta frequência + baixa quantidade)")
    st.caption(
        "Itens que aparecem muitas vezes no ano, mas sempre em quantidades pequenas. "
        "São potenciais candidatos para criação de kits, contratos de fornecimento ou compra recorrente."
    )
    fig3 = plot_itens_pingados(df_pingados)
    st.pyplot(fig3)


# --- Aba: Recorrência Mensal ---
with tab_mensal:
    st.subheader("Top itens básicos com recorrência mensal (geral)")
    st.caption(
        "Mostra quais itens básicos aparecem em mais requisições dentro dos meses analisados. "
        "Ajuda a entender consumo recorrente por item, independentemente da obra."
    )
    fig = plot_top_itens_recorrencia_mensal(df_mes)
    st.pyplot(fig)

    if obra_sel is not None:
        st.subheader(f"Recorrência mensal - Obra {obra_sel}")
        st.caption(
            "Distribuição mensal de solicitações do item por obra. "
            "Útil para entender sazonalidade ou padrões de reabastecimento específicos de cada projeto."
        )
        fig_obra = plot_recorrencia_mensal_por_obra(df_mes, obra_sel)
        st.pyplot(fig_obra)

    if not df_mes.empty:
        st.subheader("Tabela detalhada - Recorrência mensal")
        st.caption(
            "Tabela completa contendo todas as ocorrências mensais por item, obra e mês. "
            "Representa a base utilizada na construção dos gráficos mensais."
        )
        st.dataframe(df_mes)


# --- Aba: REQs Subsequentes ---
with tab_subseq:
    st.subheader("Itens que aparecem em requisições subsequentes")
    st.caption(
        "Mostra os itens básicos que foram solicitados repetidamente de uma requisição para a próxima, "
        "indicando uso contínuo ou potencial falta de estoque."
    )

    fig = plot_itens_reqs_subsequentes(df_subseq)
    st.pyplot(fig)

    if not df_subseq.empty:
        st.subheader("Tabela detalhada - REQs subsequentes")
        st.caption("Lista completa dos itens em requisições sequenciais por obra.")
        st.dataframe(df_subseq)


# --- Aba: Recorrência Semanal ---
with tab_semanal:
    st.subheader("Heatmap - Recorrência semanal por obra x item")
    st.caption(
        "Mapa de calor mostrando em quais semanas e obras cada item básico aparece. "
        "Ajuda a identificar picos de demanda, frequência semanal e itens críticos."
    )
    fig = plot_recorrencia_semanal_heatmap(df_semana, top_itens=10, top_obras=10)
    st.pyplot(fig)

    if not df_semana.empty:
        st.subheader("Tabela detalhada - Recorrência semanal")
        st.caption("Tabela base com a ocorrência semanal consolidada por obra e item.")
        st.dataframe(df_semana)


# --- Aba: Intervalo Médio entre Pedidos ---
with tab_intervalo:
    st.subheader("Intervalo médio entre pedidos x nº de REQs (itens básicos)")
    st.caption(
        "Mostra, para cada item, qual o intervalo médio em dias entre as solicitações. "
        "Ótimo para prever periodicidade, necessidade futura e possíveis padrões de reposição."
    )
    fig = plot_intervalo_medio_scatter(df_interval)
    st.pyplot(fig)

    if not df_interval.empty:
        st.subheader("Tabela detalhada - Intervalos")
        st.caption("Tabela contendo o intervalo médio por item e seu número total de requisições.")
        st.dataframe(df_interval)


# --- Aba: Itens Pingados ---
with tab_pingados:
    st.subheader("Itens pingados (alta frequência + baixa quantidade média)")
    st.caption(
        "Itens que aparecem muitas vezes durante o ano, mas em pequenas quantidades por pedido. "
        "Indicador importante para avaliar desperdícios logísticos, frete e possíveis compras recorrentes."
    )
    fig = plot_itens_pingados(df_pingados)
    st.pyplot(fig)

    if not df_pingados.empty:
        st.subheader("Tabela detalhada - Itens pingados")
        st.caption("Tabela com todos os itens pingados identificados no período.")
        st.dataframe(df_pingados)
