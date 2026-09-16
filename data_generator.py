import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_bogcm_mock_data(records=1500):
    np.random.seed(42)
    start_date = datetime(2026, 1, 1)
    
    # Mapeamento territorial real de Niterói por Inspetoria Regional
    inspetorias_bairros = {
        '1ª Inspetoria (Centro)': [
            'Centro', 'Ilha da Conceição', 'Ponta d\'Areia', 'São Lourenço', 
            'Fátima', 'Ingá', 'Boa Viagem', 'Gragoatá', 'São Domingos', 'Morro do Estado'
        ],
        '2ª Inspetoria (Icaraí)': [
            'Icaraí', 'Santa Rosa', 'Vital Brasil', 'Viradouro', 'Pé Pequeno', 'Cubango'
        ],
        '3ª Inspetoria (São Francisco)': [
            'São Francisco', 'Charitas', 'Jurujuba', 'Cachoeiras', 'Maceió', 
            'Largo da Batalha', 'Badú', 'Cantagalo', 'Ititioca', 'Sapê', 
            'Vila Progresso', 'Muriqui', 'Matapaca', 'Pendotiba', 'Maria Paula'
        ],
        '4ª Inspetoria (Fonseca)': [
            'Fonseca', 'Engenhoca', 'Barreto', 'Santana', 'Tenente Jardim', 
            'Viçoso Jardim', 'Caramujo', 'Baldeador', 'Santa Bárbara'
        ],
        '5ª Inspetoria (Oceânica)': [
            'Piratininga', 'Camboinhas', 'Itaipu', 'Itacoatiara', 'Cafubá', 
            'Engenho do Mato', 'Jacaré', 'Rio do Ouro', 'Várzea das Moças'
        ]
    }
    
    # Coordenadas geográficas reais (Latitude, Longitude) de cada bairro de Niterói
    coords_bairros = {
        # 1ª Inspetoria (Centro / Zona Urbana)
        'Centro': (-22.8870, -43.1225),
        'Ilha da Conceição': (-22.8760, -43.1280),
        'Ponta d\'Areia': (-22.8820, -43.1310),
        'São Lourenço': (-22.8810, -43.1150),
        'Fátima': (-22.8910, -43.1160),
        'Ingá': (-22.9020, -43.1220),
        'Boa Viagem': (-22.9070, -43.1300),
        'Gragoatá': (-22.9010, -43.1300),
        'São Domingos': (-22.8980, -43.1270),
        'Morro do Estado': (-22.8940, -43.1200),
        
        # 2ª Inspetoria (Icaraí / Zona Sul)
        'Icaraí': (-22.9080, -43.1080),
        'Santa Rosa': (-22.9030, -43.0980),
        'Vital Brasil': (-22.9150, -43.1020),
        'Viradouro': (-22.9120, -43.0920),
        'Pé Pequeno': (-22.9000, -43.1000),
        'Cubango': (-22.8920, -43.0950),
        
        # 3ª Inspetoria (São Francisco / Pendotiba)
        'São Francisco': (-22.9230, -43.0920),
        'Charitas': (-22.9320, -43.0950),
        'Jurujuba': (-22.9380, -43.1100),
        'Cachoeiras': (-22.9180, -43.0850),
        'Maceió': (-22.9100, -43.0780),
        'Largo da Batalha': (-22.9080, -43.0680),
        'Badú': (-22.9110, -43.0580),
        'Cantagalo': (-22.9220, -43.0620),
        'Ititioca': (-22.9010, -43.0780),
        'Sapê': (-22.9050, -43.0520),
        'Vila Progresso': (-22.9150, -43.0480),
        'Muriqui': (-22.9250, -43.0450),
        'Matapaca': (-22.8980, -43.0480),
        'Pendotiba': (-22.9120, -43.0620),
        'Maria Paula': (-22.8950, -43.0380),
        
        # 4ª Inspetoria (Fonseca / Zona Norte)
        'Fonseca': (-22.8750, -43.0920),
        'Engenhoca': (-22.8680, -43.1020),
        'Barreto': (-22.8650, -43.1180),
        'Santana': (-22.8780, -43.1120),
        'Tenente Jardim': (-22.8620, -43.0880),
        'Viçoso Jardim': (-22.8720, -43.0820),
        'Caramujo': (-22.8680, -43.0720),
        'Baldeador': (-22.8580, -43.0650),
        'Santa Bárbara': (-22.8620, -43.0550),
        
        # 5ª Inspetoria (Região Oceânica)
        'Piratininga': (-22.9520, -43.0680),
        'Camboinhas': (-22.9620, -43.0600),
        'Itaipu': (-22.9680, -43.0420),
        'Itacoatiara': (-22.9730, -43.0280),
        'Cafubá': (-22.9420, -43.0750),
        'Engenho do Mato': (-22.9520, -43.0280),
        'Jacaré': (-22.9450, -43.0380),
        'Rio do Ouro': (-22.8920, -43.0180),
        'Várzea das Moças': (-22.9050, -43.0120)
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
        
        # Busca a coordenada exata do bairro selecionado
        base_lat, base_lon = coords_bairros.get(bairro, (-22.8900, -43.1000))
        
        # Adiciona pequena variação para os pontos se espalharem naturalmente dentro do bairro
        lat = base_lat + np.random.normal(0, 0.0025)
        lon = base_lon + np.random.normal(0, 0.0025)

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
    
