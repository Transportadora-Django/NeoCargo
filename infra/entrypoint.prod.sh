#!/bin/sh

# Script de entrypoint para produção na Render
# Este script executa migrações, coleta arquivos estáticos e inicia o servidor

echo "🚀 Iniciando deploy em produção..."

# Verificar variáveis de ambiente críticas
echo "🔍 Verificando configuração..."
echo "DJANGO_SETTINGS_MODULE: ${DJANGO_SETTINGS_MODULE:-'não definido'}"
echo "PORT (Render): ${PORT:-'não definido (usando 8000)'}"
echo "DATABASE_URL: ${DATABASE_URL:+configurado}"

# Validar arquivos estáticos críticos antes do deploy
echo "📋 Validando arquivos estáticos..."
if [ -f "/app/infra/validate-static.sh" ]; then
    /app/infra/validate-static.sh
    if [ $? -ne 0 ]; then
        echo "❌ Validação de arquivos estáticos falhou! Continuando com deploy (modo resiliente)..."
    fi
else
    echo "⚠️  Script de validação não encontrado, continuando..."
fi

# Executar migrações do banco de dados
echo "📦 Executando migrações..."
python manage.py migrate --settings=frete_proj.settings.prod

# Criar superuser inicial (se não existir)
echo "👤 Configurando superuser inicial..."
python manage.py setup_initial_superuser --settings=frete_proj.settings.prod

# Popular dados iniciais
echo "🌍 Populando rotas e cidades..."
python manage.py populate_rotas --settings=frete_proj.settings.prod

echo "🚚 Populando especificações e veículos..."
python manage.py populate_veiculos --settings=frete_proj.settings.prod

# Coletar arquivos estáticos
echo "📁 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --settings=frete_proj.settings.prod

echo "✅ Deploy concluído! Iniciando servidor Gunicorn..."

# PORT é definido automaticamente pelo Render (geralmente 10000)
# Se não estiver definido, usa 8000 como fallback para desenvolvimento local
PORT=${PORT:-8000}
echo "🌐 Servidor Gunicorn iniciando em 0.0.0.0:$PORT"

# Configurações otimizadas do Gunicorn para Render
exec gunicorn frete_proj.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 3 \
    --timeout 120 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --preload \
    --log-level info