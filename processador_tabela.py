import json

def carregar_json(nome_arquivo):
    try:
        with open(nome_arquivo, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def processar_tabela_geral():
    times_fase1 = carregar_json("classificacao_fase1.json")
    
    tabela_geral = {}
    
    # Mapeamento das letras de grupos da CBF para o nome da fase
    fase_map = {
        'A': (1, '1ª Fase'),
        'B': (2, '2ª Fase'),
        'C': (3, '3ª Fase'),
        'D': (4, 'Oitavas'),
        'E': (5, 'Quartas'),
        'F': (6, 'Semifinal'),
        'G': (7, 'Final')
    }
    
    for t in times_fase1:
        chave = t.get("club_id", t["time"])
        tabela_geral[chave] = {
            "club_id": chave,
            "escudo_url": t.get("escudo_url", ""),
            "time": t["time"],
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
        
        # Descobre qual é a fase atual baseada na letra do grupo (Ex: GRUPO B01 -> B)
        grupo_match = jogo.get("grupo", "")
        letra = grupo_match.split()[1][0] if " " in grupo_match and len(grupo_match.split()) > 1 else 'B'
        nivel, nome_fase = fase_map.get(letra, (2, "Mata-Mata"))

        if chave_m in tabela_geral and chave_v in tabela_geral:
            # Atualiza o status/fase máxima que o time alcançou
            if tabela_geral[chave_m]["fase_nivel"] < nivel:
                tabela_geral[chave_m]["fase_nivel"] = nivel
                tabela_geral[chave_m]["status"] = nome_fase
                
            if tabela_geral[chave_v]["fase_nivel"] < nivel:
                tabela_geral[chave_v]["fase_nivel"] = nivel
                tabela_geral[chave_v]["status"] = nome_fase

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