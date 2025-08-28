#!/bin/bash

# Script para comandos úteis do NeoCargo Docker

cd "$(dirname "$0")"

case "$1" in
    "start")
        echo "🚀 Iniciando NeoCargo..."
        docker-compose up -d
        ;;
    "stop")
        echo "🛑 Parando NeoCargo..."
        docker-compose down
        ;;
    "restart")
        echo "🔄 Reiniciando NeoCargo..."
        docker-compose restart
        ;;
    "logs")
        echo "📋 Exibindo logs..."
        if [ -n "$2" ]; then
            docker-compose logs -f "$2"
        else
            docker-compose logs -f
        fi
        ;;
    "shell")
        echo "🐚 Abrindo shell Django..."
        docker-compose exec web python manage.py shell
        ;;
    "bash")
        echo "💻 Abrindo bash no container web..."
        docker-compose exec web bash
        ;;
    "migrate")
        echo "🔄 Executando migrações..."
        docker-compose run --rm web python manage.py migrate
        ;;
    "makemigrations")
        echo "📝 Criando migrações..."
        docker-compose run --rm web python manage.py makemigrations
        ;;
    "createsuperuser")
        echo "👤 Criando superusuário..."
        docker-compose run --rm web python manage.py createsuperuser
        ;;
    "collectstatic")
        echo "📁 Coletando arquivos estáticos..."
        docker-compose run --rm web python manage.py collectstatic --noinput
        ;;
    "test")
        echo "🧪 Executando testes..."
        docker-compose run --rm web python manage.py test
        ;;
    "build")
        echo "🔨 Reconstruindo containers..."
        docker-compose build --no-cache
        ;;
    "reset")
        echo "⚠️  Resetando ambiente (isso removerá todos os dados)..."
        read -p "Tem certeza? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose down -v
            docker-compose build --no-cache
            docker-compose up -d db
            sleep 10
            docker-compose run --rm web python manage.py migrate
            docker-compose up -d
            echo "✅ Ambiente resetado!"
        else
            echo "❌ Operação cancelada"
        fi
        ;;
    "status")
        echo "📊 Status dos containers..."
        docker-compose ps
        ;;
    *)
        echo "🚢 NeoCargo Docker Manager"
        echo ""
        echo "Uso: ./manage.sh <comando>"
        echo ""
        echo "Comandos disponíveis:"
        echo "  start              - Iniciar todos os serviços"
        echo "  stop               - Parar todos os serviços"
        echo "  restart            - Reiniciar todos os serviços"
        echo "  logs [serviço]     - Ver logs (todos ou de um serviço específico)"
        echo "  shell              - Abrir shell Django"
        echo "  bash               - Abrir bash no container web"
        echo "  migrate            - Executar migrações"
        echo "  makemigrations     - Criar migrações"
        echo "  createsuperuser    - Criar superusuário"
        echo "  collectstatic      - Coletar arquivos estáticos"
        echo "  test               - Executar testes"
        echo "  build              - Reconstruir containers"
        echo "  reset              - Resetar ambiente completo"
        echo "  status             - Ver status dos containers"
        echo ""
        echo "Exemplos:"
        echo "  ./manage.sh start"
        echo "  ./manage.sh logs web"
        echo "  ./manage.sh shell"
        ;;
esac
