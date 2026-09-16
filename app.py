import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

from data_generator import generate_bogcm_mock_data

st.set_page_config(
    page_title="GCM Niterói - Sistema BOGCM",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# PALETA DE CORES INSTITUCIONAL E MAPEAMENTO POR INSPETORIA / COORDENADORIA
# ==============================================================================
GOLD_AMARELO = "#F1C21B"
AZUL_NITEROI = "#0B1B82"
FUNDO_ESCURO = "#0A0F24"
FUNDO_CARD = "#131B38"
TEXTO_CLARO = "#F8FAFC"
TEXTO_MUTED = "#94A3B8"

# Cores fixas e distintas para cada Inspetoria Regional
COLOR_INSPETORIAS = {
    '1ª Inspetoria (Centro)': '#F1C21B',        # Dourado
    '2ª Inspetoria (Icaraí)': '#3B82F6',       # Azul Claro
    '3ª Inspetoria (São Francisco)': '#8B5CF6',  # Roxo
    '4ª Inspetoria (Fonseca)': '#EF4444',      # Vermelho
    '5ª Inspetoria (Oceânica)': '#10B981'      # Verde
}

# Cores fixas para cada Coordenadoria Especializada
COLOR_COORDENADORIAS = {
    'CMA': '#059669',          # Verde Ambiental
    'PGMP': '#EC4899',         # Rosa/Proteção Mulher
    'CT': '#F59E0B',           # Laranja Trânsito
    'CPE': '#3B82F6',          # Azul Escolar
    'GCM_PATRULHA': '#1E40AF'  # Azul Marinho Patrulha
}

st.markdown(f"""
<style>
/* Estilização do fundo da página */
.stApp {{
    background-color: {FUNDO_ESCURO};
}}

/* Estilização dos Cards de Indicadores (KPIs) */
div[data-testid="stMetric"] {{
    background-color: {FUNDO_CARD} !important;
    border-top: 4px solid {GOLD_AMARELO} !important;
    border-radius: 6px;
    padding: 12px 16px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
}}
div[data-testid="stMetricValue"] {{
    color: #FFFFFF !important;
    font-size: 1.8rem !important;
    font-weight: 700 !important;
}}
div[data-testid="stMetricLabel"] {{
    color: {TEXTO_MUTED} !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.02em;
}}

/* Títulos de seções */
h1, h2, h3 {{
    color: {TEXTO_CLARO} !important;
    font-weight: 600 !important;
}}

/* Linha divisória em tom dourado */
hr {{
    border-color: {GOLD_AMARELO} !important;
    opacity: 0.3;
}}

/* Estilização da Barra Lateral */
section[data-testid="stSidebar"] {{
    background-color: {FUNDO_CARD};
}}

/* Estilização de abas */
button[data-baseweb="tab"] {{
    font-weight: 600 !important;
}}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    return generate_bogcm_mock_data(1500)


df_raw = load_data()

# ==============================================================================
# BARRA LATERAL (SIDEBAR) - IDENTIDADE VISUAL E FILTROS
# ==============================================================================
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", use_container_width=True)

st.sidebar.markdown(
    f"<h3 style='text-align: center; color: {GOLD_AMARELO};'>GUARDA CIVIL MUNICIPAL</h3>",
    unsafe_allow_html=True
)
st.sidebar.markdown(
    f"<p style='text-align: center; color: {TEXTO_MUTED}; font-size: 0.8rem;'>"
    "PREFEITURA MUNICIPAL DE NITERÓI<br>Secretaria Municipal de Ordem Pública</p>",
    unsafe_allow_html=True
)
st.sidebar.markdown("---")
st.sidebar.subheader("Filtros Táticos")

date_min = df_raw['data_hora'].min().date()
date_max = df_raw['data_hora'].max().date()

date_range = st.sidebar.date_input(
    "Período de Análise",
    value=[date_min, date_max],
    min_value=date_min,
    max_value=date_max
)

# Tratamento seguro de seleção de data no calendário
if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    single_date = date_range[0] if isinstance(date_range, (list, tuple)) else date_range
    start_date = end_date = single_date

inspetorias_list = ["Todas"] + sorted(list(df_raw['inspetoria'].unique()))
selected_inspetoria = st.sidebar.selectbox("Inspetoria Regional", inspetorias_list)

coordenadorias_list = ["Todas"] + sorted(list(df_raw['coordenadoria'].unique()))
selected_coordenadoria = st.sidebar.selectbox("Coordenadoria Especializada", coordenadorias_list)

categorias_list = ["Todas"] + sorted(list(df_raw['categoria'].unique()))
selected_categoria = st.sidebar.selectbox("Eixo de Atuação", categorias_list)

# Aplicação dos Filtros
df_filtered = df_raw.copy()
df_filtered = df_filtered[(df_filtered['data_hora'].dt.date >= start_date) &
                          (df_filtered['data_hora'].dt.date <= end_date)]

if selected_inspetoria != "Todas":
    df_filtered = df_filtered[df_filtered['inspetoria'] == selected_inspetoria]
if selected_coordenadoria != "Todas":
    df_filtered = df_filtered[df_filtered['coordenadoria'] == selected_coordenadoria]
if selected_categoria != "Todas":
    df_filtered = df_filtered[df_filtered['categoria'] == selected_categoria]

# ==============================================================================
# CABEÇALHO PRINCIPAL
# ==============================================================================
head_col1, head_col2 = st.columns([1, 6])
with head_col1:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=90)
with head_col2:
    st.title("Sistema de Inteligência Operacional — BOGCM")
    st.markdown(
        f"<p style='color: {TEXTO_MUTED}; font-size: 1rem; margin-top: -10px;'>"
        "Painel Analítico de Ocorrências e Produtividade da Guarda Civil Municipal de Niterói</p>",
        unsafe_allow_html=True
    )

st.markdown("---")

if df_filtered.empty:
    st.warning("Nenhum registro encontrado para os filtros selecionados. Ajuste os filtros na barra lateral.")
    st.stop()

PLOTLY_TEMPLATE = "plotly_dark"


def layout_padrao(fig, **kwargs):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color=TEXTO_CLARO,
        margin=dict(t=30, b=10, l=10, r=10),
        **kwargs
    )
    return fig


# ==============================================================================
# INDICADORES CHAVE (KPIS)
# ==============================================================================
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

total_ocorrencias = len(df_filtered)
total_equinos = df_filtered['equinos_resgatados'].sum()
total_fauna = df_filtered['animais_silvestres_resgatados'].sum()
total_veiculos = df_filtered['veiculos_removidos'].sum()
atendimentos_cisp = len(df_filtered[df_filtered['origem'] == 'CISP 153'])

kpi1.metric("Total de BOGCM", f"{total_ocorrencias:,}")
kpi2.metric("Equinos Resgatados", f"{total_equinos:,}")
kpi3.metric("Fauna Silvestre", f"{total_fauna:,}")
kpi4.metric("Veículos Removidos", f"{total_veiculos:,}")
kpi5.metric("Chamados CISP 153", f"{atendimentos_cisp:,}")

st.markdown("<br>", unsafe_allow_html=True)

# ==============================================================================
# ABAS VISUAIS
# ==============================================================================
tab_regional, tab_cma, tab_geo, tab_tabela = st.tabs([
    "📊 Produtividade por Regional",
    "🍃 Coordenadoria de Meio Ambiente (CMA)",
    "🗺️ Mapeamento Espacial",
    "📄 Relatório de Microdados"
])

with tab_regional:
    col_reg1, col_reg2 = st.columns(2)

    with col_reg1:
        st.subheader("Volume de Ocorrências por Inspetoria Regional")
        df_insp = df_filtered.groupby('inspetoria').size().reset_index(name='registros').sort_values('registros')
        fig_insp = px.bar(
            df_insp, x='registros', y='inspetoria', orientation='h',
            color='inspetoria',
            color_discrete_map=COLOR_INSPETORIAS,
            template=PLOTLY_TEMPLATE, text='registros'
        )
        fig_insp.update_traces(textposition='outside')
        layout_padrao(fig_insp, xaxis_title="Volume de Registros", yaxis_title="", showlegend=False)
        st.plotly_chart(fig_insp, use_container_width=True)

    with col_reg2:
        st.subheader("Distribuição por Categoria de Ação")
        # Retorno do Gráfico de Pizza / Rosca
        df_cat = df_filtered.groupby('categoria').size().reset_index(name='registros')
        fig_cat = px.pie(
            df_cat, values='registros', names='categoria',
            color_discrete_sequence=[GOLD_AMARELO, "#3B82F6", "#059669", "#EC4899", "#8B5CF6"],
            hole=0.4, template=PLOTLY_TEMPLATE
        )
        layout_padrao(fig_cat)
        st.plotly_chart(fig_cat, use_container_width=True)

    st.subheader("Evolução Temporal Semanal de Registros")
    df_temp = df_filtered.set_index('data_hora').resample('W').size().reset_index(name='registros')
    fig_temp = px.line(
        df_temp, x='data_hora', y='registros',
        markers=True,
        color_discrete_sequence=[GOLD_AMARELO],
        template=PLOTLY_TEMPLATE
    )
    layout_padrao(fig_temp, xaxis_title="Semana", yaxis_title="BOGCMs")
    st.plotly_chart(fig_temp, use_container_width=True)

with tab_cma:
    st.subheader("Indicadores Operacionais — Coordenadoria de Meio Ambiente (CMA)")
    st.markdown("Monitoramento consolidado do resgate de animais silvestres e apreensão de equinos soltos.")

    cma_col1, cma_col2 = st.columns(2)
    df_cma = df_filtered[df_filtered['coordenadoria'] == 'CMA']

    with cma_col1:
        st.markdown("#### Resgate de Fauna Silvestre por Bairro")
        df_fauna = df_cma.groupby('bairro')['animais_silvestres_resgatados'].sum().reset_index()
        df_fauna = df_fauna[df_fauna['animais_silvestres_resgatados'] > 0].sort_values(
            'animais_silvestres_resgatados', ascending=True
        )
        fig_fauna = px.bar(
            df_fauna, x='animais_silvestres_resgatados', y='bairro', orientation='h',
            color_discrete_sequence=["#059669"],
            template=PLOTLY_TEMPLATE, text='animais_silvestres_resgatados'
        )
        fig_fauna.update_traces(textposition='outside')
        layout_padrao(fig_fauna, xaxis_title="Animais Resgatados", yaxis_title="", showlegend=False)
        st.plotly_chart(fig_fauna, use_container_width=True)

    with cma_col2:
        st.markdown("#### Apreensão de Equinos por Inspetoria Regional")
        df_equinos = df_cma.groupby('inspetoria')['equinos_resgatados'].sum().reset_index().sort_values(
            'equinos_resgatados', ascending=True
        )
        fig_equinos = px.bar(
            df_equinos, x='equinos_resgatados', y='inspetoria', orientation='h',
            color='inspetoria',
            color_discrete_map=COLOR_INSPETORIAS,
            template=PLOTLY_TEMPLATE, text='equinos_resgatados'
        )
        fig_equinos.update_traces(textposition='outside')
        layout_padrao(fig_equinos, xaxis_title="Equinos Apreendidos", yaxis_title="", showlegend=False)
        st.plotly_chart(fig_equinos, use_container_width=True)

with tab_geo:
    st.subheader("Geoprocessamento e Mapeamento Territorial")
    
    tipo_mapa = st.radio(
        "Modo de Visualização do Mapa:",
        ["Por Inspetoria Regional (Cores)", "Por Coordenadoria Especializada (Cores)", "Mancha de Calor (Heatmap)"],
        horizontal=True
    )

    if tipo_mapa == "Por Inspetoria Regional (Cores)":
        if hasattr(px, "scatter_map"):
            fig_map = px.scatter_map(
                df_filtered, lat='latitude', lon='longitude',
                color='inspetoria', color_discrete_map=COLOR_INSPETORIAS,
                zoom=11, center=dict(lat=-22.9000, lon=-43.0800),
                hover_name='tipo_ocorrencia', hover_data=['bairro', 'coordenadoria'],
                map_style="carto-darkmatter", template=PLOTLY_TEMPLATE
            )
        else:
            fig_map = px.scatter_mapbox(
                df_filtered, lat='latitude', lon='longitude',
                color='inspetoria', color_discrete_map=COLOR_INSPETORIAS,
                zoom=11, center=dict(lat=-22.9000, lon=-43.0800),
                hover_name='tipo_ocorrencia', hover_data=['bairro', 'coordenadoria'],
                mapbox_style="carto-darkmatter", template=PLOTLY_TEMPLATE
            )
    elif tipo_mapa == "Por Coordenadoria Especializada (Cores)":
        if hasattr(px, "scatter_map"):
            fig_map = px.scatter_map(
                df_filtered, lat='latitude', lon='longitude',
                color='coordenadoria', color_discrete_map=COLOR_COORDENADORIAS,
                zoom=11, center=dict(lat=-22.9000, lon=-43.0800),
                hover_name='tipo_ocorrencia', hover_data=['bairro', 'inspetoria'],
                map_style="carto-darkmatter", template=PLOTLY_TEMPLATE
            )
        else:
            fig_map = px.scatter_mapbox(
                df_filtered, lat='latitude', lon='longitude',
                color='coordenadoria', color_discrete_map=COLOR_COORDENADORIAS,
                zoom=11, center=dict(lat=-22.9000, lon=-43.0800),
                hover_name='tipo_ocorrencia', hover_data=['bairro', 'inspetoria'],
                mapbox_style="carto-darkmatter", template=PLOTLY_TEMPLATE
            )
    else:  # Mancha de Calor / Heatmap
        map_kwargs = dict(
            lat='latitude', lon='longitude', z=np.ones(len(df_filtered)),
            radius=14, center=dict(lat=-22.9000, lon=-43.0800), zoom=11,
            hover_name='tipo_ocorrencia', hover_data=['bairro', 'inspetoria', 'coordenadoria'],
        )
        if hasattr(px, "density_map"):
            fig_map = px.density_map(df_filtered, map_style="carto-darkmatter", **map_kwargs)
        else:
            fig_map = px.density_mapbox(df_filtered, mapbox_style="carto-darkmatter", **map_kwargs)

    fig_map.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    st.plotly_chart(fig_map, use_container_width=True)

with tab_tabela:
    st.subheader("Base de Microdados Filtrada do BOGCM")
    st.dataframe(
        df_filtered[['id_bogcm', 'data_hora', 'inspetoria', 'bairro', 'coordenadoria',
                     'categoria', 'tipo_ocorrencia', 'origem']],
        use_container_width=True
    )
    csv_bytes = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Exportar Dados para CSV",
        data=csv_bytes,
        file_name="relatorio_bogcm_niteroi.csv",
        mime="text/csv"
    )