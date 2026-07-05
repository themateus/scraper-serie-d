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
            a_mandante = times_divs[0].find('a')
            mandante_nome = a_mandante.find('strong')['title'] if a_mandante and a_mandante.find('strong') else times_divs[0].find('strong')['title']
            mandante_href = a_mandante.get('href', '') if a_mandante else ''
            mandante_id = mandante_href.rstrip('/').split('/')[-1] if mandante_href else mandante_nome
            
            mandante_placar = times_divs[0].find('span', class_=lambda x: x and 'gol' in x.lower()).text.strip()
            # Verifica se teve pênaltis
            mandante_penaltis = times_divs[0].find('span', class_=lambda x: x and 'penaltis' in x.lower())
            mandante_penaltis = mandante_penaltis.text.strip().replace('(', '').replace(')', '') if mandante_penaltis else ""
            
            # --- VISITANTE ---
            a_visitante = times_divs[1].find('a')
            visitante_nome = a_visitante.find('strong')['title'] if a_visitante and a_visitante.find('strong') else times_divs[1].find('strong')['title']
            visitante_href = a_visitante.get('href', '') if a_visitante else ''
            visitante_id = visitante_href.rstrip('/').split('/')[-1] if visitante_href else visitante_nome
            
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
            
            # Ignora jogos que ainda não aconteceram (placar vazio)
            if not mandante_placar.strip() or not visitante_placar.strip():
                continue
                
            lista_partidas.append({
                "grupo": grupo,
                "fase": ida_volta,
                "jogo": num_jogo,
                "mandante_id": mandante_id,
                "mandante": mandante_nome,
                "placar_mandante": int(mandante_placar),
                "penaltis_mandante": int(mandante_penaltis) if mandante_penaltis else None,
                "visitante_id": visitante_id,
                "visitante": visitante_nome,
                "placar_visitante": int(visitante_placar),
                "penaltis_visitante": int(visitante_penaltis) if visitante_penaltis else None,
                "detalhes": detalhes
            })
            
        except Exception as e:
            print(f"⚠️ Erro ao processar bloco: {e}")
            pass
            
    return lista_partidas

def obter_fases_mata_mata():
    url_base = "https://www.cbf.com.br/futebol-brasileiro/tabelas/campeonato-brasileiro/serie-d/2026"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url_base, headers=headers, verify=False)
        soup = BeautifulSoup(resp.text, 'html.parser')
        fases = []
        for a in soup.find_all('a', href=True):
            txt = a.text.strip()
            if any(x in txt for x in ['Fase', 'Oitavas', 'Quartas', 'Semifinal', 'Final', 'final']):
                if '/2026/' in a['href'] and a['href'].split('/')[-1].isdigit():
                    if '1ª Fase' not in txt and 'Grupo' not in txt:
                        full_url = a['href']
                        if not full_url.startswith('http'):
                            full_url = 'https://www.cbf.com.br' + full_url
                        fases.append(full_url)
        # Manter a ordem preservando unicos
        fases_unicas = []
        for f in fases:
            if f not in fases_unicas:
                fases_unicas.append(f)
        return fases_unicas
    except Exception as e:
        print(f"Erro ao buscar fases: {e}")
        return []

if __name__ == "__main__":
    fases_mata_mata = obter_fases_mata_mata()
    print(f"🔍 Fases de mata-mata encontradas automaticamente: {len(fases_mata_mata)}")
    
    todas_as_partidas = []
    
    # Roda o scraper para cada link e junta na mesma panela
    for link in fases_mata_mata:
        partidas_da_fase = extrair_partidas_fase(link)
        if partidas_da_fase:
            todas_as_partidas.extend(partidas_da_fase)
            
    # Salva o arquivo mestre de resultados
    with open("resultados_serie_d.json", "w", encoding="utf-8") as arquivo:
        json.dump(todas_as_partidas, arquivo, ensure_ascii=False, indent=4)
        
    print(f"\n✅ Foram salvas {len(todas_as_partidas)} partidas do mata-mata!")