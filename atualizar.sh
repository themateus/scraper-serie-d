#!/bin/bash

echo "🔄 Iniciando extração e processamento..."
# Ativa o ambiente virtual (ajuste se o nome for diferente)
source venv/bin/activate

# Roda os scrapers e o processador
python3 scraper_fase1.py
python3 processador_tabela.py

echo "📤 Enviando dados para o GitHub..."
git add classificacao_fase1.json tabela_geral.json index.html
git commit -m "🤖 Tabela atualizada automaticamente: $(date '+%Y-%m-%d %H:%M:%S')"
git push origin main

echo "✅ Site atualizado com sucesso!"