import json
import re

def carregar_json(nome_arquivo):
    try:
        with open(nome_arquivo, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

ESTADOS_TIMES = {
    "Abc": "RN", "Abecat": "GO", "Água Santa": "SP", "Aguia": "PA", "Altos": "PI", 
    "Aparecidense": "GO", "Araguaina": "TO", "Asa": "AL",
    "Atlético de Alagoinhas": "BA", "Azuriz": "PR", "Betim": "MG", "Blumenau": "SC", "Brasiliense": "DF",
    "Capital": "TO", "Cascavel": "PR", "Ceilândia": "DF", "Central": "PE", "Crac": "GO",
    "Csa": "AL", "Cse": "AL", "Decisão": "PE", "Democrata": "MG", "Atlético Cearense": "CE",
    "Ferroviário": "CE", "Fluminense": "PI", "Galvez": "AC", "Gama": "DF", "Porto Velho": "RO",
    "Goiatuba": "GO", "Brasil": "RS", "Guaporé": "RO", "Guarany": "CE", "Humaitá": "AC",
    "Iape": "MA", "Iguatu": "CE", "Imperatriz": "MA", "Independência": "AC", "Inhumas": "GO",
    "Ivinhema": "MS", "Jacuipense": "BA", "Joinville": "SC", "Juazeirense": "BA", "Lagarto": "SE",
    "Laguna": "RN", "Cianorte": "PR", "Luverdense": "MT", "Madureira": "RJ",
    "Maguary": "PE", "Manauara": "AM", "Manaus": "AM", "Maracana": "CE", "Marcílio Dias": "SC",
    "Marica": "RJ", "Mixto": "MT", "Monte Roraima": "RR", "Moto Club": "MA", "Nacional": "AM",
    "Noroeste": "SP", "Nova Iguaçu": "RJ", "Operário": "MS", "Oratório": "AP", "Parnahyba": "PI",
    "Piauí": "PI", "Porto Sport": "BA", "Porto": "PE", "Pouso Alegre": "MG",
    "Primavera": "SP", "Real Noroeste": "ES", "Retrô": "PE", "Rio Branco": "AC",
    "Santa Catarina": "SC", "Sãojoseense": "PR", "São Luiz": "RS", "São Raimundo": "RR", "Sergipe": "SE", "Serra Branca": "PB",
    "Sousa": "PB", "Tirol": "CE", "Tocantinopolis": "TO", "Tombense": "MG", "Trem": "AP", "Treze": "PB",
    "Tuna Luso": "PA", "Uberlândia": "MG", "União": "MT", "Velo Clube": "SP", "Vitoria": "ES",
    "Xv de Piracicaba": "SP", "São José": "SP"
}

def limpar_e_adicionar_estado(nome_original, club_id):
    nome = nome_original
    
    # 1. Remover SAF, FC e derivações
    padroes = [
        r'\bsaf\b', r'\bf\s*\.\s*c\s*\.?', r'\bfc\b', 
        r'\be\s*\.\s*c\s*\.?', r'\bec\b',
        r'\besporte clube\b', r'\bfutebol clube\b', r'\bfutebol e regatas\b', 
        r'\bclube\b', r'\bsport club\b'
    ]
    for p in padroes:
        nome = re.sub(p, '', nome, flags=re.IGNORECASE)
    
    # Limpa espaços e hifens soltos
    nome = ' '.join(nome.split())
    nome = nome.strip(' -')
    
    # 2. Palavras de 3 letras na primeira palavra em maiúsculo (ex: Abc -> ABC)
    partes = nome.split()
    if partes and len(partes[0]) == 3:
        partes[0] = partes[0].upper()
    nome = ' '.join(partes)

    # 3. Adicionar Estado
    estado = ""
    # Hardcoded conhecidos que geram duplicatas ou nomes comuns
    if club_id == "20046": estado = "RN"
    elif club_id == "62025": estado = "RJ"
    elif club_id == "20041": estado = "MS"
    elif club_id == "35079": estado = "MT"
    elif club_id == "20353": estado = "RR"
    elif club_id == "20056": estado = "MA"
    elif club_id == "32387": estado = "RJ"
    elif club_id == "20805": estado = "RJ"
    elif club_id == "63521": estado = "SP"
    
    if not estado:
        for key in sorted(ESTADOS_TIMES.keys(), key=len, reverse=True):
            if key.lower() in nome_original.lower():
                estado = ESTADOS_TIMES[key]
                break
                
    if estado:
        nome = f"{nome} - {estado}"
        
    return nome

def processar_tabela_geral():
    times_fase1 = carregar_json("classificacao_fase1.json")
    
    tabela_geral = {}
    
    # Mapeamento do nível da fase (para saber qual fase foi mais longe)
    fase_nivel_map = {
        '1ª Fase': 1,
        '2ª Fase': 2,
        '3ª Fase': 3,
        'Oitavas': 4,
        'Quartas': 5,
        'Semifinal': 6,
        'Final': 7
    }
    
    for t in times_fase1:
        chave = t.get("club_id", t["time"])
        nome_formatado = limpar_e_adicionar_estado(t["time"], chave)
        
        tabela_geral[chave] = {
            "club_id": chave,
            "escudo_url": t.get("escudo_url", ""),
            "time": nome_formatado,
            "pontos": t["pontos"],
            "jogos": t["jogos"],
            "vitorias": t["vitorias"],
            "empates": t["empates"],
            "derrotas": t["derrotas"],
            "gols_pro": t["gols_pro"],
            "gols_contra": t["gols_contra"],
            "saldo_gols": t["saldo_gols"],
            "fase_nivel": 1,
            "status": "1ª Fase"
        }

    jogos_matamata = carregar_json("resultados_serie_d.json")

    for jogo in jogos_matamata:
        chave_m = jogo.get("mandante_id", jogo["mandante"])
        chave_v = jogo.get("visitante_id", jogo["visitante"])

        gols_m = jogo["placar_mandante"]
        gols_v = jogo["placar_visitante"]
        
        # Descobre qual é a fase atual baseada no texto que a CBF colocou na página (ex: "2ª Fase")
        fase_texto_cbf = jogo.get("nome_fase", "Mata-Mata")
        
        nivel = 2
        nome_fase = "Mata-Mata"
        for key, val in fase_nivel_map.items():
            if key in fase_texto_cbf:
                nivel = val
                nome_fase = key
                break

        if chave_m in tabela_geral and chave_v in tabela_geral:
            # Atualiza o status/fase máxima que o time alcançou SEMPRE (mesmo se o jogo não ocorreu)
            if tabela_geral[chave_m]["fase_nivel"] < nivel:
                tabela_geral[chave_m]["fase_nivel"] = nivel
                tabela_geral[chave_m]["status"] = nome_fase
                
            if tabela_geral[chave_v]["fase_nivel"] < nivel:
                tabela_geral[chave_v]["fase_nivel"] = nivel
                tabela_geral[chave_v]["status"] = nome_fase

            # Se o jogo já aconteceu, computa pontos e gols
            if gols_m is not None and gols_v is not None:
                tabela_geral[chave_m]["jogos"] += 1
                tabela_geral[chave_v]["jogos"] += 1
                
                tabela_geral[chave_m]["gols_pro"] += gols_m
                tabela_geral[chave_m]["gols_contra"] += gols_v
                
                tabela_geral[chave_v]["gols_pro"] += gols_v
                tabela_geral[chave_v]["gols_contra"] += gols_m

                if gols_m > gols_v:
                    tabela_geral[chave_m]["pontos"] += 3
                    tabela_geral[chave_m]["vitorias"] += 1
                    tabela_geral[chave_v]["derrotas"] += 1
                elif gols_m < gols_v:
                    tabela_geral[chave_v]["pontos"] += 3
                    tabela_geral[chave_v]["vitorias"] += 1
                    tabela_geral[chave_m]["derrotas"] += 1
                else:
                    tabela_geral[chave_m]["pontos"] += 1
                    tabela_geral[chave_m]["empates"] += 1
                    tabela_geral[chave_v]["pontos"] += 1
                    tabela_geral[chave_v]["empates"] += 1

                tabela_geral[chave_m]["saldo_gols"] = tabela_geral[chave_m]["gols_pro"] - tabela_geral[chave_m]["gols_contra"]
                tabela_geral[chave_v]["saldo_gols"] = tabela_geral[chave_v]["gols_pro"] - tabela_geral[chave_v]["gols_contra"]

    lista_final = list(tabela_geral.values())
    lista_final.sort(
        key=lambda x: (x["pontos"], x["vitorias"], x["saldo_gols"], x["gols_pro"]),
        reverse=True
    )

    with open("tabela_geral.json", "w", encoding="utf-8") as arquivo:
        json.dump(lista_final, arquivo, ensure_ascii=False, indent=4)
        
    print(f"\n🏆 Tabela Geral consolidada e ordenada! {len(lista_final)} times processados.")

if __name__ == "__main__":
    processar_tabela_geral()