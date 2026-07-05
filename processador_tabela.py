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