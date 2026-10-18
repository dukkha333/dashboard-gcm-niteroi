"""Painel do Observatório Municipal de Ordem Pública sobre o BOGCM.

Rodar:  streamlit run app.py
Dados:  coloque a exportação real em dados/bogcm.csv (ou .xlsx). Sem arquivo,
        o painel usa dados fictícios e avisa isso no topo.
"""
import html as _html
import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import dados
import indicadores as ind
from codigos import GRUPOS, OFFICIAL_CODES
from territorio import CENTRO_MAPA, rotulo_coordenadoria

st.set_page_config(
    page_title="BOGCM · Observatório Municipal de Ordem Pública",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================================================================
# TEMAS: o botão da barra lateral escolhe entre os dois. Para mudar cores, mexa só aqui.
# ==============================================================================
TEMAS = {
    "escuro": dict(
        papel="#0A1230",       # fundo da página: azul-marinho, não preto
        ficha="#111B42",       # superfícies em destaque (faixa de indicadores, tabelas)
        lateral="#0D1636",
        destaque="#F1C21B",    # dourado da Guarda: o que o gráfico quer que você veja
        dado="#6F8CE0",        # barras de dado comum
        nevoa="#4F64A8",       # barras sem destaque, ao lado de uma em destaque
        tinta="#E8EEFB", suave="#9AA8C7", linha="#26346A", alerta="#FF8A4C",
        sobre_destaque="#0A1230",   # texto sobre o dourado
        esquema="dark", mapa="carto-darkmatter",
        grupo={"100": "#F0625A", "200": "#F1A83B", "300": "#3FBF7F", "400": "#5AA2F5", "500": "#A58BE0"},
        inspetoria={
            "1ª Inspetoria (Centro)": "#E5B93C", "2ª Inspetoria (Icaraí)": "#5AA2F5",
            "3ª Inspetoria (São Francisco)": "#A58BE0", "4ª Inspetoria (Fonseca)": "#F0625A",
            "5ª Inspetoria (Oceânica)": "#3FBF7F", "Não mapeada": "#8A97B8",
        },
        categorias=["#5AA2F5", "#F1A83B", "#3FBF7F", "#A58BE0", "#F0625A",
                    "#4FC3C8", "#E58BC0", "#C9D45A", "#8A97B8", "#F29E7A"],
    ),
    "claro": dict(
        papel="#EAF0F8", ficha="#FFFFFF", lateral="#F6F8FC",
        destaque="#0B1B82", dado="#3E63D8", nevoa="#9DB0D6",
        tinta="#101B3F", suave="#566380", linha="#C9D5E8", alerta="#C2410C",
        sobre_destaque="#FFFFFF",
        esquema="light", mapa="carto-positron",
        grupo={"100": "#B3261E", "200": "#A66A00", "300": "#2F7D4F", "400": "#2563B8", "500": "#6B4FA3"},
        inspetoria={
            "1ª Inspetoria (Centro)": "#B07F00", "2ª Inspetoria (Icaraí)": "#3B82F6",
            "3ª Inspetoria (São Francisco)": "#8B5CF6", "4ª Inspetoria (Fonseca)": "#EF4444",
            "5ª Inspetoria (Oceânica)": "#10B981", "Não mapeada": "#94A3B8",
        },
        categorias=["#2563B8", "#B45309", "#2F7D4F", "#6B4FA3", "#B3261E",
                    "#0E7490", "#BE3A87", "#6B7A12", "#566380", "#C2570C"],
    ),
}


def _botao_tema() -> bool:
    """Botão no topo da barra lateral. Ligado = tema escuro."""
    try:
        return st.sidebar.toggle("Tema escuro", value=True)
    except AttributeError:  # Streamlit antigo, sem toggle
        return st.sidebar.checkbox("Tema escuro", value=True)


TEMA = TEMAS["escuro" if _botao_tema() else "claro"]
PAPEL, FICHA, LATERAL = TEMA["papel"], TEMA["ficha"], TEMA["lateral"]
DESTAQUE, DADO, NEVOA = TEMA["destaque"], TEMA["dado"], TEMA["nevoa"]
TINTA, SUAVE, LINHA, ALERTA = TEMA["tinta"], TEMA["suave"], TEMA["linha"], TEMA["alerta"]
COR_GRUPO, COR_INSPETORIA, CATEGORIAS = TEMA["grupo"], TEMA["inspetoria"], TEMA["categorias"]
ESTILO_MAPA = TEMA["mapa"]
AZUL = "#0B1B82"       # azul Niterói: faixa do cabeçalho, nos dois temas
OURO = "#F1C21B"       # filete do cabeçalho e selo de dados fictícios, nos dois temas
FONTE_TITULO = "'Barlow Condensed', 'Arial Narrow', sans-serif"
FONTE_TEXTO = "'Barlow', system-ui, -apple-system, 'Segoe UI', sans-serif"

DIAS_CURTOS = {"Segunda-feira": "seg", "Terça-feira": "ter", "Quarta-feira": "qua", "Quinta-feira": "qui",
               "Sexta-feira": "sex", "Sábado": "sáb", "Domingo": "dom"}

CSS_VARIAVEIS = (
    f":root{{color-scheme:{TEMA['esquema']};--papel:{PAPEL};--ficha:{FICHA};--lateral:{LATERAL};--azul:{AZUL};"
    f"--destaque:{DESTAQUE};--sobre-destaque:{TEMA['sobre_destaque']};--tinta:{TINTA};--suave:{SUAVE};"
    f"--nevoa:{NEVOA};--linha:{LINHA};--ouro:{OURO};--alerta:{ALERTA};"
    f"--f-titulo:{FONTE_TITULO};--f-texto:{FONTE_TEXTO};}}"
)

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600&family=Barlow+Condensed:wght@500;600;700&display=swap');
html, body, .stApp, [data-testid="stSidebar"] { font-family: var(--f-texto); color: var(--tinta); }
.stApp { background: var(--papel); }
header[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 1rem; padding-bottom: 3rem; max-width: 1280px; }
h1, h2, h3, h4, h5 { font-family: var(--f-titulo); color: var(--tinta); letter-spacing: 0; font-weight: 600; }
.stApp h4 { font-size: 1.35rem; margin: .4rem 0 .2rem; }
p, li, label, [data-testid="stCaptionContainer"] { font-size: 1rem; }
[data-testid="stCaptionContainer"] { color: var(--suave); }

/* barra lateral */
[data-testid="stSidebar"], [data-testid="stSidebarContent"] { background: var(--lateral); }
[data-testid="stSidebar"] { border-right: 1px solid var(--linha); }
[data-testid="stSidebar"] h3 { font-size: 1.25rem; margin: 1.1rem 0 .1rem; }
.lateral-nome { font-family: var(--f-titulo); font-size: 1.5rem; font-weight: 600; line-height: 1.05; margin: 0; }
.lateral-sub { color: var(--suave); font-size: .9rem; margin: .2rem 0 0; }
.lateral-fonte { color: var(--suave); font-size: .85rem; margin-top: 1.4rem; border-top: 1px solid var(--linha); padding-top: .7rem; }

/* cabeçalho */
.mast { background: var(--azul); color: #fff; padding: 1.1rem 1.5rem 1.2rem; border-bottom: 5px solid var(--ouro); margin-bottom: 1rem; }
.mast-topo { display: flex; justify-content: space-between; align-items: center; gap: 1rem; flex-wrap: wrap; }
.mast-org { font-size: .98rem; color: #D6DEF5; margin: 0; }
.mast h1 { color: #fff; font-size: clamp(1.8rem, 3.4vw, 2.6rem); line-height: 1.05; margin: .35rem 0 .25rem; padding: 0; }
.mast-sub { color: #D6DEF5; margin: 0; font-size: 1rem; }
.selo { font-size: .88rem; font-weight: 600; padding: .22rem .7rem; border-radius: 999px; white-space: nowrap; }
.selo-ficticio { background: var(--ouro); color: #0A1230; }
.selo-real { border: 1px solid #fff; color: #fff; }

/* faixa de indicadores */
.faixa { display: grid; grid-template-columns: repeat(4, 1fr); background: var(--ficha); border: 1px solid var(--linha); margin-bottom: 1.1rem; }
.faixa-item { padding: .9rem 1.2rem 1rem; border-left: 1px solid var(--linha); min-width: 0; }
.faixa-item:first-child { border-left: 0; }
.faixa-rotulo { font-size: .95rem; font-weight: 500; color: var(--suave); margin: 0; }
.faixa-valor { font-family: var(--f-titulo); font-size: 2.6rem; font-weight: 600; line-height: 1.05; margin: .1rem 0; color: var(--tinta); }
.faixa-nota { font-size: .88rem; color: var(--suave); margin: 0; line-height: 1.3; }
@media (max-width: 900px) {
  .faixa { grid-template-columns: repeat(2, 1fr); }
  .faixa-item:nth-child(3) { border-left: 0; }
  .faixa-item:nth-child(n+3) { border-top: 1px solid var(--linha); }
}

/* abas */
button[data-baseweb="tab"] { font-size: 1.02rem; font-weight: 500; color: var(--suave); }
button[data-baseweb="tab"][aria-selected="true"] { color: var(--destaque); font-weight: 600; }
div[data-baseweb="tab-highlight"] { background-color: var(--destaque); height: 3px; }
div[data-baseweb="tab-border"] { background-color: var(--linha); }

/* destaque: o achado em forma de título */
.st-key-destaque { background: var(--ficha); border: 1px solid var(--linha); border-top: 4px solid var(--destaque); padding: 1.2rem 1.5rem .6rem; margin-top: .6rem; }
.achado { font-family: var(--f-titulo); font-weight: 600; font-size: clamp(1.9rem, 4vw, 3rem); line-height: 1.05; margin: 0 0 .35rem; color: var(--tinta); }
.achado-sub { color: var(--suave); margin: 0 0 .4rem; max-width: 70ch; }

/* textos de método */
.fonte-bloco { border-left: 3px solid var(--destaque); padding: .1rem 0 .1rem 1rem; margin-bottom: 1rem; }
.fonte-bloco h4 { margin-top: 0; }
.fonte-bloco p { margin: .25rem 0; max-width: 62ch; }
.passos { list-style: none; counter-reset: passo; padding: 0; margin: .5rem 0 1rem; display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.2rem; }
.passos li { counter-increment: passo; border-top: 3px solid var(--destaque); padding-top: .5rem; font-size: .98rem; line-height: 1.35; }
.passos li::before { content: counter(passo); font-family: var(--f-titulo); font-size: 1.6rem; font-weight: 600; color: var(--destaque); display: block; line-height: 1; }
.passos b { display: block; font-family: var(--f-titulo); font-size: 1.25rem; font-weight: 600; margin: .2rem 0 .1rem; }
@media (max-width: 900px) { .passos { grid-template-columns: 1fr 1fr; } }
.efeito { color: var(--suave); font-size: .92rem; margin: 0; line-height: 1.35; }
.nota-alerta { color: var(--alerta); font-weight: 500; }

/* avisos próprios (não dependem do tema do Streamlit) */
.aviso { background: var(--ficha); border: 1px solid var(--linha); border-left: 4px solid var(--destaque); padding: .7rem 1rem; margin: .5rem 0; color: var(--tinta); }
.aviso-alerta { border-left-color: var(--alerta); }

/* tabelas próprias: seguem o tema escolhido no botão */
.tabela-wrap { max-height: 540px; overflow: auto; border: 1px solid var(--linha); background: var(--ficha); margin: .4rem 0 .8rem; }
.tabela-wrap table.tabela { width: 100%; border-collapse: collapse; font-size: .93rem; color: var(--tinta); background: transparent; }
.tabela-wrap table.tabela th { position: sticky; top: 0; background: var(--lateral); color: var(--tinta); text-align: left; font-weight: 600; padding: .55rem .8rem; border: 0; border-bottom: 2px solid var(--linha); white-space: nowrap; }
.tabela-wrap table.tabela td { padding: .45rem .8rem; border: 0; border-bottom: 1px solid var(--linha); vertical-align: top; color: var(--tinta); }
.tabela-wrap table.tabela tr:last-child td { border-bottom: 0; }
.tabela-wrap table.tabela .num { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
.tabela-wrap table.tabela .cod { font-family: var(--f-titulo); font-weight: 600; font-size: 1.1rem; white-space: nowrap; }
.barra { display: inline-block; vertical-align: middle; width: 90px; height: 8px; background: var(--linha); margin-right: .55rem; }
.barra > span { display: block; height: 100%; background: var(--destaque); }

/* widgets nativos seguem o tema do botão, não o do config.toml */
.stApp [data-testid="stWidgetLabel"] p, .stApp [data-testid="stWidgetLabel"] label,
.stApp [data-testid="stWidgetLabel"] span, .stApp .stCheckbox p, .stApp .stRadio p, .stApp .stToggle p { color: var(--tinta) !important; }
.stApp div[data-baseweb="select"] > div, .stApp div[data-baseweb="input"] > div,
.stApp div[data-baseweb="base-input"] { background: var(--ficha) !important; border-color: var(--linha) !important; }
.stApp div[data-baseweb="select"] *, .stApp input, .stApp textarea { color: var(--tinta) !important; -webkit-text-fill-color: var(--tinta); }
.stApp input::placeholder, .stApp textarea::placeholder { color: var(--suave) !important; -webkit-text-fill-color: var(--suave); opacity: 1; }
.stApp div[data-baseweb="select"] svg { fill: var(--suave) !important; }
.stApp span[data-baseweb="tag"] { background: var(--destaque) !important; }
.stApp span[data-baseweb="tag"], .stApp span[data-baseweb="tag"] * { color: var(--sobre-destaque) !important; -webkit-text-fill-color: var(--sobre-destaque); }
div[data-baseweb="popover"], div[data-baseweb="popover"] > div, div[data-baseweb="menu"], ul[role="listbox"] { background: var(--ficha) !important; color: var(--tinta) !important; }
li[role="option"], li[role="option"] * { color: var(--tinta) !important; -webkit-text-fill-color: var(--tinta); }
li[role="option"]:hover, li[role="option"][aria-selected="true"] { background: var(--linha) !important; }
div[data-baseweb="calendar"] { background: var(--ficha) !important; }
div[data-baseweb="calendar"] * { color: var(--tinta); }
.stApp [data-testid="stSliderThumbValue"], .stApp [data-testid="stTickBarMin"], .stApp [data-testid="stTickBarMax"] { color: var(--tinta) !important; }
button[data-testid="stBaseButton-pills"], button[kind="pills"] { background: var(--ficha) !important; border: 1px solid var(--linha) !important; }
button[data-testid="stBaseButton-pills"] *, button[kind="pills"] * { color: var(--tinta) !important; }
button[data-testid="stBaseButton-pillsActive"], button[kind="pillsActive"] { background: var(--destaque) !important; border: 1px solid var(--destaque) !important; }
button[data-testid="stBaseButton-pillsActive"] *, button[kind="pillsActive"] * { color: var(--sobre-destaque) !important; }
[data-testid="stDownloadButton"] button, .stDownloadButton button { background: var(--ficha) !important; border: 1px solid var(--linha) !important; }
[data-testid="stDownloadButton"] button *, .stDownloadButton button * { color: var(--tinta) !important; }
[data-testid="stHeader"] *, [data-testid="stToolbar"] * { color: var(--suave) !important; }
[data-testid="stHeader"] svg, [data-testid="stSidebarCollapseButton"] svg, [data-testid="stExpandSidebarButton"] svg { fill: var(--suave) !important; color: var(--suave) !important; }
"""
st.markdown(f"<style>{CSS_VARIAVEIS}{CSS}</style>", unsafe_allow_html=True)


# ==============================================================================
# FUNÇÕES DE APOIO
# ==============================================================================
def n_br(x) -> str:
    return f"{int(x):,}".replace(",", ".")


def p_br(x, casas: int = 1) -> str:
    return f"{x:.{casas}f}".replace(".", ",")


def mostrar(fig):
    """Desenha um gráfico Plotly. Funciona em versões do Streamlit com e sem `width`."""
    cfg = {"displayModeBar": False}
    try:
        st.plotly_chart(fig, use_container_width=True, theme=None, config=cfg)
    except Exception:  # versões novas removeram use_container_width
        st.plotly_chart(fig, width="stretch", theme=None, config=cfg)


def caixa_aviso(texto: str, tipo: str = "info"):
    """Aviso na cor do tema. tipo: 'info' ou 'alerta'."""
    classe = "aviso aviso-alerta" if tipo == "alerta" else "aviso"
    st.markdown(f'<div class="{classe}">{_html.escape(texto)}</div>', unsafe_allow_html=True)


def mostrar_tabela(df, barras=(), numericas=(), codigo=(), max_linhas=500):
    """Tabela HTML com o visual do painel (a tabela nativa não acompanha o botão de tema).

    barras: colunas de percentual (0 a 100) desenhadas como barra; numericas: inteiros
    alinhados à direita; codigo: colunas com o número do código em destaque.
    """
    colunas = list(df.columns)

    def classe(c):
        return ' class="num"' if (c in barras or c in numericas) else ""

    cabecalho = "".join(f"<th{classe(c)}>{_html.escape(str(c))}</th>" for c in colunas)
    linhas = []
    for valores in df.head(max_linhas).itertuples(index=False):
        celulas = []
        for c, v in zip(colunas, valores):
            vazio = v is None or (not isinstance(v, (list, tuple)) and bool(pd.isna(v)))
            if c in barras:
                if vazio:
                    celulas.append('<td class="num">—</td>')
                else:
                    larg = min(max(float(v), 0.0), 100.0)
                    celulas.append(f'<td class="num"><span class="barra"><span style="width:{larg:.1f}%"></span></span>'
                                   f'{p_br(float(v))}%</td>')
                continue
            if vazio:
                texto = "—"
            elif c in numericas:
                texto = n_br(v)
            elif isinstance(v, pd.Timestamp):
                texto = v.strftime("%d/%m/%Y %H:%M")
            elif isinstance(v, (bool,)) or type(v).__name__ == "bool_":
                texto = "Sim" if v else "Não"
            elif isinstance(v, float):
                texto = p_br(v)
            else:
                texto = str(v)
            atributo = classe(c) or (' class="cod"' if c in codigo else "")
            celulas.append(f"<td{atributo}>{_html.escape(texto)}</td>")
        linhas.append("<tr>" + "".join(celulas) + "</tr>")
    st.markdown(
        f'<div class="tabela-wrap"><table class="tabela"><thead><tr>{cabecalho}</tr></thead>'
        f'<tbody>{"".join(linhas)}</tbody></table></div>',
        unsafe_allow_html=True,
    )


def seletor_multiplo(rotulo, opcoes, formato=str):
    """Botões de seleção múltipla (pills); em versões sem pills, cai para multiselect."""
    try:
        escolha = st.pills(rotulo, opcoes, selection_mode="multi", format_func=formato, label_visibility="collapsed")
    except Exception:
        escolha = st.multiselect(rotulo, opcoes, format_func=formato, placeholder="Todas", label_visibility="collapsed")
    return list(escolha or [])


def estilo(fig, altura=320, **kw):
    kw.setdefault("showlegend", False)
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=altura,
        font=dict(family="Barlow, system-ui, sans-serif", size=14, color=TINTA),
        margin=dict(t=10, b=10, l=10, r=10),
        hoverlabel=dict(bgcolor=FICHA, bordercolor=LINHA, font=dict(family="Barlow, system-ui, sans-serif", color=TINTA)), **kw,
    )
    # automargin: o eixo abre espaço para rótulos longos em vez de cortá-los na borda
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor=LINHA, tickfont=dict(color=SUAVE), automargin=True)
    fig.update_yaxes(gridcolor=LINHA, zeroline=False, tickfont=dict(color=SUAVE), automargin=True)
    return fig


def barras_h(rotulos, valores, textos, cores, altura):
    """Barras horizontais com a maior no topo, valor ao lado e sem eixo."""
    fig = go.Figure(go.Bar(
        y=list(rotulos)[::-1], x=list(valores)[::-1], orientation="h", marker_color=list(cores)[::-1],
        text=list(textos)[::-1], textposition="outside", cliponaxis=False,
        hovertemplate="%{y}: %{x} boletins<extra></extra>",
    ))
    estilo(fig, altura=altura)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(gridcolor="rgba(0,0,0,0)")
    return fig


def rosca(rotulos, valores, cores, altura=280):
    """Pizza com furo no meio: o total fica no centro e o percentual de cada fatia, na legenda."""
    rotulos, valores = list(rotulos), [float(v) for v in valores]
    total = sum(valores) or 1.0
    legenda = [f"{r}   {p_br(v / total * 100, 0)}%" for r, v in zip(rotulos, valores)]
    fig = go.Figure(go.Pie(
        labels=legenda, values=valores, hole=0.6, sort=False, direction="clockwise",
        marker=dict(colors=list(cores), line=dict(color=PAPEL, width=2)),
        textinfo="none", domain=dict(x=[0, 0.5], y=[0, 1]),
        hovertemplate="%{label}<br>%{value} boletins<extra></extra>",
    ))
    estilo(fig, altura=altura, showlegend=True,
           legend=dict(x=0.54, y=0.5, xanchor="left", yanchor="middle", font=dict(size=13, color=TINTA)))
    fig.update_layout(annotations=[dict(
        text=f"<b>{n_br(total)}</b>", x=0.25, y=0.5, showarrow=False,
        font=dict(size=24, color=TINTA, family="Barlow Condensed, Barlow, sans-serif"),
    )])
    return fig


def container_destaque():
    try:
        return st.container(key="destaque")
    except TypeError:  # Streamlit antigo: sem key, só perde o painel de destaque
        return st.container()


def faixa_item(rotulo, valor, nota):
    return (f'<div class="faixa-item"><p class="faixa-rotulo">{rotulo}</p>'
            f'<p class="faixa-valor">{valor}</p><p class="faixa-nota">{nota}</p></div>')


# ==============================================================================
# DADOS
# ==============================================================================
@st.cache_data(show_spinner="Carregando boletins...")
def carregar(assinatura: str):
    return dados.carregar_dados()


try:
    df_raw, meta = carregar(dados.assinatura_fonte())
except ValueError as erro:
    st.error(f"Não foi possível carregar o arquivo de boletins. {erro}")
    st.stop()

e_real = meta["origem"] == "real"
data_min, data_max = df_raw["data_hora"].min().date(), df_raw["data_hora"].max().date()

# ==============================================================================
# FILTROS (barra lateral)
# ==============================================================================
sb = st.sidebar
if os.path.exists("logo.png"):
    sb.image("logo.png", width=110)
sb.markdown('<p class="lateral-nome">Guarda Civil Municipal de Niterói</p>'
            '<p class="lateral-sub">Secretaria Municipal de Ordem Pública</p>', unsafe_allow_html=True)

sb.subheader("Período")
atalho = sb.selectbox(
    "Período", ["Último mês com dados", "Últimos 3 meses", "Ano corrente", "Todo o período", "Escolher datas"],
    label_visibility="collapsed",
)
ultimo = pd.Timestamp(data_max)
if atalho == "Último mês com dados":
    inicio, fim = ultimo.replace(day=1).date(), data_max
elif atalho == "Últimos 3 meses":
    inicio, fim = (ultimo.replace(day=1) - pd.DateOffset(months=2)).date(), data_max
elif atalho == "Ano corrente":
    inicio, fim = ultimo.replace(month=1, day=1).date(), data_max
elif atalho == "Todo o período":
    inicio, fim = data_min, data_max
else:
    escolha = sb.date_input("Datas", value=(data_min, data_max), min_value=data_min, max_value=data_max,
                            format="DD/MM/YYYY")
    if isinstance(escolha, (list, tuple)) and len(escolha) == 2:
        inicio, fim = escolha
    else:
        inicio = fim = escolha[0] if isinstance(escolha, (list, tuple)) else escolha

sb.subheader("Horário e dias")
hora_ini, hora_fim = sb.select_slider(
    "Faixa de hora da ocorrência", options=list(range(24)), value=(0, 23), format_func=lambda h: f"{h:02d}h"
)
dias_sel = sb.multiselect("Dias da semana", dados.DIAS_PT, placeholder="Todos os dias")
so_fim_semana = sb.checkbox("Apenas sexta, sábado e domingo")

sb.subheader("Coordenadoria")
ordem_coord = df_raw["servico"].value_counts().index.tolist()
servicos_sel = sb.multiselect(
    "Coordenadoria ou serviço", ordem_coord, format_func=rotulo_coordenadoria,
    placeholder="Todas as coordenadorias",
)

sb.subheader("Onde")
inspetorias = sorted(df_raw["inspetoria"].unique())
insp_sel = sb.selectbox("Inspetoria", ["Todas"] + inspetorias)
bairros_disp = sorted(df_raw.loc[df_raw["inspetoria"] == insp_sel, "bairro"].unique()) if insp_sel != "Todas" \
    else sorted(df_raw["bairro"].unique())
bairros_sel = sb.multiselect("Bairros", bairros_disp, placeholder="Todos os bairros")

sb.subheader("O quê")
grupos_disp = sorted(df_raw["grupo"].unique())
grupos_sel = sb.multiselect("Grupo de ocorrência", grupos_disp, placeholder="Todos os grupos")
codigos_disp = sorted(
    df_raw.loc[df_raw["grupo"].isin(grupos_sel) if grupos_sel else slice(None), ["codigo", "ocorrencia"]]
    .drop_duplicates().itertuples(index=False, name=None)
)
codigos_sel = sb.multiselect("Código", [c for c, _ in codigos_disp],
                             format_func=lambda c: f"{c} - {dict(codigos_disp).get(c, '')}",
                             placeholder="Todos os códigos")

sb.markdown(
    f'<p class="lateral-fonte">{"Fonte: " + meta["arquivo"] if e_real else "Fonte: dados fictícios gerados por data_generator.py"}'
    f'<br>{n_br(len(df_raw))} boletins na base, de {data_min:%d/%m/%Y} a {data_max:%d/%m/%Y}.</p>',
    unsafe_allow_html=True,
)

# --- aplicação dos filtros: df_base ignora o período (serve para comparar com o ano anterior)
df_base = df_raw
df_base = df_base[df_base["hora"].between(hora_ini, hora_fim)]
if dias_sel:
    df_base = df_base[df_base["dia_semana"].isin(dias_sel)]
if so_fim_semana:
    df_base = df_base[df_base["fim_de_semana"]]
if insp_sel != "Todas":
    df_base = df_base[df_base["inspetoria"] == insp_sel]
if bairros_sel:
    df_base = df_base[df_base["bairro"].isin(bairros_sel)]
if servicos_sel:
    df_base = df_base[df_base["servico"].isin(servicos_sel)]
if grupos_sel:
    df_base = df_base[df_base["grupo"].isin(grupos_sel)]
if codigos_sel:
    df_base = df_base[df_base["codigo"].isin(codigos_sel)]

ts_ini = pd.Timestamp(inicio)
ts_fim = pd.Timestamp(fim) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
df_f = df_base[df_base["data_hora"].between(ts_ini, ts_fim)]
n = len(df_f)

# ==============================================================================
# CABEÇALHO E FAIXA DE INDICADORES
# ==============================================================================
selo = (f'<span class="selo selo-real">Dados reais: {meta["arquivo"]}</span>' if e_real
        else '<span class="selo selo-ficticio">Dados fictícios para demonstração</span>')
st.markdown(
    '<div class="mast"><div class="mast-topo">'
    '<p class="mast-org">Observatório Municipal de Ordem Pública, SEOP Niterói</p>' + selo + '</div>'
    '<h1>Boletins de Ocorrência da Guarda Civil Municipal</h1>'
    f'<p class="mast-sub">{n_br(n)} boletins de {inicio:%d/%m/%Y} a {fim:%d/%m/%Y}</p></div>',
    unsafe_allow_html=True,
)

for aviso in meta["avisos"]:
    caixa_aviso(aviso, 'alerta')

if n == 0:
    caixa_aviso("Nenhum boletim com esses filtros. Amplie o período ou limpe o filtro de hora ou de código na barra lateral.")
    st.stop()

comp = ind.comparativo_ano(df_base, ts_ini, ts_fim)
if comp["tem_base"]:
    sinal = "+" if comp["variacao"] >= 0 else "−"
    item_ano = faixa_item("Contra o mesmo período do ano anterior", f'{sinal}{p_br(abs(comp["variacao"]), 0)}%',
                          f'{n_br(comp["anterior"])} boletins em {ts_ini.year - 1}')
else:
    item_ano = faixa_item("Contra o mesmo período do ano anterior", "sem base",
                          "A base não cobre o mesmo período de um ano antes.")

origem_conducao = meta["conducao_origem"]
if origem_conducao == "indisponivel":
    item_conducao = faixa_item("Conduções e prisões", "sem dado", "A base não traz o campo nem o texto do relato.")
else:
    qtd = int(df_f["conducao_prisao"].fillna(False).sum())
    nota = "Marcadas no boletim." if origem_conducao == "campo" else "Estimativa a partir do texto do relato."
    item_conducao = faixa_item("Conduções e prisões", n_br(qtd), nota)

st.markdown(
    '<div class="faixa">'
    + faixa_item("Boletins no período", n_br(n), f"{inicio:%d/%m/%Y} a {fim:%d/%m/%Y}")
    + item_ano + item_conducao
    + faixa_item("Registrados como “Outros”", f'{p_br(ind.pct_outros(df_f))}%',
                 "Os códigos 150, 250, 350, 450 e 550 devem ser exceção.")
    + '</div>',
    unsafe_allow_html=True,
)

# ==============================================================================
# ABAS
# ==============================================================================
tab_pan, tab_nat, tab_coord, tab_ter, tab_qual, tab_cod, tab_micro = st.tabs(
    ["Panorama", "Natureza", "Coordenadorias", "Território", "Qualidade do registro", "Códigos e método", "Microdados"]
)

# ------------------------------------------------------------------ PANORAMA
with tab_pan:
    pico = ind.janela_pico(df_f)
    filtro_de_hora = (hora_ini, hora_fim) != (0, 23)
    with container_destaque():
        if filtro_de_hora:
            st.markdown(f'<p class="achado">{n_br(n)} boletins entre as {hora_ini}h e as {hora_fim}h59</p>'
                        '<p class="achado-sub">A faixa de hora está filtrada na barra lateral. '
                        'Volte para 00h a 23h para ver onde a demanda se concentra no dia.</p>',
                        unsafe_allow_html=True)
        else:
            seg = ind.segundo_pico(df_f, pico)
            extra = f" Um segundo pico aparece às {seg}h." if seg is not None else ""
            st.markdown(
                f'<p class="achado">{p_br(pico["pct"], 0)}% dos boletins foram registrados entre as '
                f'{pico["inicio"]}h e as {pico["fim"]}h59</p>'
                f'<p class="achado-sub">{n_br(pico["boletins"])} de {n_br(n)} boletins, pela hora da ocorrência.{extra} '
                'Use para dimensionar a escala do efetivo e o planejamento do patrulhamento.</p>',
                unsafe_allow_html=True,
            )
        por_hora = ind.contagem_por_hora(df_f)
        em_destaque = set(range(pico["inicio"], pico["fim"] + 1)) if (pico and not filtro_de_hora) else set()
        fig = go.Figure(go.Bar(
            x=[f"{h:02d}h" for h in por_hora.index], y=por_hora.values,
            marker_color=[DESTAQUE if h in em_destaque else NEVOA for h in por_hora.index],
            hovertemplate="%{x}: %{y} boletins<extra></extra>",
        ))
        estilo(fig, altura=330, bargap=0.18)
        fig.update_xaxes(tickangle=0, tickmode="array", tickvals=[f"{h:02d}h" for h in range(0, 24, 3)])
        mostrar(fig)

    col_mes, col_dia = st.columns([3, 2], gap="large")
    with col_mes:
        st.markdown("#### Boletins por mês, ano contra ano")
        mensal = ind.mensal_por_ano(df_base)
        if mensal.empty:
            st.caption("Sem dados para comparar.")
        else:
            fig = go.Figure()
            anos = list(mensal.columns)
            for i, ano in enumerate(anos):
                atual = i == len(anos) - 1
                fig.add_trace(go.Scatter(
                    x=ind.MESES_ABREV, y=mensal[ano], name=str(ano), mode="lines+markers",
                    line=dict(color=DESTAQUE if atual else NEVOA, width=3 if atual else 2.5),
                    marker=dict(size=7), connectgaps=False,
                    hovertemplate=f"%{{x}}/{ano}: %{{y:,.0f}} boletins<extra></extra>",
                ))
            estilo(fig, altura=300, showlegend=True, legend=dict(orientation="h", y=1.12, x=0))
            mostrar(fig)
        st.caption("Mais boletins pode significar mais presença e mais registro, não necessariamente mais ocorrências.")

    with col_dia:
        st.markdown("#### Dia da semana")
        por_dia = df_f["dia_semana"].value_counts().reindex(dados.DIAS_PT, fill_value=0)
        maior = por_dia.idxmax()
        fig = go.Figure(go.Bar(
            x=[DIAS_CURTOS[d] for d in por_dia.index], y=por_dia.values,
            marker_color=[DESTAQUE if d == maior else NEVOA for d in por_dia.index],
            text=[n_br(v) for v in por_dia.values], textposition="outside", cliponaxis=False,
            hovertemplate="%{x}: %{y} boletins<extra></extra>",
        ))
        estilo(fig, altura=300, bargap=0.25)
        fig.update_yaxes(visible=False)
        mostrar(fig)

    st.markdown("#### Por turno do dia")
    turnos = [("Madrugada (0h–5h59)", range(0, 6)), ("Manhã (6h–11h59)", range(6, 12)),
              ("Tarde (12h–17h59)", range(12, 18)), ("Noite (18h–23h59)", range(18, 24))]
    por_hora_t = ind.contagem_por_hora(df_f)
    vals_t = [int(por_hora_t.loc[list(r)].sum()) for _, r in turnos]
    col_t, col_tn = st.columns([3, 2], gap="large")
    with col_t:
        mostrar(rosca([t for t, _ in turnos], vals_t, [CATEGORIAS[3], CATEGORIAS[1], CATEGORIAS[0], CATEGORIAS[8]], altura=250))
    with col_tn:
        mais = max(range(4), key=lambda i: vals_t[i])
        st.markdown(f'<p class="faixa-valor">{turnos[mais][0].split(" (")[0]}</p>'
                    f'<p class="faixa-nota">é o turno com mais boletins, {p_br(vals_t[mais] / max(sum(vals_t), 1) * 100, 0)}% do total do filtro.</p>',
                    unsafe_allow_html=True)

# ------------------------------------------------------------------ NATUREZA
with tab_nat:
    col_g, col_p = st.columns([2, 3], gap="large")
    with col_g:
        st.markdown("#### Por grupo de ocorrência")
        g = ind.por_grupo(df_f)
        mostrar(rosca([f"{c} {nm}" for c, nm in zip(g["grupo_cod"], g["grupo"])], g["boletins"],
                      [COR_GRUPO.get(c, NEVOA) for c in g["grupo_cod"]], altura=300))

    with col_p:
        st.markdown("#### Códigos mais registrados")
        par = ind.pareto_codigos(df_f, n=10)
        rotulos = [f'{c}  {o if len(o) <= 34 else o[:33] + "…"}' for c, o in zip(par["codigo"], par["ocorrencia"])]
        fig = go.Figure(go.Bar(
            y=rotulos[::-1], x=par["boletins"][::-1], orientation="h",
            marker_color=[ALERTA if o else DADO for o in par["e_outros"][::-1]],
            text=[f"{p_br(p)}%" for p in par["pct"][::-1]], textposition="outside", cliponaxis=False,
            hovertemplate="%{y}: %{x} boletins<extra></extra>",
        ))
        estilo(fig, altura=380)
        fig.update_xaxes(visible=False)
        fig.update_yaxes(gridcolor="rgba(0,0,0,0)")
        mostrar(fig)
        st.caption(f"Os {len(par)} códigos mais registrados somam {p_br(par['acumulado'].iloc[-1], 0)}% dos boletins. "
                   "Em laranja, os códigos “Outros”.")

    st.markdown("---")
    col_f, col_j = st.columns(2, gap="large")
    with col_f:
        st.markdown("#### Furto, por tipo")
        furto = ind.furto_por_tipo(df_f)
        if furto.empty:
            st.caption("Nenhum boletim de furto (106) com tipo informado neste filtro.")
        else:
            mostrar(rosca(furto.index, furto.values, CATEGORIAS[:len(furto)], altura=260))
            st.caption("Pergunta complementar que o formulário abre quando o código é 106.")
    with col_j:
        st.markdown("#### Situação com a Justiça")
        q507 = int((df_f["codigo"] == "507").sum())
        st.markdown(f'<p class="faixa-valor">{n_br(q507)}</p>'
                    '<p class="faixa-nota">boletins com código 507, indivíduos em situação ilegal com a Justiça.</p>',
                    unsafe_allow_html=True)

# ------------------------------------------------------------------ COORDENADORIAS
with tab_coord:
    st.markdown("#### Boletins por coordenadoria ou serviço")
    st.caption("O comprimento é o volume. A cor é o grupo de ocorrência: mostra o que cada coordenadoria atende.")
    tc, ordem_c = ind.por_coordenadoria(df_f)
    rotulos_c = list(ordem_c)[::-1]
    col_cb, col_cp = st.columns([3, 2], gap="large")
    fig = go.Figure()
    for cod_g, nome_g in GRUPOS.items():
        sub_g = tc[tc["grupo_cod"] == cod_g].set_index("servico")["boletins"].reindex(ordem_c, fill_value=0)
        fig.add_trace(go.Bar(
            y=rotulos_c, x=sub_g.values[::-1], orientation="h", name=f"{cod_g} - {nome_g}",
            marker_color=COR_GRUPO[cod_g],
            hovertemplate="%{y}, " + f"{cod_g} - {nome_g}" + ": %{x} boletins<extra></extra>",
        ))
    totais = df_f["servico"].value_counts().reindex(ordem_c)
    fig.add_trace(go.Scatter(
        y=rotulos_c, x=totais.values[::-1], mode="text", text=[n_br(v) for v in totais.values[::-1]],
        textposition="middle right", showlegend=False, hoverinfo="skip",
    ))
    estilo(fig, altura=max(280, 44 * len(ordem_c) + 90), barmode="stack", showlegend=True, bargap=0.3,
           legend=dict(orientation="h", y=1.12, x=0, font=dict(color=TINTA)))
    fig.update_xaxes(visible=False, range=[0, float(totais.max()) * 1.15])
    fig.update_yaxes(gridcolor="rgba(0,0,0,0)")
    with col_cb:
        mostrar(fig)
    with col_cp:
        st.markdown("##### Participação no total")
        mostrar(rosca([rotulo_coordenadoria(c) for c in ordem_c], totais.values,
                      [CATEGORIAS[i % len(CATEGORIAS)] for i in range(len(ordem_c))],
                      altura=max(280, 44 * len(ordem_c) + 90)))

    st.markdown("#### Detalhe de uma coordenadoria")
    escolha_c = st.selectbox("Escolha a coordenadoria", ordem_c, format_func=rotulo_coordenadoria,
                             label_visibility="collapsed")
    rc = ind.resumo_coordenadoria(df_f, escolha_c)
    top_c = ind.pareto_codigos(rc["sub"], n=8)
    pico_c = rc["pico"]
    st.markdown(
        '<div class="faixa">'
        + faixa_item("Boletins", n_br(rc["boletins"]), f'{p_br(rc["pct_total"])}% do total do filtro')
        + faixa_item("Horário de pico", f'{pico_c["inicio"]}h às {pico_c["fim"]}h59' if pico_c else "sem dado",
                     f'{p_br(pico_c["pct"], 0)}% dos boletins da coordenadoria' if pico_c else "")
        + faixa_item("Código mais registrado", top_c["codigo"].iloc[0] if len(top_c) else "sem dado",
                     top_c["ocorrencia"].iloc[0] if len(top_c) else "")
        + faixa_item("Registrados como “Outros”", f'{p_br(rc["pct_outros"])}%',
                     "Os códigos 150, 250, 350, 450 e 550 devem ser exceção.")
        + '</div>',
        unsafe_allow_html=True,
    )

    cc1, cc2 = st.columns(2, gap="large")
    with cc1:
        st.markdown("#### Códigos mais registrados")
        if len(top_c):
            nomes = [f'{c}  {o if len(o) <= 34 else o[:33] + "…"}' for c, o in zip(top_c["codigo"], top_c["ocorrencia"])]
            mostrar(barras_h(nomes, top_c["boletins"], [f"{p_br(p)}%" for p in top_c["pct"]],
                             [ALERTA if o else DADO for o in top_c["e_outros"]], altura=340))
    with cc2:
        st.markdown("#### Bairros com mais boletins")
        bt = rc["sub"].groupby("bairro").size().sort_values(ascending=False).head(8)
        mostrar(barras_h(bt.index, bt.values, [n_br(v) for v in bt.values], [DADO] * len(bt), altura=340))

    st.markdown("#### Boletins por hora do dia")
    por_hora_c = ind.contagem_por_hora(rc["sub"])
    destaque_c = set(range(pico_c["inicio"], pico_c["fim"] + 1)) if pico_c else set()
    fig = go.Figure(go.Bar(
        x=[f"{h:02d}h" for h in por_hora_c.index], y=por_hora_c.values,
        marker_color=[DESTAQUE if h in destaque_c else NEVOA for h in por_hora_c.index],
        hovertemplate="%{x}: %{y} boletins<extra></extra>",
    ))
    estilo(fig, altura=240, bargap=0.18)
    fig.update_xaxes(tickmode="array", tickvals=[f"{h:02d}h" for h in range(0, 24, 3)])
    mostrar(fig)
    st.caption("Em dourado, a janela de 3 horas seguidas com mais boletins desta coordenadoria.")

# ------------------------------------------------------------------ TERRITÓRIO
with tab_ter:
    st.markdown("#### Filtrar o mapa por inspetoria")
    insp_disp = sorted(df_f["inspetoria"].unique())
    insp_mapa = seletor_multiplo("Inspetorias no mapa", insp_disp)
    df_t = df_f[df_f["inspetoria"].isin(insp_mapa)] if insp_mapa else df_f
    n_t = len(df_t)
    if insp_mapa:
        st.caption(f"Mapa, gráficos e bairros abaixo mostram {n_br(n_t)} boletins de: {', '.join(insp_mapa)}. "
                   "Sem nenhuma selecionada, aparecem todas.")
    else:
        st.caption("Nenhuma inspetoria selecionada: o mapa mostra todas. Clique em uma ou mais para isolar.")

    modo = st.radio("Como mostrar", ["Pontos por grupo", "Pontos por inspetoria", "Pontos por coordenadoria", "Mancha de calor"],
                    horizontal=True, label_visibility="collapsed")
    no_mapa = df_t[df_t["pino_valido"]]
    sem_pino = n_t - len(no_mapa)

    col_mapa, col_bairro = st.columns([3, 2], gap="large")
    with col_mapa:
        if no_mapa.empty:
            caixa_aviso("Nenhum boletim com pino válido neste filtro.")
        else:
            if insp_mapa:  # aproxima da área escolhida
                centro = {"lat": float(no_mapa["latitude"].mean()), "lon": float(no_mapa["longitude"].mean())}
                zoom = 12.3 if len(insp_mapa) == 1 else 11.6
            else:
                centro, zoom = CENTRO_MAPA, 11
            comum = dict(lat="latitude", lon="longitude", zoom=zoom, center=centro,
                         hover_name="ocorrencia", hover_data={"bairro": True, "hora": True, "latitude": False, "longitude": False})
            if modo != "Mancha de calor":
                amostra = no_mapa if len(no_mapa) <= 6000 else no_mapa.sample(6000, random_state=1)
                if modo == "Pontos por grupo":
                    cores = {f"{k} - {v}": COR_GRUPO[k] for k, v in GRUPOS.items()}
                    args = dict(color="grupo", color_discrete_map=cores, **comum)
                elif modo == "Pontos por inspetoria":
                    args = dict(color="inspetoria", color_discrete_map=COR_INSPETORIA,
                                category_orders={"inspetoria": list(COR_INSPETORIA)}, **comum)
                else:
                    args = dict(color="servico", color_discrete_sequence=CATEGORIAS,
                                category_orders={"servico": ordem_coord}, **comum)
                if hasattr(px, "scatter_map"):
                    fig = px.scatter_map(amostra, map_style=ESTILO_MAPA, **args)
                else:
                    fig = px.scatter_mapbox(amostra, mapbox_style=ESTILO_MAPA, **args)
                fig.update_traces(marker=dict(size=7, opacity=0.8))
                fig.update_layout(legend=dict(orientation="h", y=-0.02, title_text="", font=dict(color=TINTA)))
                if len(no_mapa) > 6000:
                    st.caption(f"Mostrando 6.000 de {n_br(len(no_mapa))} pontos, sorteados.")
            else:
                args = dict(z=[1] * len(no_mapa), radius=14, color_continuous_scale="YlOrRd", **comum)
                if hasattr(px, "density_map"):
                    fig = px.density_map(no_mapa, map_style=ESTILO_MAPA, **args)
                else:
                    fig = px.density_mapbox(no_mapa, mapbox_style=ESTILO_MAPA, **args)
                fig.update_coloraxes(showscale=False)
            fig.update_layout(margin=dict(r=0, t=0, l=0, b=0), height=520, paper_bgcolor="rgba(0,0,0,0)",
                              font=dict(family="Barlow, system-ui, sans-serif", color=TINTA))
            mostrar(fig)
        if sem_pino and n_t:
            st.caption(f"{n_br(sem_pino)} boletins ({p_br(sem_pino / n_t * 100)}%) estão sem pino válido e não aparecem no mapa. "
                       "Pino errado, mapa errado.")

    with col_bairro:
        st.markdown("#### Bairros com mais boletins")
        top = (df_t.groupby(["bairro", "inspetoria"]).size().reset_index(name="boletins")
               .sort_values("boletins", ascending=False).head(10))
        fig = go.Figure(go.Bar(
            y=top["bairro"][::-1], x=top["boletins"][::-1], orientation="h",
            marker_color=[COR_INSPETORIA.get(i, NEVOA) for i in top["inspetoria"][::-1]],
            text=[n_br(v) for v in top["boletins"][::-1]], textposition="outside", cliponaxis=False,
            customdata=top["inspetoria"][::-1], hovertemplate="%{y} (%{customdata}): %{x} boletins<extra></extra>",
        ))
        estilo(fig, altura=320)
        fig.update_xaxes(visible=False)
        fig.update_yaxes(gridcolor="rgba(0,0,0,0)")
        mostrar(fig)
        st.markdown("#### Por inspetoria")
        pi = df_t["inspetoria"].value_counts().reindex([i for i in COR_INSPETORIA if i in set(df_t["inspetoria"])])
        mostrar(rosca(pi.index, pi.values, [COR_INSPETORIA[i] for i in pi.index], altura=240))

# ------------------------------------------------------------------ QUALIDADE
with tab_qual:
    st.markdown("#### Erros de preenchimento que distorcem os indicadores")
    st.caption("Calculado sobre os boletins do filtro atual. Cada item mostra o efeito no indicador, como na aula do OMOP.")
    q = ind.qualidade(df_f)

    def item_q(rotulo, valor, efeito):
        texto = "indisponível" if valor is None else f"{p_br(valor)}%"
        return faixa_item(rotulo, texto, efeito)

    st.markdown(
        '<div class="faixa">'
        + item_q("Código “Outros”", q["outros"], "O fato some do indicador específico e infla a categoria genérica.")
        + item_q("Sem pino válido", q["sem_pino"], "O ponto vai para o lugar errado do mapa e desvia o patrulhamento.")
        + item_q("Registrado em outro dia", q["dia_diferente"], "O balanço mensal usa a data de criação do boletim. Registre no mesmo dia.")
        + item_q("Relato curto ou genérico", q["relato_fraco"], "Conduções e prisões deixam de ser contadas.")
        + '</div>',
        unsafe_allow_html=True,
    )
    if q["relato_fraco"] is None:
        st.caption("O relato não está na base carregada, então este indicador não pode ser calculado. "
                   "Se o arquivo real trouxer a coluna do relato, ele passa a aparecer sozinho.")

    st.markdown("#### Por coordenadoria ou serviço")
    por_servico = ind.qualidade_por_servico(df_f)
    if por_servico.empty or (por_servico["servico"] == "Não informado").all():
        st.caption("Não há coordenadorias ou serviços com boletins suficientes (mínimo de 30) para comparar.")
    else:
        mostrar_tab = por_servico.rename(columns={
            "servico": "Coordenadoria / serviço", "boletins": "Boletins", "pct_outros": "Código “Outros”",
            "pct_sem_pino": "Sem pino válido", "pct_dia_diferente": "Registrado em outro dia",
            "pct_relato_fraco": "Relato curto ou genérico",
        })
        vazias = [c for c in mostrar_tab.columns[2:] if mostrar_tab[c].isna().all()]
        mostrar_tabela(mostrar_tab.drop(columns=vazias), barras=[c for c in mostrar_tab.columns[2:] if c not in vazias],
                       numericas=["Boletins"])
        st.caption("Ordenado por uso do código “Outros”. Serve para saber onde reforçar a orientação, não para ranquear guardas.")

# ------------------------------------------------------------------ CÓDIGOS E MÉTODO
with tab_cod:
    st.markdown("#### Dicionário oficial de códigos")
    st.caption("39 códigos em 5 grupos. Na dúvida, descreva no relato e use o código “Outros” do grupo.")
    c1, c2 = st.columns([2, 1])
    busca = c1.text_input("Buscar por código ou palavra", placeholder="Ex.: 106, furto, animal")
    grupo_dic = c2.selectbox("Grupo", ["Todos"] + [f"{k} - {v}" for k, v in GRUPOS.items()])
    termo = busca.strip().lower()
    linhas = [
        {"Código": c["codigo"], "Ocorrência": c["nome"], "Grupo": c["grupo"], "Como preencher": c["guia"]}
        for c in OFFICIAL_CODES
        if (grupo_dic == "Todos" or c["grupo"] == grupo_dic)
        and (not termo or termo in c["codigo"] or termo in c["nome"].lower() or termo in c["guia"].lower())
    ]
    if linhas:
        mostrar_tabela(pd.DataFrame(linhas), codigo=["Código"])
    else:
        caixa_aviso("Nenhum código com essa busca. Tente o número do código ou outra palavra.")

    st.markdown("---")
    st.markdown("#### Duas fontes, duas perguntas")
    f1, f2 = st.columns(2, gap="large")
    f1.markdown(
        '<div class="fonte-bloco"><h4>ISP-RJ</h4>'
        '<p>Registros de ocorrência feitos nas delegacias da Polícia Civil.</p>'
        '<p><b>Responde:</b> quanto crime foi registrado na cidade?</p>'
        '<p><b>Recorte:</b> município e áreas de delegacia (CISPs 76, 77, 78, 79 e 81).</p></div>',
        unsafe_allow_html=True)
    f2.markdown(
        '<div class="fonte-bloco"><h4>BOGCM</h4>'
        '<p>Ocorrências atendidas pelos guardas ou demandadas a eles na rua.</p>'
        '<p><b>Responde:</b> onde, quando e como a Guarda atua?</p>'
        '<p><b>Recorte:</b> bairro, código de ocorrência, dia e horário.</p></div>',
        unsafe_allow_html=True)
    st.caption("O BOGCM mede a atuação e a demanda da Guarda. Ele não substitui a estatística criminal oficial: as duas fontes se complementam.")

    st.markdown("#### IARA: o dado guia cada etapa")
    st.markdown(
        '<ol class="passos">'
        '<li><b>Identificar</b>Mapas e séries mostram onde e quando o problema se repete.</li>'
        '<li><b>Analisar</b>Hora, local, alvo e tipo de ocorrência explicam por que ele acontece.</li>'
        '<li><b>Responder</b>Metas em número orientam a ação da Guarda e dos parceiros.</li>'
        '<li><b>Avaliar</b>Comparar antes e depois mostra se o problema diminuiu.</li></ol>',
        unsafe_allow_html=True)

# ------------------------------------------------------------------ MICRODADOS
with tab_micro:
    st.markdown("#### Boletins do filtro atual")
    st.caption("Esta tabela não traz nomes, documentos, telefones nem o texto do relato. Esses campos ficam fora do painel.")
    colunas = {
        "id_bogcm": "Boletim", "data_hora": "Data e hora", "bairro": "Bairro", "servico": "Coordenadoria / serviço",
        "codigo": "Código", "ocorrencia": "Ocorrência", "grupo": "Grupo",
    }
    ordens = {
        "Data e hora, mais recentes primeiro": (["Data e hora"], [False]),
        "Coordenadoria ou serviço": (["Coordenadoria / serviço", "Data e hora"], [True, False]),
        "Bairro": (["Bairro", "Data e hora"], [True, False]),
        "Código": (["Código", "Data e hora"], [True, False]),
    }
    ordem_micro = st.selectbox("Ordenar por", list(ordens))
    cols_o, asc_o = ordens[ordem_micro]
    vista = df_f[list(colunas)].rename(columns=colunas).sort_values(cols_o, ascending=asc_o)
    mostrar_tabela(vista, codigo=["Código"], max_linhas=500)
    if len(vista) > 500:
        st.caption(f"Mostrando as 500 primeiras linhas de {n_br(len(vista))}, na ordem escolhida. O download leva todas.")
    st.download_button(
        "Baixar CSV (abre no Excel)",
        data=vista.to_csv(index=False, sep=";", encoding="utf-8-sig").encode("utf-8-sig"),
        file_name="bogcm_filtrado.csv", mime="text/csv",
    )
