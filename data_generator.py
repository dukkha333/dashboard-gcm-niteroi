"""Gerador de dados FICTÍCIOS do BOGCM, para demonstração e testes.

O formato imita o que o formulário do BOGCM coleta (grupo e código, bairro,
pino, serviço, RAS, guarnição, qualificados) e o perfil agregado mostrado na
aula do OMOP: volume mensal, concentração entre 9h e 11h59, código 503 com ~45%
dos boletins, "Outros" com ~8%. Os registros individuais são inventados.

Só gera colunas brutas; grupo, hora, dia da semana etc. são derivados em dados.py,
pelo mesmo caminho que os dados reais vão percorrer.
"""
import numpy as np
import pandas as pd

from territorio import BAIRROS_POR_INSPETORIA, COORDS_BAIRROS

# Boletins por mês (slides 11 e 12: set/25 = 1.337, fev/26 = 1.160, set/26 = 2.568;
# jan a mai/26 somam 8.532). Meses fora da série dos slides são estimativa.
VOLUME_MENSAL = {
    "2025-01": 1250, "2025-02": 1200, "2025-03": 1300, "2025-04": 1320,
    "2025-05": 1350, "2025-06": 1300, "2025-07": 1290, "2025-08": 1310,
    "2025-09": 1337, "2025-10": 1300, "2025-11": 1250, "2025-12": 1280,
    "2026-01": 1500, "2026-02": 1160, "2026-03": 1700, "2026-04": 2000,
    "2026-05": 2172, "2026-06": 2250, "2026-07": 2350, "2026-08": 2450,
    "2026-09": 2568,
}

# Boletins por hora do dia (slide 12): pico das 9h às 11h59 e segundo pico às 15h.
PESO_HORA = [65, 45, 25, 30, 40, 195, 370, 445, 545, 857, 1062, 787,
             590, 505, 485, 665, 520, 365, 275, 210, 195, 135, 110, 90]

# Segunda a domingo (slide 12).
PESO_DIA_SEMANA = [1229, 1260, 1304, 1191, 1293, 1145, 1110]

# Distribuição por código (slide 14): 503 ~45%, dez códigos ~89%, "Outros" (150 e 550) ~8%.
PESO_CODIGO = {
    "503": 46.0, "506": 7.5, "204": 6.0, "402": 5.0, "502": 5.0, "202": 4.5,
    "508": 4.0, "203": 4.0, "550": 5.0, "150": 3.0,
    # restante (~11,5%): ilustrativo
    "106": 2.8, "501": 2.2, "107": 1.0, "102": 0.8, "110": 0.7, "111": 0.6,
    "401": 0.7, "507": 0.5, "304": 0.5, "301": 0.4, "104": 0.4, "108": 0.3,
    "205": 0.3, "201": 0.2, "112": 0.2, "114": 0.9, "303": 0.2, "302": 0.1,
    "113": 0.1, "103": 0.1, "105": 0.1, "504": 0.1, "250": 0.1, "350": 0.05,
    "450": 0.05, "505": 0.03, "101": 0.02, "109": 0.02, "115": 0.02,
}

LIMITE_CRIACAO = pd.Timestamp(list(VOLUME_MENSAL)[-1] + "-01") + pd.offsets.MonthEnd(0) + pd.Timedelta(hours=23, minutes=59)

SERVICOS = ["Regional", "CISP", "SSOP", "Supervisão", "Patrulha Escolar", "CASS", "CMA", "PGMP", "CAT"]
_BASE = [0.38, 0.18, 0.09, 0.09, 0.09, 0.03, 0.02, 0.02, 0.10]
_PESO_SERVICO = {
    "503": [0.30, 0.04, 0.03, 0.04, 0.02, 0.55, 0.00, 0.00, 0.02],        # assistência social -> CASS
    "ambiental": [0.12, 0.03, 0.02, 0.04, 0.00, 0.00, 0.75, 0.00, 0.04],  # 301 a 304 e 350 -> CMA
    "114": [0.10, 0.06, 0.02, 0.02, 0.00, 0.00, 0.00, 0.80, 0.00],        # violência contra a mulher -> PGMP
    "mulher": [0.40, 0.20, 0.05, 0.05, 0.00, 0.00, 0.00, 0.30, 0.00],     # 102 e 104
}


def _pesos_servico(cod: str):
    if cod == "503":
        chave = "503"
    elif cod in ("301", "302", "303", "304", "350"):
        chave = "ambiental"
    elif cod == "114":
        chave = "114"
    elif cod in ("102", "104"):
        chave = "mulher"
    else:
        return _BASE
    return _PESO_SERVICO[chave]


# Chance de condução/prisão por código
P_CONDUCAO = {"107": 0.5, "106": 0.2, "111": 0.7, "112": 0.8, "110": 0.6,
              "507": 0.9, "508": 0.15, "102": 0.3}

TIPOS_FURTO = ["Celular", "Transeunte", "Bicicleta", "Comércio", "Residência"]
PESO_FURTO = [0.35, 0.25, 0.10, 0.18, 0.12]

# Concentração por bairro: poucos lugares reúnem boa parte dos boletins (slide 16).
_PESO_BAIRRO_TOPO = {"Centro": 14, "Icaraí": 11, "Ingá": 6, "Fonseca": 5, "São Francisco": 5,
                     "Santa Rosa": 4, "Charitas": 3, "Piratininga": 3}


def gerar_bogcm_ficticio(escala: float = 0.25, semente: int = 42) -> pd.DataFrame:
    """Gera boletins fictícios.

    escala: fração do volume mensal real a gerar (0.25 → cerca de 9 mil linhas).
    """
    rng = np.random.default_rng(semente)

    bairros = [b for lista in BAIRROS_POR_INSPETORIA.values() for b in lista]
    p_bairro = np.array([_PESO_BAIRRO_TOPO.get(b, 1.0) for b in bairros], dtype=float)
    p_bairro /= p_bairro.sum()

    codigos = list(PESO_CODIGO)
    p_codigo = np.array([PESO_CODIGO[c] for c in codigos], dtype=float)
    p_codigo /= p_codigo.sum()

    p_hora = np.array(PESO_HORA, dtype=float)
    p_hora /= p_hora.sum()

    linhas = []
    for mes, total in VOLUME_MENSAL.items():
        n = int(round(total * escala))
        inicio = pd.Timestamp(mes + "-01")
        dias_mes = pd.date_range(inicio, inicio + pd.offsets.MonthEnd(0))
        peso_dia = np.array([PESO_DIA_SEMANA[d.weekday()] for d in dias_mes], dtype=float)
        peso_dia /= peso_dia.sum()

        dias = rng.choice(len(dias_mes), size=n, p=peso_dia)
        horas = rng.choice(24, size=n, p=p_hora)
        minutos = rng.integers(0, 60, size=n)
        cods = rng.choice(codigos, size=n, p=p_codigo)
        bairros_n = rng.choice(bairros, size=n, p=p_bairro)

        for i in range(n):
            cod = cods[i]
            bairro = bairros_n[i]
            data_hora = dias_mes[dias[i]] + pd.Timedelta(hours=int(horas[i]), minutes=int(minutos[i]))

            # Registro no mesmo dia na maioria dos casos (slide 9)
            atraso = 0 if rng.random() < 0.88 else int(rng.integers(1, 4))
            data_criacao = data_hora + pd.Timedelta(days=atraso, minutes=int(rng.integers(5, 90)))
            data_criacao = min(data_criacao, LIMITE_CRIACAO)  # série termina no último mês do VOLUME_MENSAL

            lat0, lon0 = COORDS_BAIRROS[bairro]
            lat = lat0 + rng.normal(0, 0.002)
            lon = lon0 + rng.normal(0, 0.002)
            sorteio = rng.random()
            if sorteio < 0.015:          # pino ausente
                lat = lon = np.nan
            elif sorteio < 0.03:         # pino errado, longe do bairro
                lat, lon = lat + 0.12, lon + 0.15

            p_serv = np.array(_pesos_servico(cod), dtype=float)
            p_serv /= p_serv.sum()
            linhas.append({
                "data_hora": data_hora,
                "data_criacao": data_criacao,
                "bairro": bairro,
                "latitude": lat,
                "longitude": lon,
                "servico": str(rng.choice(SERVICOS, p=p_serv)),
                "ras": bool(rng.random() < 0.15),
                "codigo": cod,
                "tipo_furto": rng.choice(TIPOS_FURTO, p=PESO_FURTO) if cod == "106" else None,
                "qtd_guardas": int(rng.choice([1, 2, 3, 4], p=[0.35, 0.40, 0.18, 0.07])),
                "qtd_qualificados": 1 if cod == "503" else int(rng.choice([0, 1, 2, 3], p=[0.35, 0.35, 0.2, 0.1])),
                "conducao_prisao": bool(rng.random() < P_CONDUCAO.get(cod, 0.02)),
            })

    df = pd.DataFrame(linhas).sort_values("data_hora").reset_index(drop=True)
    df.insert(0, "id_bogcm", [f"FICT-{d.year}-{i + 1:06d}" for i, d in enumerate(df["data_hora"])])
    return df


if __name__ == "__main__":
    df = gerar_bogcm_ficticio()
    df.to_csv("bogcm_ficticio.csv", index=False)
    print(f"{len(df):,} boletins fictícios gravados em bogcm_ficticio.csv")
