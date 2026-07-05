#!/bin/bash

echo "🔄 Iniciando extração e processamento..."
# Se você não estiver usando ambiente virtual ativado direto, 
# pode até remover a linha do 'source venv/bin/activate'
source venv/bin/activate

# Puxa o mata-mata
python scraper_resultados.py

# Processa a matemática e gera o tabela_geral.json
python processador_tabela.py

echo "📤 Enviando dados para o GitHub..."
git add classificacao_fase1.json tabela_geral.json index.html
git commit -m "🤖 Tabela atualizada automaticamente: $(date '+%Y-%m-%d %H:%M:%S')"
git push origin main

echo "✅ Site atualizado com sucesso!"