import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def generate_bogcm_mock_data(records=1200):
    np.random.seed(42)
    start_date = datetime(2026, 1, 1)

    # Mapeamento territorial real da GCM Niterói
    inspetorias_bairros = {
        '1ª Inspetoria (Centro)': ['Centro', 'Ilha da Conceição', "Ponta d'Areia", 'São Lourenço', 'Fátima', 'Ingá', 'Boa Viagem'],
        '2ª Inspetoria (Icaraí)': ['Icaraí', 'Santa Rosa', 'Vital Brasil', 'Viradouro', 'Pé Pequeno', 'Cubango'],
        '3ª Inspetoria (São Francisco)': ['São Francisco', 'Charitas', 'Jurujuba', 'Largo da Batalha', 'Badu', 'Pendotiba'],
        '4ª Inspetoria (Fonseca)': ['Fonseca', 'Engenhoca', 'Barreto', 'Caramujo', 'Santa Bárbara'],
        '5ª Inspetoria (Oceânica)': ['Piratininga', 'Camboinhas', 'Itacoatiara', 'Itaipu', 'Engenho do Mato', 'Várzea das Moças'],
    }

    # NOTE: coordenadas aproximadas (uso em dado fictício/demo). Para dado real,
    # troque por uma base geocodificada de verdade (ex.: geocoding oficial da
    # prefeitura ou uma tabela de centróides de bairro do IBGE).
    # Antes: só 6 bairros tinham coordenada e o restante caía no fallback
    # "Centro" por causa de um match por substring — isso empilhava quase
    # todos os pontos no mapa em cima do Centro. Agora cada bairro tem sua
    # própria coordenada aproximada.
    bairro_coords = {
        # 1ª Inspetoria (Centro)
        'Centro': (-22.8833, -43.1250),
        'Ilha da Conceição': (-22.8790, -43.1290),
        "Ponta d'Areia": (-22.8870, -43.1200),
        'São Lourenço': (-22.8950, -43.1230),
        'Fátima': (-22.8920, -43.1270),
        'Ingá': (-22.8980, -43.1180),
        'Boa Viagem': (-22.9020, -43.1150),
        # 2ª Inspetoria (Icaraí)
        'Icaraí': (-22.9083, -43.1100),
        'Santa Rosa': (-22.9010, -43.1080),
        'Vital Brasil': (-22.9130, -43.1050),
        'Viradouro': (-22.8950, -43.1100),
        'Pé Pequeno': (-22.9060, -43.1150),
        'Cubango': (-22.8850, -43.0980),
        # 3ª Inspetoria (São Francisco)
        'São Francisco': (-22.9250, -43.0900),
        'Charitas': (-22.9330, -43.0850),
        'Jurujuba': (-22.9280, -43.1000),
        'Largo da Batalha': (-22.8900, -43.0650),
        'Badu': (-22.8950, -43.0700),
        'Pendotiba': (-22.8800, -43.0600),
        # 4ª Inspetoria (Fonseca)
        'Fonseca': (-22.8750, -43.0950),
        'Engenhoca': (-22.8700, -43.0900),
        'Barreto': (-22.8680, -43.1050),
        'Caramujo': (-22.8650, -43.0980),
        'Santa Bárbara': (-22.8600, -43.0900),
        # 5ª Inspetoria (Oceânica)
        'Piratininga': (-22.9500, -43.0600),
        'Camboinhas': (-22.9450, -43.0500),
        'Itacoatiara': (-22.9600, -43.0500),
        'Itaipu': (-22.9650, -43.0400),
        'Engenho do Mato': (-22.9200, -43.0400),
        'Várzea das Moças': (-22.9000, -43.0300),
    }

    categorias = {
        'CMA': ('Meio Ambiente', ['Resgate de Fauna Silvestre', 'Apreensão de Equinos', 'Combate a Incêndio Vegetal']),
        'PGMP': ('Proteção à Mulher', ['Acompanhamento de Medida Protetiva', 'Atendimento de Emergência PGMP']),
        'CT': ('Trânsito', ['Fiscalização de Fluidez', 'Estacionamento Irregular', 'Remoção de Veículo Abandonado']),
        'CPE': ('Patrulha Escolar', ['Ronda Preventiva Escolar', 'Mediação de Conflito Estudantil']),
        'GCM_PATRULHA': ('Ordem Pública', ['Desordem Urbana', 'Auxílio ao Cidadão', 'Fiscalização de Posturas']),
    }

    data = []
    for i in range(records):
        bogcm_id = f"BOGCM-2026-{i + 1001:05d}"

        days_offset = np.random.randint(0, 240)
        hours_offset = np.random.randint(0, 24)
        dt = start_date + timedelta(days=days_offset, hours=hours_offset)

        insp = np.random.choice(list(inspetorias_bairros.keys()))
        bairro = np.random.choice(inspetorias_bairros[insp])

        base_lat, base_lon = bairro_coords.get(bairro, (-22.8900, -43.1000))
        lat = base_lat + np.random.normal(0, 0.003)
        lon = base_lon + np.random.normal(0, 0.003)

        coord_choice = np.random.choice(list(categorias.keys()), p=[0.30, 0.15, 0.25, 0.15, 0.15])
        cat_nome, tipos = categorias[coord_choice]
        tipo = np.random.choice(tipos)

        equinos = 0
        animais_silvestres = 0
        veiculos_removidos = 0
        if tipo == 'Apreensão de Equinos':
            equinos = np.random.randint(1, 4)
        elif tipo == 'Resgate de Fauna Silvestre':
            animais_silvestres = np.random.randint(1, 3)
        elif tipo == 'Remoção de Veículo Abandonado':
            veiculos_removidos = 1

        data.append({
            'id_bogcm': bogcm_id,
            'data_hora': dt,
            'inspetoria': insp,
            'bairro': bairro,
            'coordenadoria': coord_choice,
            'categoria': cat_nome,
            'tipo_ocorrencia': tipo,
            'equinos_resgatados': equinos,
            'animais_silvestres_resgatados': animais_silvestres,
            'veiculos_removidos': veiculos_removidos,
            'latitude': lat,
            'longitude': lon,
            'origem': np.random.choice(['CISP 153', 'Patrulhamento Movel', 'Presencial'], p=[0.60, 0.30, 0.10]),
        })

    return pd.DataFrame(data)


if __name__ == "__main__":
    df = generate_bogcm_mock_data()
    df.to_csv("bogcm_ficticio.csv", index=False)