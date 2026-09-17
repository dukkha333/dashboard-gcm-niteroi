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
# PALETAS DE CORES INSTITUCIONAIS
# ==============================================================================
GOLD_AMARELO = "#F1C21B"
AZUL_NITEROI = "#0B1B82"
FUNDO_ESCURO = "#0A0F24"
FUNDO_CARD = "#131B38"
TEXTO_CLARO = "#F8FAFC"
TEXTO_MUTED = "#94A3B8"

COLOR_INSPETORIAS = {
    '1ª Inspetoria (Centro)': '#F1C21B',        # Dourado
    '2ª Inspetoria (Icaraí)': '#3B82F6',       # Azul Claro
    '3ª Inspetoria (São Francisco)': '#8B5CF6',  # Roxo
    '4ª Inspetoria (Fonseca)': '#EF4444',      # Vermelho
    '5ª Inspetoria (Oceânica)': '#10B981'      # Verde
}

COLOR_COORDENADORIAS = {
    'CASS': '#F59E0B',         # Laranja Apoio Social PSR
    'CMA': '#059669',          # Verde Ambiental
    'PGMP': '#EC4899',         # Rosa Proteção Mulher
    'CT': '#3B82F6',           # Azul Trânsito
    'POSTURAS': '#EF4444',     # Vermelho Fiscalização
    'CPE': '#8B5CF6',          # Roxo Escolar
    'GCM_PATRULHA': '#64748B'  # Cinza Patrulhamento
}

st.markdown(f"""
<style>
.stApp {{ background-color: {FUNDO_ESCURO}; }}
div[data-testid="stMetric"] {{
    background-color: {FUNDO_CARD} !important;
    border-top: 4px solid {GOLD_AMARELO} !important;
    border-radius: 6px;
    padding: 10px 14px;
}}
div[data-testid="stMetricValue"] {{ color: #FFFFFF !important; font-size: 1.7rem !important; font-weight: 700 !important; }}
div[data-testid="stMetricLabel"] {{ color: {TEXTO_MUTED} !important; font-size: 0.8rem !important; font-weight: 600 !important; text-transform: uppercase; }}
h1, h2, h3 {{ color: {TEXTO_CLARO} !important; font-weight: 600 !important; }}
hr {{ border-color: {GOLD_AMARELO} !important; opacity: 0.3; }}
section[data-testid="stSidebar"] {{ background-color: {FUNDO_CARD}; }}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    return generate_bogcm_mock_data(2000)

df_raw = load_data()

# ==============================================================================
# BARRA LATERAL (FILTROS TEMPORAIS E OPERACIONAIS)
# ==============================================================================
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", use_container_width=True)

st.sidebar.markdown(f"<h3 style='text-align: center; color: {GOLD_AMARELO};'>GUARDA CIVIL MUNICIPAL</h3>", unsafe_allow_html=True)
st.sidebar.markdown(f"<p style='text-align: center; color: {TEXTO_MUTED}; font-size: 0.8rem;'>PREFEITURA MUNICIPAL DE NITERÓI<br>Secretaria Municipal de Ordem Pública</p>", unsafe_allow_html=True)
st.sidebar.markdown("---")

st.sidebar.subheader("📅 Período & Calendário")
date_min = df_raw['data_hora'].min().date()
date_max = df_raw['data_hora'].max().date()

date_range = st.sidebar.date_input("Intervalo de Datas", value=[date_min, date_max], min_value=date_min, max_value=date_max)

if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    single_date = date_range[0] if isinstance(date_range, (list, tuple)) else date_range
    start_date = end_date = single_date

st.sidebar.subheader("⏰ Filtro de Horário (Escala/Turno)")
modo_hora = st.sidebar.radio("Modo de Seleção de Hora:", ["Todas as Horas", "Hora Específica", "Faixa Horária (Turno)"])

if modo_hora == "Hora Específica":
    hora_sel = st.sidebar.slider("Selecione a Hora Exata (0h - 23h):", 0, 23, 14)
elif modo_hora == "Faixa Horária (Turno)":
    hora_inicio, hora_fim = st.sidebar.slider("Selecione o Turno Operacional:", 0, 23, (18, 23))

st.sidebar.subheader("🗓️ Filtros de Dias")
so_fim_semana = st.sidebar.checkbox("Apenas Sextas, Sábados e Domingos")

dias_semana_opcoes = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo']
dias_selecionados = st.sidebar.multiselect("Dias da Semana Específicos:", dias_semana_opcoes, default=dias_semana_opcoes)

st.sidebar.subheader("🎯 Circunscrição & Unidades")
inspetorias_list = ["Todas"] + sorted(list(df_raw['inspetoria'].unique()))
selected_inspetoria = st.sidebar.selectbox("Inspetoria Regional", inspetorias_list)

coordenadorias_list = ["Todas"] + sorted(list(df_raw['coordenadoria'].unique()))
selected_coordenadoria = st.sidebar.selectbox("Coordenadoria Especializada", coordenadorias_list)

# APLICAÇÃO DOS FILTROS
df_filtered = df_raw.copy()
df_filtered = df_filtered[(df_filtered['data_hora'].dt.date >= start_date) & (df_filtered['data_hora'].dt.date <= end_date)]

# Filtro de Hora
if modo_hora == "Hora Específica":
    df_filtered = df_filtered[df_filtered['hora'] == hora_sel]
elif modo_hora == "Faixa Horária (Turno)":
    df_filtered = df_filtered[(df_filtered['hora'] >= hora_inicio) & (df_filtered['hora'] <= hora_fim)]

# Filtro de Fins de Semana e Dias da Semana
if so_fim_semana:
    df_filtered = df_filtered[df_filtered['fim_de_semana'] == True]

df_filtered = df_filtered[df_filtered['dia_semana'].isin(dias_selecionados)]

if selected_inspetoria != "Todas":
    df_filtered = df_filtered[df_filtered['inspetoria'] == selected_inspetoria]
if selected_coordenadoria != "Todas":
    df_filtered = df_filtered[df_filtered['coordenadoria'] == selected_coordenadoria]

# ==============================================================================
# CABEÇALHO
# ==============================================================================
head_col1, head_col2 = st.columns([1, 6])
with head_col1:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=90)
with head_col2:
    st.title("Sistema de Inteligência Operacional — BOGCM")
    st.markdown(f"<p style='color: {TEXTO_MUTED}; font-size: 1rem; margin-top: -10px;'>Guarda Civil Municipal de Niterói — Monitoramento Tático e Alocação de Efetivo</p>", unsafe_allow_html=True)

st.markdown("---")

if df_filtered.empty:
    st.warning("⚠️ Nenhuma ocorrência registrada para a combinação de filtros selecionada (Ajuste o horário ou período na barra lateral).")
    st.stop()

PLOTLY_TEMPLATE = "plotly_dark"

def layout_padrao(fig, **kwargs):
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color=TEXTO_CLARO, margin=dict(t=30, b=10, l=10, r=10), **kwargs)
    return fig

# ==============================================================================
# CARDS DE KPIS
# ==============================================================================
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

kpi1.metric("Total de BOGCM", f"{len(df_filtered):,}")
kpi2.metric("Abordagens PSR (CASS)", f"{df_filtered['psr_atendimentos'].sum():,}")
kpi3.metric("Equinos Resgatados", f"{df_filtered['equinos_resgatados'].sum():,}")
kpi4.metric("Fauna Silvestre", f"{df_filtered['animais_silvestres_resgatados'].sum():,}")
kpi5.metric("Chamados CISP 153", f"{len(df_filtered[df_filtered['origem'] == 'CISP 153']):,}")

st.markdown("<br>", unsafe_allow_html=True)

# ==============================================================================
# ABAS DE ANÁLISE
# ==============================================================================
tab_regional, tab_cass, tab_cma, tab_geo, tab_tabela = st.tabs([
    "📊 Produtividade por Regional",
    "👥 Abordagem Social (CASS / PSR)",
    "🍃 Coordenadoria de Meio Ambiente (CMA)",
    "🗺️ Mapeamento Espacial (Por Horário)",
    "📄 Relatório de Microdados"
])

with tab_regional:
    col_reg1, col_reg2 = st.columns(2)
    with col_reg1:
        st.subheader("Ocorrências por Inspetoria Regional")
        df_insp = df_filtered.groupby('inspetoria').size().reset_index(name='registros').sort_values('registros')
        fig_insp = px.bar(df_insp, x='registros', y='inspetoria', orientation='h', color='inspetoria', color_discrete_map=COLOR_INSPETORIAS, template=PLOTLY_TEMPLATE, text='registros')
        fig_insp.update_traces(textposition='outside')
        layout_padrao(fig_insp, xaxis_title="Registros", yaxis_title="", showlegend=False)
        st.plotly_chart(fig_insp, use_container_width=True)

    with col_reg2:
        st.subheader("Distribuição por Categoria de Ação")
        df_cat = df_filtered.groupby('categoria').size().reset_index(name='registros')
        fig_cat = px.pie(df_cat, values='registros', names='categoria', color_discrete_sequence=[GOLD_AMARELO, "#F59E0B", "#3B82F6", "#059669", "#EC4899", "#EF4444"], hole=0.4, template=PLOTLY_TEMPLATE)
        layout_padrao(fig_cat)
        st.plotly_chart(fig_cat, use_container_width=True)

    st.subheader("Distribuição do Volume de Ocorrências por Horário do Dia (0h - 23h)")
    df_hora_dist = df_filtered.groupby('hora').size().reset_index(name='registros')
    fig_hora = px.bar(df_hora_dist, x='hora', y='registros', color_discrete_sequence=[GOLD_AMARELO], template=PLOTLY_TEMPLATE)
    layout_padrao(fig_hora, xaxis_title="Hora do Dia", yaxis_title="Quantidade de Registros")
    st.plotly_chart(fig_hora, use_container_width=True)

with tab_cass:
    st.subheader("👥 Coordenadoria de Apoio ao Serviço Social (CASS) — Ações PSR")
    st.markdown("Monitoramento de abordagens humanizadas, acolhimento e ordenamento urbano relacionado a Pessoas em Situação de Rua em Niterói.")
    
    df_cass_data = df_filtered[df_filtered['coordenadoria'] == 'CASS']
    
    if not df_cass_data.empty:
        cass_col1, cass_col2 = st.columns(2)
        with cass_col1:
            st.markdown("#### Concentração de Atendimentos PSR por Bairro")
            df_cass_bairro = df_cass_data.groupby('bairro').size().reset_index(name='registros').sort_values('registros', ascending=True)
            fig_cass_b = px.bar(df_cass_bairro, x='registros', y='bairro', orientation='h', color_discrete_sequence=['#F59E0B'], template=PLOTLY_TEMPLATE, text='registros')
            fig_cass_b.update_traces(textposition='outside')
            layout_padrao(fig_cass_b, xaxis_title="Atendimentos", yaxis_title="")
            st.plotly_chart(fig_cass_b, use_container_width=True)
            
        with cass_col2:
            st.markdown("#### Tipologia de Ação de Apoio Social")
            df_cass_tipo = df_cass_data.groupby('tipo_ocorrencia').size().reset_index(name='registros')
            fig_cass_t = px.pie(df_cass_tipo, values='registros', names='tipo_ocorrencia', color_discrete_sequence=['#F59E0B', '#D97706', '#B45309'], hole=0.3, template=PLOTLY_TEMPLATE)
            layout_padrao(fig_cass_t)
            st.plotly_chart(fig_cass_t, use_container_width=True)
    else:
        st.info("Nenhuma ocorrência da CASS/PSR registrada para o filtro selecionado.")

with tab_cma:
    st.subheader("🍃 Coordenadoria de Meio Ambiente (CMA)")
    cma_col1, cma_col2 = st.columns(2)
    df_cma = df_filtered[df_filtered['coordenadoria'] == 'CMA']

    with cma_col1:
        st.markdown("#### Resgate de Fauna Silvestre por Bairro")
        df_fauna = df_cma.groupby('bairro')['animais_silvestres_resgatados'].sum().reset_index()
        df_fauna = df_fauna[df_fauna['animais_silvestres_resgatados'] > 0].sort_values('animais_silvestres_resgatados', ascending=True)
        fig_fauna = px.bar(df_fauna, x='animais_silvestres_resgatados', y='bairro', orientation='h', color_discrete_sequence=["#059669"], template=PLOTLY_TEMPLATE, text='animais_silvestres_resgatados')
        fig_fauna.update_traces(textposition='outside')
        layout_padrao(fig_fauna, xaxis_title="Animais Resgatados", yaxis_title="", showlegend=False)
        st.plotly_chart(fig_fauna, use_container_width=True)

    with cma_col2:
        st.markdown("#### Apreensão de Equinos por Inspetoria")
        df_equinos = df_cma.groupby('inspetoria')['equinos_resgatados'].sum().reset_index().sort_values('equinos_resgatados', ascending=True)
        fig_equinos = px.bar(df_equinos, x='equinos_resgatados', y='inspetoria', orientation='h', color='inspetoria', color_discrete_map=COLOR_INSPETORIAS, template=PLOTLY_TEMPLATE, text='equinos_resgatados')
        fig_equinos.update_traces(textposition='outside')
        layout_padrao(fig_equinos, xaxis_title="Equinos Apreendidos", yaxis_title="", showlegend=False)
        st.plotly_chart(fig_equinos, use_container_width=True)

with tab_geo:
    st.subheader("🗺️ Geoprocessamento — Alocação de Efetivo por Horário")
    if modo_hora == "Hora Específica":
        st.info(f"📍 Exibindo ocorrências ativas exclusivamente na faixa das **{hora_sel}h:00 às {hora_sel}h:59** ({len(df_filtered)} eventos).")
    elif modo_hora == "Faixa Horária (Turno)":
        st.info(f"📍 Exibindo ocorrências ativas no turno das **{hora_inicio}h:00 às {hora_fim}h:59** ({len(df_filtered)} eventos).")

    tipo_mapa = st.radio(
        "Modo de Visualização no Mapa:",
        ["Por Inspetoria Regional (Cores)", "Por Coordenadoria Especializada (Cores)", "Mancha de Calor (Heatmap)"],
        horizontal=True
    )

    if tipo_mapa == "Por Inspetoria Regional (Cores)":
        if hasattr(px, "scatter_map"):
            fig_map = px.scatter_map(df_filtered, lat='latitude', lon='longitude', color='inspetoria', color_discrete_map=COLOR_INSPETORIAS, zoom=11, center=dict(lat=-22.9000, lon=-43.0800), hover_name='tipo_ocorrencia', hover_data=['bairro', 'coordenadoria', 'hora'], map_style="carto-darkmatter", template=PLOTLY_TEMPLATE)
        else:
            fig_map = px.scatter_mapbox(df_filtered, lat='latitude', lon='longitude', color='inspetoria', color_discrete_map=COLOR_INSPETORIAS, zoom=11, center=dict(lat=-22.9000, lon=-43.0800), hover_name='tipo_ocorrencia', hover_data=['bairro', 'coordenadoria', 'hora'], mapbox_style="carto-darkmatter", template=PLOTLY_TEMPLATE)
    elif tipo_mapa == "Por Coordenadoria Especializada (Cores)":
        if hasattr(px, "scatter_map"):
            fig_map = px.scatter_map(df_filtered, lat='latitude', lon='longitude', color='coordenadoria', color_discrete_map=COLOR_COORDENADORIAS, zoom=11, center=dict(lat=-22.9000, lon=-43.0800), hover_name='tipo_ocorrencia', hover_data=['bairro', 'inspetoria', 'hora'], map_style="carto-darkmatter", template=PLOTLY_TEMPLATE)
        else:
            fig_map = px.scatter_mapbox(df_filtered, lat='latitude', lon='longitude', color='coordenadoria', color_discrete_map=COLOR_COORDENADORIAS, zoom=11, center=dict(lat=-22.9000, lon=-43.0800), hover_name='tipo_ocorrencia', hover_data=['bairro', 'inspetoria', 'hora'], mapbox_style="carto-darkmatter", template=PLOTLY_TEMPLATE)
    else:
        map_kwargs = dict(lat='latitude', lon='longitude', z=np.ones(len(df_filtered)), radius=14, center=dict(lat=-22.9000, lon=-43.0800), zoom=11, hover_name='tipo_ocorrencia', hover_data=['bairro', 'inspetoria', 'hora'])
        if hasattr(px, "density_map"):
            fig_map = px.density_map(df_filtered, map_style="carto-darkmatter", **map_kwargs)
        else:
            fig_map = px.density_mapbox(df_filtered, mapbox_style="carto-darkmatter", **map_kwargs)

    fig_map.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    st.plotly_chart(fig_map, use_container_width=True)

with tab_tabela:
    st.subheader("Base de Microdados Filtrada do BOGCM")
    st.dataframe(df_filtered[['id_bogcm', 'data_hora', 'hora', 'dia_semana', 'inspetoria', 'bairro', 'coordenadoria', 'tipo_ocorrencia', 'origem']], use_container_width=True)
    csv_bytes = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(label="📥 Exportar Dados para CSV", data=csv_bytes, file_name="relatorio_bogcm_niteroi.csv", mime="text/csv")