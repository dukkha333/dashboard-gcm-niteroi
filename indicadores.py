"""Cálculos dos indicadores produzidos com o BOGCM (slide 9 da aula do OMOP).

Funções puras de pandas: recebem o DataFrame já normalizado por dados.py e
devolvem números ou tabelas. Nada aqui desenha tela.
"""
from __future__ import annotations

import pandas as pd

MESES_ABREV = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def contagem_por_hora(df: pd.DataFrame) -> pd.Series:
    return df.groupby("hora").size().reindex(range(24), fill_value=0)


def janela_pico(df: pd.DataFrame, largura: int = 3) -> dict | None:
    """Faixa de `largura` horas seguidas com mais boletins (ex.: 9h às 11h59)."""
    por_hora = contagem_por_hora(df)
    total = int(por_hora.sum())
    if total == 0:
        return None
    somas = por_hora.rolling(largura).sum().dropna()
    fim = int(somas.idxmax())
    inicio = fim - largura + 1
    return {"inicio": inicio, "fim": fim, "boletins": int(somas.max()), "pct": somas.max() / total * 100}


def segundo_pico(df: pd.DataFrame, pico: dict, folga: int = 1) -> int | None:
    """Hora isolada mais movimentada fora da janela principal (e fora das horas vizinhas)."""
    por_hora = contagem_por_hora(df)
    fora = por_hora.drop(index=[h for h in range(pico["inicio"] - folga, pico["fim"] + folga + 1) if h in por_hora.index])
    return int(fora.idxmax()) if fora.max() > 0 else None


def serie_mensal(df: pd.DataFrame) -> pd.Series:
    return df.groupby("mes_ref").size().sort_index()


def comparativo_ano(df_base: pd.DataFrame, inicio: pd.Timestamp, fim: pd.Timestamp) -> dict:
    """Boletins no período x mesmo período do ano anterior (slide 13).

    df_base deve ter todos os filtros, exceto o de período.
    """
    atual = int(df_base["data_hora"].between(inicio, fim).sum())
    ini_ant, fim_ant = inicio - pd.DateOffset(years=1), fim - pd.DateOffset(years=1)
    anterior = int(df_base["data_hora"].between(ini_ant, fim_ant).sum())
    cobertura = df_base["data_hora"].min() <= ini_ant
    variacao = (atual - anterior) / anterior * 100 if anterior and cobertura else None
    return {"atual": atual, "anterior": anterior, "variacao": variacao, "tem_base": bool(cobertura and anterior)}


def mensal_por_ano(df_base: pd.DataFrame, anos: int = 2) -> pd.DataFrame:
    """Boletins por mês, uma coluna por ano (os `anos` mais recentes), para sobrepor as linhas."""
    s = serie_mensal(df_base)
    if s.empty:
        return pd.DataFrame()
    tabela = pd.DataFrame({"ano": s.index.year, "mes": s.index.month, "boletins": s.values})
    ultimos = sorted(tabela["ano"].unique())[-anos:]
    pivot = tabela[tabela["ano"].isin(ultimos)].pivot(index="mes", columns="ano", values="boletins")
    return pivot.reindex(range(1, 13))


def pareto_codigos(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Códigos mais registrados, com % e % acumulado (slide 14)."""
    total = len(df)
    if total == 0:
        return pd.DataFrame(columns=["codigo", "ocorrencia", "boletins", "pct", "acumulado", "e_outros"])
    t = (
        df.groupby(["codigo", "ocorrencia", "e_outros"], dropna=False)
        .size().reset_index(name="boletins")
        .sort_values("boletins", ascending=False).head(n).reset_index(drop=True)
    )
    t["pct"] = t["boletins"] / total * 100
    t["acumulado"] = t["pct"].cumsum()
    return t


def por_grupo(df: pd.DataFrame) -> pd.DataFrame:
    t = df.groupby(["grupo_cod", "grupo"]).size().reset_index(name="boletins").sort_values("grupo_cod")
    t["pct"] = t["boletins"] / max(len(df), 1) * 100
    return t


def pct_outros(df: pd.DataFrame) -> float:
    return float(df["e_outros"].mean() * 100) if len(df) else 0.0


def qualidade(df: pd.DataFrame) -> dict:
    """Os erros que mais distorcem os indicadores (slide 31). None = indicador indisponível."""
    n = len(df)
    if n == 0:
        return {}

    def pct(serie):
        validos = serie.dropna()
        return float(validos.astype(bool).mean() * 100) if len(validos) else None

    return {
        "outros": pct(df["e_outros"]),
        "sem_pino": float((~df["pino_valido"]).mean() * 100),
        "dia_diferente": pct(df["criado_dia_diferente"]),
        "relato_fraco": pct(df["relato_fraco"]),
        "codigo_fora": float((~df["codigo_valido"]).mean() * 100),
    }


def qualidade_por_servico(df: pd.DataFrame, minimo: int = 30) -> pd.DataFrame:
    """Qualidade do registro por serviço, só para quem tem boletins suficientes para comparar."""
    def resumo(g):
        q = qualidade(g)
        return pd.Series({
            "boletins": len(g),
            "pct_outros": q["outros"],
            "pct_sem_pino": q["sem_pino"],
            "pct_dia_diferente": q["dia_diferente"],
            "pct_relato_fraco": q["relato_fraco"],
        })
    t = df.groupby("servico").apply(resumo, include_groups=False)
    t = t[t["boletins"] >= minimo].sort_values("pct_outros", ascending=False)
    return t.reset_index()


def furto_por_tipo(df: pd.DataFrame) -> pd.Series:
    return df.loc[df["codigo"] == "106", "tipo_furto"].dropna().value_counts()


def por_coordenadoria(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Boletins por coordenadoria/serviço e grupo. Devolve (tabela longa, ordem por volume)."""
    ordem = df["servico"].value_counts().index.tolist()
    t = df.groupby(["servico", "grupo_cod", "grupo"]).size().reset_index(name="boletins")
    return t, ordem


def resumo_coordenadoria(df: pd.DataFrame, sigla: str) -> dict:
    """Números de uma coordenadoria dentro do filtro atual."""
    sub = df[df["servico"] == sigla]
    n = len(sub)
    pico = janela_pico(sub) if n else None
    return {
        "boletins": n,
        "pct_total": n / len(df) * 100 if len(df) else 0.0,
        "pico": pico,
        "pct_outros": pct_outros(sub),
        "sub": sub,
    }
