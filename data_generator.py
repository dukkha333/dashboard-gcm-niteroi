import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_bogcm_mock_data(records=2000):
    np.random.seed(42)
    start_date = datetime(2026, 1, 1)
    
    inspetorias_bairros = {
        '1ª Inspetoria (Centro)': ['Centro', 'Ilha da Conceição', 'Ponta d\'Areia', 'São Lourenço', 'Fátima', 'Ingá', 'Boa Viagem', 'São Domingos', 'Morro do Estado'],
        '2ª Inspetoria (Icaraí)': ['Icaraí', 'Santa Rosa', 'Vital Brasil', 'Viradouro', 'Pé Pequeno', 'Cubango'],
        '3ª Inspetoria (São Francisco)': ['São Francisco', 'Charitas', 'Jurujuba', 'Cachoeiras', 'Largo da Batalha', 'Badú', 'Pendotiba'],
        '4ª Inspetoria (Fonseca)': ['Fonseca', 'Engenhoca', 'Barreto', 'Santana', 'Caramujo', 'Santa Bárbara'],
        '5ª Inspetoria (Oceânica)': ['Piratininga', 'Camboinhas', 'Itaipu', 'Itacoatiara', 'Cafubá', 'Engenho do Mato']
    }
    
    coords_bairros = {
        'Centro': (-22.8870, -43.1225), 'Ilha da Conceição': (-22.8760, -43.1280), 'Ponta d\'Areia': (-22.8820, -43.1310),
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
        'Engenho do Mato': (-22.9520, -43.0280)
    }

    categorias = {
        'CASS': ('Apoio Social (PSR)', ['Abordagem e Acolhimento PSR', 'Desmobilização de Acampamento PSR', 'Encaminhamento Centro POP/Abrigo']),
        'CMA': ('Meio Ambiente', ['Resgate de Fauna Silvestre', 'Apreensão de Equinos', 'Combate a Incêndio Vegetal']),
        'PGMP': ('Proteção à Mulher', ['Acompanhamento de Medida Protetiva', 'Atendimento de Emergência PGMP']),
        'CT': ('Trânsito', ['Fiscalização de Fluidez', 'Estacionamento Irregular', 'Remoção de Veículo Abandonado']),
        'POSTURAS': ('Ordem Pública e Som', ['Fiscalização de Som Alto / Perturbação', 'Ambulante Irregular', 'Operação Verão / Orla']),
        'CPE': ('Patrulha Escolar', ['Ronda Preventiva Escolar', 'Mediação de Conflito Estudantil']),
        'GCM_PATRULHA': ('Patrulhamento Geral', ['Auxílio ao Cidadão', 'Apoio ao Cercamento Eletrônico CISP', 'Preservação de Próprio Municipal'])
    }

    data = []
    for i in range(records):
        bogcm_id = f"BOGCM-2026-{i+1001:05d}"
        days_offset = np.random.randint(0, 240)
        
        # Sorteio de hora realista por tipo de serviço
        coord_choice = np.random.choice(
            list(categorias.keys()), 
            p=[0.25, 0.18, 0.10, 0.17, 0.15, 0.08, 0.07] # 25% para CASS/PSR
        )
        cat_nome, tipos = categorias[coord_choice]
        tipo = np.random.choice(tipos)

        # Horários táticos probabilísticos
        if tipo == 'Fiscalização de Som Alto / Perturbação':
            hour = np.random.choice([20, 21, 22, 23, 0, 1, 2, 3])
        elif tipo in ['Abordagem e Acolhimento PSR', 'Desmobilização de Acampamento PSR']:
            hour = np.random.choice([8, 9, 10, 11, 14, 15, 16, 19, 20])
        elif tipo == 'Operação Verão / Orla':
            hour = np.random.choice([10, 11, 12, 13, 14, 15, 16, 17])
        else:
            hour = np.random.randint(0, 24)

        dt = start_date + timedelta(days=int(days_offset), hours=int(hour))
        
        # Pessoas em situação de rua concentradas no Centro e Icaraí
        if coord_choice == 'CASS':
            insp = np.random.choice(['1ª Inspetoria (Centro)', '2ª Inspetoria (Icaraí)'], p=[0.70, 0.30])
        else:
            insp = np.random.choice(list(inspetorias_bairros.keys()))
            
        bairro = np.random.choice(inspetorias_bairros[insp])
        
        base_lat, base_lon = coords_bairros.get(bairro, (-22.8900, -43.1000))
        lat = base_lat + np.random.normal(0, 0.002)
        lon = base_lon + np.random.normal(0, 0.002)

        equinos = 1 if tipo == 'Apreensão de Equinos' else 0
        fauna = 1 if tipo == 'Resgate de Fauna Silvestre' else 0
        veiculos = 1 if tipo == 'Remoção de Veículo Abandonado' else 0
        psr_atendimentos = 1 if coord_choice == 'CASS' else 0

        # Identificação de dia da semana
        dia_semana_nome = dt.strftime('%A')
        dias_pt = {
            'Monday': 'Segunda-feira', 'Tuesday': 'Terça-feira', 'Wednesday': 'Quarta-feira',
            'Thursday': 'Quinta-feira', 'Friday': 'Sexta-feira', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
        }
        dia_pt = dias_pt.get(dia_semana_nome, dia_semana_nome)
        fim_semana = True if dt.weekday() in [4, 5, 6] else False # Sex, Sáb, Dom

        data.append({
            'id_bogcm': bogcm_id,
            'data_hora': dt,
            'hora': dt.hour,
            'dia_semana': dia_pt,
            'fim_de_semana': fim_semana,
            'inspetoria': insp,
            'bairro': bairro,
            'coordenadoria': coord_choice,
            'categoria': cat_nome,
            'tipo_ocorrencia': tipo,
            'equinos_resgatados': equinos,
            'animais_silvestres_resgatados': fauna,
            'veiculos_removidos': veiculos,
            'psr_atendimentos': psr_atendimentos,
            'latitude': lat,
            'longitude': lon,
            'origem': np.random.choice(['CISP 153', 'Patrulhamento Movel', 'Presencial'], p=[0.65, 0.25, 0.10])
        })

    return pd.DataFrame(data)

if __name__ == "__main__":
    df = generate_bogcm_mock_data()
    df.to_csv("bogcm_ficticio.csv", index=False)