"""Carregamento e normalização dos dados do BOGCM.

Fluxo:
  1. Se existir um arquivo real em dados/ (bogcm.csv ou bogcm.xlsx), usa ele.
  2. Senão, usa os dados fictícios de data_generator.py.
  3. Nos dois casos, o resultado passa pelo MESMO tratamento: renomeia colunas
     (ALIAS), valida o código, deriva hora/dia/mês, confere o pino e descarta
     tudo que não é indicador (nomes, CPF, telefone, endereço, relato).

Quando chegar a exportação real, o único trecho a ajustar costuma ser ALIAS.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

import numpy as np
import pandas as pd

from codigos import CODIGO_NOME, CODIGOS_OUTROS, GRUPOS
from data_generator import gerar_bogcm_ficticio
from territorio import BBOX_NITEROI, INSPETORIA_POR_BAIRRO, normalizar_texto

PASTA_DADOS = Path(__file__).parent / "dados"
ARQUIVOS_REAIS = ["bogcm.csv", "bogcm.xlsx"]

# nome canônico -> nomes que a coluna pode ter na exportação real
# (comparados sem acento, em minúsculas, com espaços trocados por "_").
ALIAS = {
    "id_bogcm": ["id_bogcm", "id", "protocolo", "numero", "n_protocolo", "numero_protocolo"],
    "data_hora": ["data_hora", "data_hora_ocorrencia", "data_e_hora", "datahora"],
    "data": ["data", "data_ocorrencia", "data_da_ocorrencia", "data_do_fato"],
    "hora_txt": ["hora", "hora_ocorrencia", "hora_da_ocorrencia", "horario"],
    "data_criacao": ["data_criacao", "data_de_criacao", "criado_em", "data_registro", "data_do_registro", "created_at"],
    "bairro": ["bairro", "bairro_ocorrencia"],
    "latitude": ["latitude", "lat"],
    "longitude": ["longitude", "lon", "lng", "long"],
    "servico": ["servico", "coordenadoria", "coordenadoria_servico", "servico_lotacao", "lotacao", "unidade"],
    "ras": ["ras"],
    "codigo": ["codigo", "codigo_ocorrencia", "codigo_de_ocorrencia", "codigo_da_ocorrencia",
               "cod_ocorrencia", "cod", "natureza", "ocorrencia"],
    "tipo_furto": ["tipo_furto", "tipo_de_furto"],
    "qtd_guardas": ["qtd_guardas", "numero_guardas", "guardas_presentes"],
    "qtd_qualificados": ["qtd_qualificados", "numero_qualificados", "qualificados"],
    "conducao_prisao": ["conducao_prisao", "conducao", "prisao", "conducao_ou_prisao"],
    "relato": ["relato", "relatorio", "historico", "historico_da_ocorrencia"],
}

# Só estas colunas chegam ao app. Nomes, documentos, telefones e endereços
# das pessoas qualificadas nunca entram (LGPD; slide 29 pede sigilo).
COLUNAS_FINAIS = [
    "id_bogcm", "data_hora", "data_criacao", "mes_ref", "hora", "dia_semana", "fim_de_semana",
    "bairro", "inspetoria", "latitude", "longitude", "pino_valido",
    "servico", "ras", "grupo_cod", "grupo", "codigo", "ocorrencia", "codigo_valido", "e_outros",
    "tipo_furto", "qtd_guardas", "qtd_qualificados", "conducao_prisao", "relato_fraco",
    "criado_dia_diferente",
]

DIAS_PT = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira",
           "Sexta-feira", "Sábado", "Domingo"]

_NOME_PARA_CODIGO = {normalizar_texto(nome): cod for cod, nome in CODIGO_NOME.items()}

_PADRAO_CONDUCAO = re.compile(
    r"conduz|conduc|preso|prisao|flagrante|delegacia|apresentad|detid|\bcisp\b|\bdp\b"
)
RELATO_MIN_CHARS = 80  # abaixo disso o relato é tratado como curto demais (ajuste conforme a rotina da Guarda)
_RELATOS_GENERICOS = {"teste", "conforme narrado", "conforme relatado", "ver anexo", "sem alteracao"}


def _chave(nome) -> str:
    return re.sub(r"[^a-z0-9]+", "_", normalizar_texto(nome)).strip("_")


def _renomear(df: pd.DataFrame) -> pd.DataFrame:
    reverso = {}
    for canonico, nomes in ALIAS.items():
        for n in nomes:
            reverso.setdefault(_chave(n), canonico)
    novos = {}
    usados = set()
    for col in df.columns:
        canonico = reverso.get(_chave(col))
        if canonico and canonico not in usados:
            novos[col] = canonico
            usados.add(canonico)
    return df.rename(columns=novos)


def _ler_arquivo(caminho: Path) -> pd.DataFrame:
    if caminho.suffix.lower() == ".xlsx":
        return pd.read_excel(caminho)
    for enc in ("utf-8-sig", "latin-1"):
        try:
            return pd.read_csv(caminho, sep=None, engine="python", encoding=enc)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Não consegui ler {caminho.name}: codificação desconhecida.")


def _para_bool(serie: pd.Series) -> pd.Series:
    """Sim/Não, True/False, 1/0 -> booleano que aceita ausência (NA)."""
    texto = serie.astype("string").str.strip().str.lower()
    out = pd.Series(pd.NA, index=serie.index, dtype="boolean")
    out[texto.isin(["true", "1", "sim", "s", "x", "yes"])] = True
    out[texto.isin(["false", "0", "nao", "não", "n", "no"])] = False
    return out


def _converter_datas(serie: pd.Series) -> pd.Series:
    if pd.api.types.is_datetime64_any_dtype(serie):
        return serie
    texto = serie.astype("string")
    dia_primeiro = texto.str.contains("/", regex=False).fillna(False).mean() > 0.5
    return pd.to_datetime(texto, errors="coerce", dayfirst=bool(dia_primeiro))


def _localizar_arquivo_real() -> Path | None:
    forcado = os.environ.get("BOGCM_ARQUIVO")
    if forcado and Path(forcado).exists():
        return Path(forcado)
    for nome in ARQUIVOS_REAIS:
        p = PASTA_DADOS / nome
        if p.exists():
            return p
    return None


def assinatura_fonte() -> str:
    """Muda quando o arquivo real muda; serve de chave para o cache do app."""
    p = _localizar_arquivo_real()
    return f"{p}:{p.stat().st_mtime_ns}" if p else "ficticio"


def normalizar(bruto: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Aplica o tratamento padrão. Devolve (dados, meta); meta tem 'avisos' e 'conducao_origem'."""
    avisos: list[str] = []
    df = _renomear(bruto.copy())

    # --- data e hora da ocorrência
    if "data_hora" in df:
        df["data_hora"] = _converter_datas(df["data_hora"])
    elif "data" in df:
        base = df["data"].astype("string")
        if "hora_txt" in df:
            base = base + " " + df["hora_txt"].astype("string")
        df["data_hora"] = _converter_datas(base)
    else:
        raise ValueError(
            "Não encontrei a data/hora da ocorrência. Colunas do arquivo: "
            f"{list(bruto.columns)}. Ajuste ALIAS em dados.py."
        )

    if "codigo" not in df:
        raise ValueError(
            "Não encontrei a coluna do código de ocorrência. Colunas do arquivo: "
            f"{list(bruto.columns)}. Ajuste ALIAS em dados.py."
        )

    antes = len(df)
    df = df[df["data_hora"].notna()].copy()
    if len(df) < antes:
        avisos.append(f"{antes - len(df):,} boletins sem data/hora válida foram descartados.")

    # --- código, grupo, "Outros"
    bruto_codigo = df["codigo"].astype("string")
    por_digitos = bruto_codigo.str.extract(r"(\d{3})", expand=False)
    por_nome = bruto_codigo.map(lambda t: _NOME_PARA_CODIGO.get(normalizar_texto(t)) if pd.notna(t) else None)
    df["codigo"] = por_digitos.fillna(por_nome).astype("string")
    df["codigo_valido"] = df["codigo"].isin(CODIGO_NOME)
    if (~df["codigo_valido"]).any():
        avisos.append(f"{int((~df['codigo_valido']).sum()):,} boletins com código fora do dicionário de 39 códigos.")
    df["ocorrencia"] = df["codigo"].map(CODIGO_NOME).fillna("Código fora do dicionário")
    df["grupo_cod"] = np.where(df["codigo_valido"], df["codigo"].fillna("0").str[0] + "00", "")
    df["grupo"] = [f"{g} - {GRUPOS[g]}" if g in GRUPOS else "Sem grupo" for g in df["grupo_cod"]]
    df["e_outros"] = df["codigo"].isin(CODIGOS_OUTROS)

    # --- tempo
    df["hora"] = df["data_hora"].dt.hour
    df["dia_semana"] = df["data_hora"].dt.weekday.map(dict(enumerate(DIAS_PT)))
    df["fim_de_semana"] = df["data_hora"].dt.weekday.isin([4, 5, 6])
    if "data_criacao" in df:
        df["data_criacao"] = _converter_datas(df["data_criacao"])
    else:
        df["data_criacao"] = pd.NaT
    referencia = df["data_criacao"].fillna(df["data_hora"])  # mês de referência = data de criação (slide 9)
    df["mes_ref"] = referencia.dt.to_period("M").dt.to_timestamp()
    diferente = (df["data_criacao"].dt.normalize() != df["data_hora"].dt.normalize()).astype("boolean")
    diferente[df["data_criacao"].isna()] = pd.NA
    df["criado_dia_diferente"] = diferente

    # --- território e pino
    df["bairro"] = df["bairro"].astype("string").str.strip() if "bairro" in df else "Não informado"
    df["bairro"] = df["bairro"].fillna("Não informado").replace("", "Não informado")
    df["inspetoria"] = df["bairro"].map(lambda b: INSPETORIA_POR_BAIRRO.get(normalizar_texto(b), "Não mapeada"))
    for col in ("latitude", "longitude"):
        df[col] = pd.to_numeric(df[col], errors="coerce") if col in df else np.nan
    b = BBOX_NITEROI
    df["pino_valido"] = (
        df["latitude"].between(b["lat_min"], b["lat_max"]) & df["longitude"].between(b["lon_min"], b["lon_max"])
    )

    # --- campos opcionais
    for col, padrao in (("servico", "Não informado"), ("tipo_furto", None), ("id_bogcm", None)):
        if col not in df:
            df[col] = padrao
    df["servico"] = df["servico"].astype("string").str.strip().fillna("Não informado").replace("", "Não informado")
    df["ras"] = _para_bool(df["ras"]) if "ras" in df else pd.Series(pd.NA, index=df.index, dtype="boolean")
    for col in ("qtd_guardas", "qtd_qualificados"):
        df[col] = pd.to_numeric(df[col], errors="coerce") if col in df else np.nan

    # --- condução/prisão e qualidade do relato (a condução só existe no texto do relato)
    nulo = pd.Series(pd.NA, index=df.index, dtype="boolean")
    texto = None
    if "relato" in df:
        texto = df["relato"].astype("string").map(lambda t: normalizar_texto(t) if pd.notna(t) else "")

    if "conducao_prisao" in df:
        df["conducao_prisao"] = _para_bool(df["conducao_prisao"])
        conducao_origem = "campo"
    elif texto is not None:
        df["conducao_prisao"] = texto.str.contains(_PADRAO_CONDUCAO).astype("boolean")
        conducao_origem = "relato"
    else:
        df["conducao_prisao"] = nulo
        conducao_origem = "indisponivel"

    if texto is not None:
        df["relato_fraco"] = ((texto.str.len() < RELATO_MIN_CHARS) | texto.isin(_RELATOS_GENERICOS)).astype("boolean")
    else:
        df["relato_fraco"] = nulo

    # --- só o que é indicador
    meta = {"avisos": avisos, "conducao_origem": conducao_origem}
    return df.reindex(columns=COLUNAS_FINAIS).reset_index(drop=True), meta


def carregar_dados() -> tuple[pd.DataFrame, dict]:
    """Devolve (dados, meta). meta: origem ('real'|'ficticio'), avisos, conducao_origem."""
    caminho = _localizar_arquivo_real()
    if caminho is not None:
        df, meta = normalizar(_ler_arquivo(caminho))
        meta["origem"] = "real"
        meta["arquivo"] = caminho.name
    else:
        df, meta = normalizar(gerar_bogcm_ficticio())
        meta["origem"] = "ficticio"
        meta["arquivo"] = None
    return df, meta
