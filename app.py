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

# Estilização CSS personalizada para Design Sóbrio e Institucional
st.markdown("""
    <style>
    /* Estilização dos Cards de Indicadores (KPIs) */
    .stMetric {
        background-color: #131B38 !important;
        border-top: 4px solid #F1C21B !important;
        border-radius: 6px;
        padding: 12px 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    div[data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #94A3B8 !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
    }
    /* Estilização dos títulos de seções */
    h1, h2, h3 {
        color: #F8FAFC !important;
        font-weight: 600 !important;
    }
    /* Linha divisória fina na cor ouro */
    hr {
        border-color: #F1C21B !important;
        opacity: 0.3;
    }
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

st.sidebar.markdown("<h3 style='text-align: center; color: #F1C21B;'>GUARDA CIVIL MUNICIPAL</h3>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; color: #94A3B8; font-size: 0.8rem;'>PREFEITURA MUNICIPAL DE NITERÓI<br>Secretaria Municipal de Ordem Pública</p>", unsafe_allow_html=True)
st.sidebar.markdown("---")

st.sidebar.subheader("Filtros Táticos")

date_min = df_raw['data_hora'].min().date()
date_max = df_raw['data_hora'].max().date()

start_date, end_date = st.sidebar.date_input(
    "Período de Análise",
    value=[date_min, date_max],
    min_value=date_min,
    max_value=date_max
)

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
    st.markdown("<p style='color: #94A3B8; font-size: 1rem;'>Painel Analítico de Ocorrências e Produtividade da Guarda Civil Municipal de Niterói</p>", unsafe_allow_html=True)

st.markdown("---")

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
kpi2.metric("Equinos Resgatados", f"{total_equinos}")
kpi3.metric("Fauna Silvestre", f"{total_fauna}")
kpi4.metric("Veículos Removidos", f"{total_veiculos}")
kpi5.metric("Chamados CISP 153", f"{atendimentos_cisp}")

st.markdown("<br>", unsafe_allow_html=True)

# Paleta Institucional para Gráficos (Azul GCM, Dourado Ouro, Vermelho Tocha, Verde Ambiental)
PALETA_GCM = ["#0B1B82", "#F1C21B", "#1E3A8A", "#D9251D", "#059669", "#475569"]

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
        df_insp = df_filtered.groupby('inspetoria').size().reset_index(name='registros')
        fig_insp = px.bar(
            df_insp, x='registros', y='inspetoria', orientation='h',
            color_discrete_sequence=['#F1C21B'],
            template='plotly_dark'
        )
        fig_insp.update_layout(
            xaxis_title="Volume de Registros", yaxis_title="", showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_insp, use_container_width=True)

    with col_reg2:
        st.subheader("Distribuição por Categoria de Ação")
        df_cat = df_filtered.groupby('categoria').size().reset_index(name='registros')
        fig_cat = px.pie(
            df_cat, values='registros', names='categoria',
            color_discrete_sequence=PALETA_GCM,
            hole=0.4, template='plotly_dark'
        )
        fig_cat.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_cat, use_container_width=True)

    st.subheader("Evolução Temporal Semanal de Registros")
    df_temp = df_filtered.set_index('data_hora').resample('W').size().reset_index(name='registros')
    fig_temp = px.line(
        df_temp, x='data_hora', y='registros',
        markers=True, line_shape='spline',
        color_discrete_sequence=['#F1C21B'],
        template='plotly_dark'
    )
    fig_temp.update_layout(
        xaxis_title="Semana", yaxis_title="BOGCMs",
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_temp, use_container_width=True)

with tab_cma:
    st.subheader("Indicadores Operacionais — Coordenadoria de Meio Ambiente (CMA)")
    st.markdown("Monitoramento consolidado do resgate de animais silvestres e apreensão de equinos soltos.")
    
    cma_col1, cma_col2 = st.columns(2)
    df_cma = df_filtered[df_filtered['coordenadoria'] == 'CMA']
    
    with cma_col1:
        st.markdown("#### Resgate de Fauna Silvestre por Bairro")
        df_fauna = df_cma.groupby('bairro')['animais_silvestres_resgatados'].sum().reset_index()
        df_fauna = df_fauna[df_fauna['animais_silvestres_resgatados'] > 0].sort_values('animais_silvestres_resgatados', ascending=False)
        fig_fauna = px.bar(
            df_fauna, x='bairro', y='animais_silvestres_resgatados',
            color_discrete_sequence=['#059669'],
            template='plotly_dark'
        )
        fig_fauna.update_layout(
            xaxis_title="Bairro", yaxis_title="Animais Resgatados", showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_fauna, use_container_width=True)

    with cma_col2:
        st.markdown("#### Apreensão de Equinos por Inspetoria Regional")
        df_equinos = df_cma.groupby('inspetoria')['equinos_resgatados'].sum().reset_index()
        fig_equinos = px.pie(
            df_equinos, values='equinos_resgatados', names='inspetoria',
            color_discrete_sequence=['#F1C21B', '#D9251D', '#0B1B82', '#1E3A8A', '#059669'],
            template='plotly_dark'
        )
        fig_equinos.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_equinos, use_container_width=True)

with tab_geo:
    st.subheader("Geoprocessamento e Mancha de Ocorrências")
    if not df_filtered.empty:
        if hasattr(px, "density_map"):
            fig_map = px.density_map(
                df_filtered, 
                lat='latitude', 
                lon='longitude', 
                z=np.ones(len(df_filtered)),
                radius=14,
                center=dict(lat=-22.9000, lon=-43.0800), 
                zoom=11,
                map_style="carto-darkmatter",
                hover_name='tipo_ocorrencia',
                hover_data=['bairro', 'inspetoria', 'coordenadoria'],
                template='plotly_dark'
            )
        else:
            fig_map = px.density_mapbox(
                df_filtered, 
                lat='latitude', 
                lon='longitude', 
                z=np.ones(len(df_filtered)),
                radius=14,
                center=dict(lat=-22.9000, lon=-43.0800), 
                zoom=11,
                mapbox_style="carto-darkmatter",
                hover_name='tipo_ocorrencia',
                hover_data=['bairro', 'inspetoria', 'coordenadoria'],
                template='plotly_dark'
            )
        fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True)

with tab_tabela:
    st.subheader("Base de Microdados Filtrada do BOGCM")
    st.dataframe(
        df_filtered[['id_bogcm', 'data_hora', 'inspetoria', 'bairro', 'coordenadoria', 'categoria', 'tipo_ocorrencia', 'origem']],
        use_container_width=True
    )
    
    csv_bytes = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Exportar Dados para CSV",
        data=csv_bytes,
        file_name="relatorio_bogcm_niteroi.csv",
        mime="text/csv"
    )
    