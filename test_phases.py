import requests
from bs4 import BeautifulSoup
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

resp = requests.get("https://www.cbf.com.br/futebol-brasileiro/tabelas/campeonato-brasileiro/serie-d/2026", verify=False)
soup = BeautifulSoup(resp.text, "html.parser")
nav = soup.find('nav', class_=lambda x: x and 'nav' in x.lower())
# just print all a tags with href that might look like phase links
for a in soup.find_all('a', href=True):
    if '/serie-d/' in a['href'] and a['href'].split('/')[-1].isdigit():
        print(a.text.strip(), "->", a['href'])
