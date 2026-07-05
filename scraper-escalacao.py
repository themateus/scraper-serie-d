import requests
from bs4 import BeautifulSoup
import urllib3
import json

# Suprime o aviso de certificado inválido
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def extrair_partidas_fase(url_fase):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    print(f"Baixando a página da fase: {url_fase} ...\n")
    response = requests.get(url_fase, headers=headers, verify=False)
    
    if response.status_code != 200:
        print(f"Erro na requisição. Status: {response.status_code}")
        return
        
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Encontra todos os blocos de partida usando parte da classe (card-wrapper)
    cartoes_jogos = soup.find_all('div', class_=lambda x: x and 'card-wrapper' in x.lower())
    
    print(f"🏟️ Encontrados {len(cartoes_jogos)} jogos na página!\n")
    
    lista_partidas = []
    
    for cartao in cartoes_jogos:
        try:
            # 1. Grupo e Ida/Volta
            tags = cartao.find('div', class_=lambda x: x and 'tag' in x.lower()).find_all('span')
            grupo = tags[0].text.strip()
            ida_volta = tags[1].text.strip()
            
            # 2. Placar e Times
            score_container = cartao.find('div', class_=lambda x: x and 'score' in x.lower())
            
            # Pega apenas as divs diretas (Mandante na pos 0 e Visitante na pos 1)
            times_divs = score_container.find_all('div', recursive=False) 
            
            # --- MANDANTE ---
            mandante_nome = times_divs[0].find('strong')['title']
            mandante_placar = times_divs[0].find('span', class_=lambda x: x and 'gol' in x.lower()).text.strip()
            # Verifica se teve pênaltis
            mandante_penaltis = times_divs[0].find('span', class_=lambda x: x and 'penaltis' in x.lower())
            mandante_penaltis = mandante_penaltis.text.strip().replace('(', '').replace(')', '') if mandante_penaltis else ""
            
            # --- VISITANTE ---
            visitante_nome = times_divs[1].find('strong')['title']
            visitante_placar = times_divs[1].find('span', class_=lambda x: x and 'gol' in x.lower()).text.strip()
            # Verifica se teve pênaltis
            visitante_penaltis = times_divs[1].find('span', class_=lambda x: x and 'penaltis' in x.lower())
            visitante_penaltis = visitante_penaltis.text.strip().replace('(', '').replace(')', '') if visitante_penaltis else ""
            
            # 3. Informações (Data, Jogo, Estádio)
            info_container = cartao.find('div', class_=lambda x: x and 'informations' in x.lower())
            # A classe do número do jogo muda muito, então pegamos o primeiro span
            num_jogo = info_container.find('span').text.strip() 
            # O get_text com separator=' | ' troca as quebras de linha <br> por barras bonitinhas
            detalhes = info_container.find('p').get_text(separator=' | ').strip()
            
            # Monta a string pro terminal
            placar_str = f"{mandante_nome} {mandante_placar} x {visitante_placar} {visitante_nome}"
            if mandante_penaltis or visitante_penaltis:
                placar_str += f" (Pênaltis: {mandante_penaltis} x {visitante_penaltis})"
                
            print(f"[{grupo} - {ida_volta} | {num_jogo}] {placar_str}")
            
            lista_partidas.append({
                "grupo": grupo,
                "fase": ida_volta,
                "jogo": num_jogo,
                "mandante": mandante_nome,
                "placar_mandante": int(mandante_placar),
                "penaltis_mandante": int(mandante_penaltis) if mandante_penaltis else None,
                "visitante": visitante_nome,
                "placar_visitante": int(visitante_placar),
                "penaltis_visitante": int(visitante_penaltis) if visitante_penaltis else None,
                "detalhes": detalhes
            })
            
        except Exception as e:
            # Ignora erros em blocos de propagandas ou mal formatados
            pass
            
    # Salvar o JSON
    with open("resultados_serie_d.json", "w", encoding="utf-8") as arquivo:
        json.dump(lista_partidas, arquivo, ensure_ascii=False, indent=4)
        
    print("\n✅ Arquivo 'resultados_serie_d.json' gerado com sucesso!")

if __name__ == "__main__":
    # Coloque aqui a URL da fase que você quer puxar os resultados
    url_alvo = "https://www.cbf.com.br/futebol-brasileiro/tabelas/campeonato-brasileiro/serie-d/2026/2066"
    extrair_partidas_fase(url_alvo)