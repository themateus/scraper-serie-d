import json

def carregar_json(nome_arquivo):
    try:
        with open(nome_arquivo, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def processar_tabela_geral():
    # 1. Carrega a base imutável da Fase 1
    times_fase1 = carregar_json("classificacao_fase1.json")
    
    # Transforma em dicionário indexado pelo nome do time para busca O(1)
    tabela_geral = {}
    for t in times_fase1:
        tabela_geral[t["time"]] = {
            "time": t["time"],
            "pontos": t["pontos"],
            "jogos": t["jogos"],
            "vitorias": t["vitorias"],
            "empates": t["empates"],
            "derrotas": t["derrotas"],
            "gols_pro": t["gols_pro"],
            "gols_contra": t["gols_contra"],
            "saldo_gols": t["saldo_gols"]
        }

    # 2. Carrega os resultados do mata-mata (Fase 2, Fase 3, etc.)
    jogos_matamata = carregar_json("resultados_serie_d.json")

    # 3. Computa os incrementos do mata-mata
    for jogo in jogos_matamata:
        mandante = jogo["mandante"]
        visitante = jogo["visitante"]
        gols_m = jogo["placar_mandante"]
        gols_v = jogo["placar_visitante"]

        # Se o time não foi mapeado na Fase 1 (prevenção de inconsistência de nome)
        if mandante not in tabela_geral or visitante not in tabela_geral:
            continue

        # Atualiza gols e jogos (Tempo Normal)
        tabela_geral[mandante]["jogos"] += 1
        tabela_geral[visitante]["jogos"] += 1
        
        tabela_geral[mandante]["gols_pro"] += gols_m
        tabela_geral[mandante]["gols_contra"] += gols_v
        
        tabela_geral[visitante]["gols_pro"] += gols_v
        tabela_geral[visitante]["gols_contra"] += gols_m

        # Calcula o resultado do tempo normal (Pênaltis NÃO dão pontos na tabela geral)
        if gols_m > gols_v:
            tabela_geral[mandante]["pontos"] += 3
            tabela_geral[mandante]["vitorias"] += 1
            tabela_geral[visitante]["derrotas"] += 1
        elif gols_m < gols_v:
            tabela_geral[visitante]["pontos"] += 3
            tabela_geral[visitante]["vitorias"] += 1
            tabela_geral[mandante]["derrotas"] += 1
        else:
            tabela_geral[mandante]["pontos"] += 1
            tabela_geral[mandante]["empates"] += 1
            tabela_geral[visitante]["pontos"] += 1
            tabela_geral[visitante]["empates"] += 1

        # Recalcula Saldos de Gols
        tabela_geral[mandante]["saldo_gols"] = tabela_geral[mandante]["gols_pro"] - tabela_geral[mandante]["gols_contra"]
        tabela_geral[visitante]["saldo_gols"] = tabela_geral[visitante]["gols_pro"] - tabela_geral[visitante]["gols_contra"]

    # 4. Transforma o dicionário de volta em lista
    lista_final = list(tabela_geral.values())

    # 5. Ordena aplicando estritamente as regras de desempate da CBF
    # O Python ordena estavelmente, avaliando da direita para a esquerda na tupla da chave lambda
    lista_final.sort(
        key=lambda x: (x["pontos"], x["vitorias"], x["saldo_gols"], x["gols_pro"]),
        reverse=True
    )

    # 6. Salva o resultado final que alimentará o Front-end
    with open("tabela_geral.json", "w", encoding="utf-8") as arquivo:
        json.dump(lista_final, arquivo, ensure_ascii=False, indent=4)
        
    print(f"🏆 Tabela Geral consolidada e ordenada! {len(lista_final)} times processados.")

if __name__ == "__main__":
    processar_tabela_geral()