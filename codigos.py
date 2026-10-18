"""Dicionário oficial de códigos de ocorrência do BOGCM (39 códigos).

Fonte: apresentação do OMOP "Indicadores de Ordem Pública e o novo BOGCM",
slides 32 a 38. Se a Guarda criar, remover ou renomear um código, este é o
único arquivo a editar.
"""

GRUPOS = {
    "100": "Crimes",
    "200": "Posturas",
    "300": "Meio Ambiente",
    "400": "Trânsito",
    "500": "Auxílios e Atividades",
}

# (código, ocorrência, orientação de preenchimento)
_TABELA = [
    # 100 - Crimes
    ("101", "Homicídio", "Morte causada por terceiro; registrar local, vítima, meio e prisão."),
    ("102", "Lesão Corporal", "Ofensa à integridade física; descrever lesões, partes e atendimento médico."),
    ("103", "Ofensa", "Injúria, calúnia ou difamação; registrar o que foi dito e testemunhas."),
    ("104", "Ameaça", "Promessa de mal grave; transcrever a ameaça e o meio usado."),
    ("105", "Violação de Domicílio", "Entrada em casa alheia sem consentimento; descrever a forma de entrada."),
    ("106", "Furto", "Subtração sem violência; descrever o bem, valor estimado e local."),
    ("107", "Roubo", "Subtração com violência ou ameaça; informar arma, vítima e fuga."),
    ("108", "Dano a bem público ou privado", "Destruição de bem; identificar o bem, o dono e a extensão do dano."),
    ("109", "Crimes Sexuais", "Tratar com sigilo; preservar a vítima e acionar órgãos competentes."),
    ("110", "Resistência, Desobediência e Desacato", "Oposição ou ofensa a agente público; descrever a conduta e o contexto."),
    ("111", "Apreensão de Entorpecentes", "Registrar tipo, quantidade/peso e destinação à delegacia."),
    ("112", "Porte/Apreensão de Arma de Fogo", "Tipo, calibre, numeração e munição; encaminhar à autoridade."),
    ("113", "Porte/Apreensão de Arma Branca", "Tipo da arma, local do porte e circunstância."),
    ("114", "Violência Contra a Mulher", "Lei Maria da Penha; registrar vínculo e medida protetiva."),
    ("115", "Exercício Irregular da Profissão", "Atuação sem habilitação; identificar atividade e pessoa."),
    ("150", "Outros Crimes e/ou Contravenções", "Sem código específico; detalhar o fato no relato."),
    # 200 - Posturas
    ("201", "Publicidade e propaganda sem autorização", "Anúncio, faixa ou cartaz sem licença; registrar local, responsável e tipo."),
    ("202", "Comércio ambulante ilegal e/ou sem autorização", "Venda sem autorização; identificar vendedor, produto e local."),
    ("203", "Acampamento Irregular", "Ocupação de via ou área pública; registrar local e número de pessoas."),
    ("204", "Perturbação da Ordem, do Trabalho ou do Sossego", "Som ou algazarra; registrar origem, horário e medição se houver."),
    ("205", "Apreensão de Bens e Mercadorias", "Listar itens apreendidos, quantidade e destino dado."),
    ("250", "Outras Infrações ao Código de Posturas", "Sem código específico; descrever a infração de posturas."),
    # 300 - Meio Ambiente
    ("301", "Abandono/Maus Tratos de Animais", "Descrever o estado do animal, o local e o responsável; acionar setor competente."),
    ("302", "Incêndio", "Registrar local, proporção, vítimas e acionamento do Corpo de Bombeiros."),
    ("303", "Crimes e Infrações Ambientais", "Poluição, desmate ou descarte irregular; registrar o dano e o responsável."),
    ("304", "Resgate/Entrega Voluntária de Animais", "Informar espécie, quantidade, estado e destino do animal."),
    ("350", "Outros Meio Ambiente", "Sem código específico; detalhar a ocorrência ambiental."),
    # 400 - Trânsito
    ("401", "Acidente de Trânsito", "Registrar veículos, vítimas, danos e sinalização; acionar socorro se houver feridos."),
    ("402", "Irregularidade de Trânsito", "Estacionamento ou conduta irregular; identificar veículo, placa e local."),
    ("450", "Outros Trânsito", "Sem código específico; descrever a situação de trânsito."),
    # 500 - Auxílios e Atividades
    ("501", "Auxílio ao GCM", "Apoio a outra equipe da Guarda; registrar o tipo de apoio e o local."),
    ("502", "Auxílio a outros órgãos", "Apoio a PM, PC, Bombeiros etc.; informar o órgão e a demanda."),
    ("503", "Auxílio à Assistência Social", "Encaminhamento social; registrar a pessoa e o órgão acionado."),
    ("504", "Pessoa Desaparecida", "Dados e características da pessoa, local e última visualização."),
    ("505", "Encontro de Cadáver", "Preservar o local; acionar PM/PC e perícia; não alterar a cena."),
    ("506", "Auxílio ao cidadão", "Orientação ou apoio ao público; descrever a demanda atendida."),
    ("507", "Indivíduos em situação ilegal com a Justiça", "Mandado ou foragido; conferir identidade e encaminhar à autoridade."),
    ("508", "Indivíduo em Atitude Suspeita", "Abordagem preventiva; descrever a conduta e o resultado."),
    ("550", "Outros Auxílios ou Atividades", "Sem código específico; detalhar a atividade realizada."),
]

OFFICIAL_CODES = [
    {
        "codigo": cod,
        "nome": nome,
        "guia": guia,
        "grupo_cod": cod[0] + "00",
        "grupo": f"{cod[0]}00 - {GRUPOS[cod[0] + '00']}",
    }
    for cod, nome, guia in _TABELA
]

CODIGO_NOME = {c["codigo"]: c["nome"] for c in OFFICIAL_CODES}

# Códigos "Outros": exceção, não regra (slide 28). Distorcem os indicadores.
CODIGOS_OUTROS = {"150", "250", "350", "450", "550"}

assert len(OFFICIAL_CODES) == 39, "O dicionário deveria ter 39 códigos"
