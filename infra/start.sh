#!/bin/bash

# Script para inicializar o ambiente Docker do NeoCargo

echo "🚀 Iniciando NeoCargo..."

# Verificar se docker e docker-compose estão instalados
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não está instalado"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose não está instalado"
    exit 1
fi

# Navegar para o diretório da infraestrutura
cd "$(dirname "$0")"

echo "📦 Construindo containers..."
docker-compose build

echo "🗄️ Iniciando banco de dados..."
docker-compose up -d db

echo "⏳ Aguardando banco de dados ficar pronto..."
sleep 10

echo "📧 Iniciando MailHog..."
docker-compose up -d mailhog

echo "🔄 Executando migrações..."
docker-compose run --rm web python manage.py migrate

echo "👤 Criando superusuário (opcional)..."
echo "Você pode criar um superusuário executando:"
echo "docker-compose run --rm web python manage.py createsuperuser"

echo "🌐 Iniciando aplicação web..."
docker-compose up -d web

echo ""
echo "✅ NeoCargo iniciado com sucesso!"
echo ""
echo "📍 Serviços disponíveis:"
echo "   🌐 Aplicação Web: http://localhost:8000"
echo "   📧 MailHog (Web UI): http://localhost:8025"
echo "   🗄️ PostgreSQL: localhost:5432"
echo ""
echo "📋 Comandos úteis:"
echo "   Para ver logs: docker-compose logs -f"
echo "   Para parar: docker-compose down"
echo "   Para reiniciar: docker-compose restart"
echo "   Para shell Django: docker-compose exec web python manage.py shell"
echo ""
