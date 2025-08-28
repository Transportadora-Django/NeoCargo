# Makefile para NeoCargo
# Sistema de gerenciamento de transportadora

.PHONY: help setup start stop restart logs shell bash migrate makemigrations createsuperuser collectstatic test build reset status clean install-deps

# Configurações
DOCKER_COMPOSE = docker-compose -f infra/docker-compose.yml -p neocargo
PYTHON = python
PIP = pip

# Cores para output
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

help: ## Exibe esta ajuda
	@echo "$(GREEN)NeoCargo - Sistema de Gerenciamento de Transportadora$(NC)"
	@echo ""
	@echo "$(YELLOW)Comandos disponíveis:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Exemplos:$(NC)"
	@echo "  make setup     # Configuração inicial"
	@echo "  make start     # Iniciar aplicação"
	@echo "  make logs      # Ver logs em tempo real"
	@echo "  make shell     # Acessar shell Django"

# === Configuração e Setup ===
setup: ## Configuração inicial do projeto
	@echo "$(GREEN)🚀 Configurando NeoCargo...$(NC)"
	@if [ ! -f backend/.env ]; then \
		echo "$(YELLOW)📝 Criando arquivo .env...$(NC)"; \
		cp backend/.env.example backend/.env; \
		echo "$(GREEN)✅ Arquivo .env criado. Edite conforme necessário.$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  Arquivo .env já existe.$(NC)"; \
	fi
	@echo "$(GREEN)🔨 Construindo containers...$(NC)"
	@$(DOCKER_COMPOSE) build
	@echo "$(GREEN)✅ Setup concluído!$(NC)"

install-deps: ## Instala dependências localmente (desenvolvimento sem Docker)
	@echo "$(GREEN)📦 Instalando dependências...$(NC)"
	@cd backend && $(PIP) install -r requirements.txt
	@echo "$(GREEN)✅ Dependências instaladas!$(NC)"

# === Gerenciamento de Containers ===
start: ## Inicia todos os serviços
	@echo "$(GREEN)🚀 Iniciando NeoCargo...$(NC)"
	@$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)✅ Serviços iniciados!$(NC)"
	@echo ""
	@echo "$(YELLOW)📍 Acesse:$(NC)"
	@echo "  🌐 Web: http://localhost:8000"
	@echo "  📧 MailHog: http://localhost:8025"

stop: ## Para todos os serviços
	@echo "$(YELLOW)🛑 Parando serviços...$(NC)"
	@$(DOCKER_COMPOSE) down
	@echo "$(GREEN)✅ Serviços parados!$(NC)"

restart: ## Reinicia todos os serviços
	@echo "$(YELLOW)🔄 Reiniciando serviços...$(NC)"
	@$(DOCKER_COMPOSE) restart
	@echo "$(GREEN)✅ Serviços reiniciados!$(NC)"

build: ## Reconstrói os containers
	@echo "$(GREEN)🔨 Reconstruindo containers...$(NC)"
	@$(DOCKER_COMPOSE) build --no-cache
	@echo "$(GREEN)✅ Containers reconstruídos!$(NC)"

# === Logs e Debug ===
logs: ## Exibe logs em tempo real
	@echo "$(GREEN)📋 Exibindo logs...$(NC)"
	@$(DOCKER_COMPOSE) logs -f

logs-web: ## Exibe logs apenas do serviço web
	@$(DOCKER_COMPOSE) logs -f web

logs-db: ## Exibe logs apenas do banco de dados
	@$(DOCKER_COMPOSE) logs -f db

status: ## Mostra status dos containers
	@echo "$(GREEN)📊 Status dos containers:$(NC)"
	@$(DOCKER_COMPOSE) ps

# === Shell e Acesso ===
shell: ## Acessa shell Django
	@echo "$(GREEN)🐚 Abrindo shell Django...$(NC)"
	@$(DOCKER_COMPOSE) exec web python manage.py shell

bash: ## Acessa bash no container web
	@echo "$(GREEN)💻 Abrindo bash...$(NC)"
	@$(DOCKER_COMPOSE) exec web bash

# === Django Management ===
migrate: ## Executa migrações do Django
	@echo "$(GREEN)🔄 Executando migrações...$(NC)"
	@$(DOCKER_COMPOSE) run --rm web python manage.py migrate
	@echo "$(GREEN)✅ Migrações executadas!$(NC)"

makemigrations: ## Cria novas migrações
	@echo "$(GREEN)📝 Criando migrações...$(NC)"
	@$(DOCKER_COMPOSE) run --rm web python manage.py makemigrations
	@echo "$(GREEN)✅ Migrações criadas!$(NC)"

createsuperuser: ## Cria superusuário
	@echo "$(GREEN)👤 Criando superusuário...$(NC)"
	@$(DOCKER_COMPOSE) run --rm web python manage.py createsuperuser

collectstatic: ## Coleta arquivos estáticos
	@echo "$(GREEN)📁 Coletando arquivos estáticos...$(NC)"
	@$(DOCKER_COMPOSE) run --rm web python manage.py collectstatic --noinput
	@echo "$(GREEN)✅ Arquivos coletados!$(NC)"

# === Testes ===
test: ## Executa testes
	@echo "$(GREEN)🧪 Executando testes...$(NC)"
	@$(DOCKER_COMPOSE) run --rm web python manage.py test
	@echo "$(GREEN)✅ Testes concluídos!$(NC)"

test-coverage: ## Executa testes com coverage
	@echo "$(GREEN)🧪 Executando testes com coverage...$(NC)"
	@$(DOCKER_COMPOSE) run --rm web coverage run --source='.' manage.py test
	@$(DOCKER_COMPOSE) run --rm web coverage report
	@echo "$(GREEN)✅ Testes com coverage concluídos!$(NC)"

# === Limpeza e Reset ===
clean: ## Remove containers, volumes e imagens não utilizados
	@echo "$(YELLOW)🧹 Limpando containers e volumes...$(NC)"
	@docker system prune -f
	@docker volume prune -f
	@echo "$(GREEN)✅ Limpeza concluída!$(NC)"

reset: ## Reset completo (CUIDADO: remove todos os dados)
	@echo "$(RED)⚠️  ATENÇÃO: Isso removerá todos os dados!$(NC)"
	@read -p "Tem certeza? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@echo "$(YELLOW)🔄 Resetando ambiente...$(NC)"
	@$(DOCKER_COMPOSE) down -v
	@$(DOCKER_COMPOSE) build --no-cache
	@$(DOCKER_COMPOSE) up -d db
	@sleep 10
	@$(DOCKER_COMPOSE) run --rm web python manage.py migrate
	@$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)✅ Ambiente resetado!$(NC)"

# === Desenvolvimento Local (sem Docker) ===
runserver: ## Executa servidor Django localmente
	@echo "$(GREEN)🌐 Iniciando servidor local...$(NC)"
	@cd backend && $(PYTHON) manage.py runserver

migrate-local: ## Executa migrações localmente
	@echo "$(GREEN)🔄 Executando migrações localmente...$(NC)"
	@cd backend && $(PYTHON) manage.py migrate

shell-local: ## Acessa shell Django localmente
	@echo "$(GREEN)🐚 Abrindo shell Django local...$(NC)"
	@cd backend && $(PYTHON) manage.py shell

# === Utilitários ===
requirements: ## Atualiza requirements.txt
	@echo "$(GREEN)📦 Atualizando requirements.txt...$(NC)"
	@$(DOCKER_COMPOSE) run --rm web pip freeze > backend/requirements.txt
	@echo "$(GREEN)✅ Requirements atualizados!$(NC)"

backup-db: ## Faz backup do banco de dados
	@echo "$(GREEN)💾 Fazendo backup do banco...$(NC)"
	@mkdir -p backups
	@$(DOCKER_COMPOSE) exec db pg_dump -U neocargo_user neocargo > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✅ Backup criado em backups/$(NC)"

# Target padrão
.DEFAULT_GOAL := help
