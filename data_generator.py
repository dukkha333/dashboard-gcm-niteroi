import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_bogcm_mock_data(records=1200):
    np.random.seed(42)
    start_date = datetime(2026, 1, 1)
    
    # Mapeamento territorial real da GCM Niterói
    inspetorias_bairros = {
        '1ª Inspetoria (Centro)': ['Centro', 'Ilha da Conceição', 'Ponta d\'Areia', 'São Lourenço', 'Fátima', 'Ingá', 'Boa Viagem'],
        '2ª Inspetoria (Icaraí)': ['Icaraí', 'Santa Rosa', 'Vital Brasil', 'Viradouro', 'Pé Pequeno', 'Cubango'],
        '3ª Inspetoria (São Francisco)': ['São Francisco', 'Charitas', 'Jurujuba', 'Largo da Batalha', 'Badú', 'Pendotiba'],
        '4ª Inspetoria (Fonseca)': ['Fonseca', 'Engenhoca', 'Barreto', 'Caramujo', 'Santa Bárbara'],
        '5ª Inspetoria (Oceânica)': ['Piratininga', 'Camboinhas', 'Itacoatiara', 'Itaipu', 'Engenho do Mato', 'Várzea das Moças']
    }
    
    coords_bairros = {
        'Centro': (-22.8833, -43.1250), 'Icaraí': (-22.9083, -43.1100),
        'São Francisco': (-22.9250, -43.0900), 'Fonseca': (-22.8750, -43.0950),
        'Piratininga': (-22.9500, -43.0600), 'Itaipu': (-22.9650, -43.0400)
    }

    categorias = {
        'CMA': ('Meio Ambiente', ['Resgate de Fauna Silvestre', 'Apreensão de Equinos', 'Combate a Incêndio Vegetal']),
        'PGMP': ('Proteção à Mulher', ['Acompanhamento de Medida Protetiva', 'Atendimento de Emergência PGMP']),
        'CT': ('Trânsito', ['Fiscalização de Fluidez', 'Estacionamento Irregular', 'Remoção de Veículo Abandonado']),
        'CPE': ('Patrulha Escolar', ['Ronda Preventiva Escolar', 'Mediação de Conflito Estudantil']),
        'GCM_PATRULHA': ('Ordem Pública', ['Desordem Urbana', 'Auxílio ao Cidadão', 'Fiscalização de Posturas'])
    }

    data = []
    for i in range(records):
        bogcm_id = f"BOGCM-2026-{i+1001:05d}"
        days_offset = np.random.randint(0, 240)
        hours_offset = np.random.randint(0, 24)
        dt = start_date + timedelta(days=days_offset, hours=hours_offset)
        
        insp = np.random.choice(list(inspetorias_bairros.keys()))
        bairro = np.random.choice(inspetorias_bairros[insp])
        
        coord_key = 'Centro'
        for k in coords_bairros.keys():
            if k in bairro:
                coord_key = k
                break
        base_lat, base_lon = coords_bairros.get(coord_key, (-22.8900, -43.1000))
        lat = base_lat + np.random.normal(0, 0.006)
        lon = base_lon + np.random.normal(0, 0.006)

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
            'origem': np.random.choice(['CISP 153', 'Patrulhamento Movel', 'Presencial'], p=[0.60, 0.30, 0.10])
        })

    return pd.DataFrame(data)

if __name__ == "__main__":
    df = generate_bogcm_mock_data()
    df.to_csv("bogcm_ficticio.csv", index=False)