import requests
from bs4 import BeautifulSoup
import urllib3
import json

# Suprime o aviso de certificado inválido
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def extrair_classificacao_fase1(url_fase1):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    print(f"Baixando a Fase 1: {url_fase1} ...\n")
    response = requests.get(url_fase1, headers=headers, verify=False)
    
    if response.status_code != 200:
        print(f"Erro na requisição. Status: {response.status_code}")
        return
        
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 1. Encontra todos os títulos de grupos (ex: <h2>GRUPO A1</h2>)
    grupos_titulos = soup.find_all('h2', string=lambda t: t and 'GRUPO' in t.upper())
    
    print(f"📊 Encontrados {len(grupos_titulos)} grupos!\n")
    
    tabela_geral = []
    
    # 2. Varre cada grupo e extrai sua respectiva tabela
    for titulo in grupos_titulos:
        nome_grupo = titulo.text.strip()
        
        # A tabela sempre vem no HTML logo após o header do grupo
        tabela = titulo.find_next('table')
        if not tabela:
            continue
            
        linhas = tabela.find('tbody').find_all('tr')
        
        for linha in linhas:
            tds = linha.find_all('td')
            
            # Prevenção de quebra: garante que a linha tem dados suficientes
            if len(tds) < 9:
                continue
                
            # 3. Extração pura via índices das colunas (Padrão CBF)
            # O nome do time está dentro de uma tag <a> no td[0]
            a_tag = tds[0].find('a')
            nome_time = a_tag.text.strip()
            
            # ID único do clube e Escudo
            href = a_tag.get('href', '')
            club_id = href.rstrip('/').split('/')[-1] if href else nome_time
            
            img_tag = a_tag.find('img')
            escudo_url = img_tag.get('src') if img_tag else ""
            if escudo_url and escudo_url.startswith('/'):
                escudo_url = f"https://www.cbf.com.br{escudo_url}"
            
            # Os demais são convertidos para números inteiros (int) para permitir cálculos matemáticos
            pontos = int(tds[1].text.strip())
            jogos = int(tds[2].text.strip())
            vitorias = int(tds[3].text.strip())
            empates = int(tds[4].text.strip())
            derrotas = int(tds[5].text.strip())
            gols_pro = int(tds[6].text.strip())
            gols_contra = int(tds[7].text.strip())
            saldo_gols = int(tds[8].text.strip())
            
            print(f"[{nome_grupo}] {nome_time:.<25} {pontos:02d} pts | SG: {saldo_gols}")
            
            tabela_geral.append({
                "club_id": club_id,
                "escudo_url": escudo_url,
                "grupo_origem": nome_grupo,
                "time": nome_time,
                "pontos": pontos,
                "jogos": jogos,
                "vitorias": vitorias,
                "empates": empates,
                "derrotas": derrotas,
                "gols_pro": gols_pro,
                "gols_contra": gols_contra,
                "saldo_gols": saldo_gols
            })

    # 4. Salva a "Base Imutável"
    with open("classificacao_fase1.json", "w", encoding="utf-8") as arquivo:
        json.dump(tabela_geral, arquivo, ensure_ascii=False, indent=4)
        
    print(f"\n✅ Arquivo 'classificacao_fase1.json' gerado com sucesso contendo {len(tabela_geral)} times!")

if __name__ == "__main__":
    url_alvo = "https://www.cbf.com.br/futebol-brasileiro/tabelas/campeonato-brasileiro/serie-d/2026/2040"
    extrair_classificacao_fase1(url_alvo)