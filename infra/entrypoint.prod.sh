#!/bin/sh

# Script de entrypoint para produção na Render
# Este script executa migrações, coleta arquivos estáticos e inicia o servidor

echo "🚀 Iniciando deploy em produção..."

# Executar migrações do banco de dados
echo "📦 Executando migrações..."
python manage.py migrate --settings=frete_proj.settings.prod

# Coletar arquivos estáticos
echo "📁 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --settings=frete_proj.settings.prod

echo "✅ Deploy concluído! Iniciando servidor Gunicorn..."

# Iniciar o servidor Gunicorn
exec gunicorn frete_proj.wsgi:application --bind 0.0.0.0:8000 --workers 3