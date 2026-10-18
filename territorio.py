"""Território de Niterói: bairros por inspetoria e coordenadas aproximadas.

Reaproveitado do data_generator.py original. Quando chegarem os dados reais,
confira se os nomes de bairro do BOGCM batem com estes; os que não baterem
aparecem como "Não mapeada" na coluna de inspetoria.
"""
import unicodedata

BAIRROS_POR_INSPETORIA = {
    '1ª Inspetoria (Centro)': ['Centro', 'Ilha da Conceição', "Ponta d'Areia", 'São Lourenço', 'Fátima', 'Ingá', 'Boa Viagem', 'São Domingos', 'Morro do Estado'],
    '2ª Inspetoria (Icaraí)': ['Icaraí', 'Santa Rosa', 'Vital Brasil', 'Viradouro', 'Pé Pequeno', 'Cubango'],
    '3ª Inspetoria (São Francisco)': ['São Francisco', 'Charitas', 'Jurujuba', 'Cachoeiras', 'Largo da Batalha', 'Badú', 'Pendotiba'],
    '4ª Inspetoria (Fonseca)': ['Fonseca', 'Engenhoca', 'Barreto', 'Santana', 'Caramujo', 'Santa Bárbara'],
    '5ª Inspetoria (Oceânica)': ['Piratininga', 'Camboinhas', 'Itaipu', 'Itacoatiara', 'Cafubá', 'Engenho do Mato'],
}

COORDS_BAIRROS = {
    'Centro': (-22.8870, -43.1225), 'Ilha da Conceição': (-22.8760, -43.1280), "Ponta d'Areia": (-22.8820, -43.1310),
    'São Lourenço': (-22.8810, -43.1150), 'Fátima': (-22.8910, -43.1160), 'Ingá': (-22.9020, -43.1220),
    'Boa Viagem': (-22.9070, -43.1300), 'São Domingos': (-22.8980, -43.1270), 'Morro do Estado': (-22.8940, -43.1200),
    'Icaraí': (-22.9080, -43.1080), 'Santa Rosa': (-22.9030, -43.0980), 'Vital Brasil': (-22.9150, -43.1020),
    'Viradouro': (-22.9120, -43.0920), 'Pé Pequeno': (-22.9000, -43.1000), 'Cubango': (-22.8920, -43.0950),
    'São Francisco': (-22.9230, -43.0920), 'Charitas': (-22.9320, -43.0950), 'Jurujuba': (-22.9380, -43.1100),
    'Cachoeiras': (-22.9180, -43.0850), 'Largo da Batalha': (-22.9080, -43.0680), 'Badú': (-22.9110, -43.0580),
    'Pendotiba': (-22.9120, -43.0620), 'Fonseca': (-22.8750, -43.0920), 'Engenhoca': (-22.8680, -43.1020),
    'Barreto': (-22.8650, -43.1180), 'Santana': (-22.8780, -43.1120), 'Caramujo': (-22.8680, -43.0720),
    'Santa Bárbara': (-22.8620, -43.0550), 'Piratininga': (-22.9520, -43.0680), 'Camboinhas': (-22.9620, -43.0600),
    'Itaipu': (-22.9680, -43.0420), 'Itacoatiara': (-22.9730, -43.0280), 'Cafubá': (-22.9420, -43.0750),
    'Engenho do Mato': (-22.9520, -43.0280),
}

# Caixa aproximada do município. Pino fora dela é tratado como pino errado.
# Ajuste se a base real tiver pontos legítimos nas bordas (ex.: Ilha da Boa Viagem).
BBOX_NITEROI = {"lat_min": -23.01, "lat_max": -22.82, "lon_min": -43.14, "lon_max": -42.97}

CENTRO_MAPA = {"lat": -22.9000, "lon": -43.0800}


def normalizar_texto(s) -> str:
    """minúsculas, sem acento, sem espaços nas pontas: para comparar nomes."""
    s = unicodedata.normalize("NFKD", str(s))
    return "".join(c for c in s if not unicodedata.combining(c)).strip().lower()


INSPETORIA_POR_BAIRRO = {
    normalizar_texto(b): insp
    for insp, bairros in BAIRROS_POR_INSPETORIA.items()
    for b in bairros
}


# Coordenadorias e serviços que aparecem no campo "Serviço" do BOGCM (slide 23 da aula cita
# Regional, CASS, CISP, SSOP, Patrulha Escolar e Supervisão, "entre outros").
# Edite aqui: sigla -> nome por extenso, só para exibir ao lado da sigla. Se não souber o nome
# de uma sigla, deixe "" e o painel mostra só a sigla. Siglas que não estiverem aqui continuam
# funcionando: aparecem como vierem na base.
COORDENADORIAS = {
    "CASS": "Apoio ao Serviço Social",
    "CMA": "Meio Ambiente",
    "PGMP": "Proteção à Mulher",
    "CAT": "",   # confirmar o nome por extenso com a Guarda
    "Patrulha Escolar": "",
    "Regional": "",
    "CISP": "",
    "SSOP": "",
    "Supervisão": "",
}


def rotulo_coordenadoria(sigla) -> str:
    nome = COORDENADORIAS.get(sigla, "")
    return f"{sigla} ({nome})" if nome else str(sigla)
