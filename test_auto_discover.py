import requests
from bs4 import BeautifulSoup
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url_base = "https://www.cbf.com.br/futebol-brasileiro/tabelas/campeonato-brasileiro/serie-d/2026"
headers = {"User-Agent": "Mozilla/5.0"}
resp = requests.get(url_base, headers=headers, verify=False)
soup = BeautifulSoup(resp.text, 'html.parser')
for a in soup.find_all('a', href=True):
    txt = a.text.strip()
    if 'Fase' in txt or 'Oitavas' in txt or 'Quartas' in txt or 'Semifinal' in txt or 'Final' in txt or 'final' in txt.lower():
        if '/2026/' in a['href']:
            print(txt, a['href'])
