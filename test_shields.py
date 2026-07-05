import requests
from bs4 import BeautifulSoup
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Fase 1
resp1 = requests.get("https://www.cbf.com.br/futebol-brasileiro/tabelas/campeonato-brasileiro/serie-d/2026/2040", verify=False)
soup1 = BeautifulSoup(resp1.text, "html.parser")
linha = soup1.find('table').find('tbody').find('tr')
tds = linha.find_all('td')
print("FASE 1 TEAM:", tds[0])

# Mata-mata
resp2 = requests.get("https://www.cbf.com.br/futebol-brasileiro/tabelas/campeonato-brasileiro/serie-d/2026/2066", verify=False)
soup2 = BeautifulSoup(resp2.text, "html.parser")
cartao = soup2.find('div', class_=lambda x: x and 'card-wrapper' in x.lower())
score_container = cartao.find('div', class_=lambda x: x and 'score' in x.lower())
times_divs = score_container.find_all('div', recursive=False)
print("MATA MATA TEAM 1:", times_divs[0])
