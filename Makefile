# Makefile para NeoCargo
# Sistema de gerenciamento de transportadora

.PHONY: help setup start stop restart logs shell bash migrate test lint format fix ci clean

# Configurações
DOCKER_COMPOSE = docker-compose -f infra/docker-compose.yml -p neocargo

# Cores para output
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

help: ## Exibe esta ajuda
	@echo "$(GREEN)NeoCargo - Sistema de Gerenciamento de Transportadora$(NC)"
	@echo ""
	@echo "$(YELLOW)Comandos disponíveis:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Exemplos rápidos:$(NC)"
	@echo "  make setup     # Configuração inicial completa"
	@echo "  make start     # Iniciar aplicação"
	@echo "  make test      # Executar testes"
	@echo "  make lint      # Verificar código"
	@echo "  make fix       # Corrigir problemas automaticamente"
	@echo "  make ci        # Verificação completa do CI"

# === Setup e Build ===
setup: ## Configuração inicial completa
	@echo "$(GREEN)🚀 Configurando NeoCargo...$(NC)"
	@if [ ! -f backend/.env ]; then \
		echo "$(YELLOW)📝 Criando arquivo .env...$(NC)"; \
		cp backend/.env.dev backend/.env; \
	fi
	@echo "$(GREEN)🔨 Construindo containers (com dependências)...$(NC)"
	@$(DOCKER_COMPOSE) build --no-cache
	@echo "$(GREEN)✅ Setup concluído! Use 'make start' para iniciar.$(NC)"

build: ## Reconstrói containers
	@echo "$(GREEN)🔨 Reconstruindo containers...$(NC)"
	@$(DOCKER_COMPOSE) build --no-cache
	@echo "$(GREEN)✅ Build concluído!$(NC)"

# === Gerenciamento ===
start: ## Inicia todos os serviços
	@echo "$(GREEN)🚀 Iniciando NeoCargo...$(NC)"
	@$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)✅ Serviços iniciados!$(NC)"
	@echo "$(YELLOW)📍 Acesse: http://localhost:8000$(NC)"

stop: ## Para todos os serviços
	@echo "$(YELLOW)🛑 Parando serviços...$(NC)"
	@$(DOCKER_COMPOSE) down
	@echo "$(GREEN)✅ Serviços parados!$(NC)"

restart: ## Reinicia todos os serviços
	@$(DOCKER_COMPOSE) restart
	@echo "$(GREEN)✅ Serviços reiniciados!$(NC)"

logs: ## Exibe logs em tempo real
	@$(DOCKER_COMPOSE) logs -f

shell: ## Acessa shell Django
	@$(DOCKER_COMPOSE) exec web python manage.py shell

bash: ## Acessa bash do container
	@$(DOCKER_COMPOSE) exec web bash

# === Django ===
migrate: ## Executa migrações
	@echo "$(GREEN)🔄 Executando migrações...$(NC)"
	@$(DOCKER_COMPOSE) run --rm web python manage.py migrate
	@echo "$(GREEN)✅ Migrações concluídas!$(NC)"

makemigrations: ## Cria novas migrações
	@$(DOCKER_COMPOSE) run --rm web python manage.py makemigrations

superuser: ## Cria superusuário
	@$(DOCKER_COMPOSE) run --rm web python manage.py createsuperuser

# === Testes ===
test: ## Executa todos os testes
	@echo "$(GREEN)🧪 Executando testes...$(NC)"
	@$(DOCKER_COMPOSE) run --rm web pytest --cov=. --cov-report=xml --cov-report=term-missing
	@echo "$(GREEN)✅ Testes concluídos!$(NC)"

test-cov: ## Testes com coverage
	@echo "$(GREEN)🧪 Testes com coverage...$(NC)"
	@$(DOCKER_COMPOSE) run --rm web pytest --cov=. --cov-report=term-missing
	@echo "$(GREEN)✅ Coverage concluído!$(NC)"

# === Linting e Formatação ===
lint: ## Verifica qualidade do código
	@echo "$(GREEN)🔍 Verificando código...$(NC)"
	@echo "$(YELLOW)Backend (Ruff)...$(NC)"
	@$(DOCKER_COMPOSE) run --rm web ruff check .
	@$(DOCKER_COMPOSE) run --rm web ruff format --check .
	@echo "$(YELLOW)Frontend (ESLint/Prettier/Stylelint/HTMLHint)...$(NC)"
	@if [ -f "ui/package.json" ]; then \
		$(DOCKER_COMPOSE) run --rm web sh -c "cd /app/ui && npm run lint && npm run lint:css && npm run lint:html && npm run format:check"; \
	else \
		echo "$(YELLOW)Frontend não configurado$(NC)"; \
	fi
	@echo "$(GREEN)✅ Verificação concluída!$(NC)"

format: ## Formata todo o código
	@echo "$(GREEN)✨ Formatando código...$(NC)"
	@$(DOCKER_COMPOSE) run --rm web ruff format .
	@if [ -f "ui/package.json" ]; then \
		$(DOCKER_COMPOSE) run --rm web sh -c "cd /app/ui && npm run format"; \
	fi
	@echo "$(GREEN)✅ Formatação concluída!$(NC)"

fix: ## Corrige problemas automaticamente
	@echo "$(GREEN)✨ Corrigindo problemas...$(NC)"
	@$(DOCKER_COMPOSE) run --rm web ruff check --fix .
	@$(DOCKER_COMPOSE) run --rm web ruff format .
	@if [ -f "ui/package.json" ]; then \
		$(DOCKER_COMPOSE) run --rm web sh -c "cd /app/ui && npm run lint:fix && npm run lint:css:fix && npm run format"; \
	fi
	@echo "$(GREEN)✅ Correções aplicadas!$(NC)"

# === CI/CD ===
ci: ## Executa todas as verificações do CI (idêntico ao GitHub Actions)
	@echo "$(GREEN)🚀 Executando CI completo (sequencial)...$(NC)"
	@echo "$(YELLOW)1. Docker Build Test...$(NC)"
	@$(DOCKER_COMPOSE) build --no-cache
	@$(DOCKER_COMPOSE) run --rm web python --version
	@echo "$(YELLOW)2. Backend & Frontend Linting...$(NC)"
	@$(MAKE) lint
	@echo "$(YELLOW)3. Backend Tests...$(NC)"
	@$(MAKE) test
	@echo "$(GREEN)✅ CI passou em todas as verificações!$(NC)"

security: ## Verificações de segurança
	@echo "$(GREEN)🔒 Verificações de segurança...$(NC)"
	@$(DOCKER_COMPOSE) run --rm web safety check -r requirements.txt
	@$(DOCKER_COMPOSE) run --rm web bandit -r . -x tests/
	@echo "$(GREEN)✅ Segurança verificada!$(NC)"

# === Utilitários ===
clean: ## Limpa containers e volumes
	@echo "$(YELLOW)🧹 Limpando sistema...$(NC)"
	@$(DOCKER_COMPOSE) down -v
	@docker system prune -f
	@echo "$(GREEN)✅ Limpeza concluída!$(NC)"

reset: ## Reset completo (CUIDADO!)
	@echo "$(RED)⚠️  ATENÇÃO: Remove todos os dados!$(NC)"
	@read -p "Confirma? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@$(MAKE) clean
	@$(MAKE) setup
	@$(MAKE) migrate
	@echo "$(GREEN)✅ Reset completo!$(NC)"

status: ## Status dos containers
	@$(DOCKER_COMPOSE) ps

# Target padrão
.DEFAULT_GOAL := help