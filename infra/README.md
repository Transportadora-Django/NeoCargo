# Infraestrutura NeoCargo

Este diretório contém toda a configuração Docker para o projeto NeoCargo.

## Estrutura

```
infra/
├── docker-compose.yml    # Configuração dos serviços
├── Dockerfile           # Imagem da aplicação Django
├── start.sh            # Script de inicialização
├── .env.example        # Exemplo de variáveis de ambiente
└── README.md           # Este arquivo
```

## Serviços

### 🌐 Web (Django)
- **Porta**: 8000
- **Descrição**: Aplicação Django principal
- **URL**: http://localhost:8000

### 🗄️ Database (PostgreSQL)
- **Porta**: 5432
- **Banco**: neocargo
- **Usuário**: neocargo_user
- **Senha**: neocargo_password

### 📧 MailHog
- **Porta SMTP**: 1025
- **Porta Web UI**: 8025
- **Descrição**: Servidor de email para desenvolvimento
- **URL**: http://localhost:8025

## Como usar

### Inicialização rápida

```bash
# Executar o script de inicialização
./start.sh
```

### Comandos manuais

```bash
# Construir os containers
docker-compose build

# Iniciar todos os serviços
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar todos os serviços
docker-compose down

# Executar migrações
docker-compose run --rm web python manage.py migrate

# Criar superusuário
docker-compose run --rm web python manage.py createsuperuser

# Acessar shell Django
docker-compose exec web python manage.py shell

# Acessar shell do container
docker-compose exec web bash
```

### Configuração de ambiente

1. Copie o arquivo de exemplo:
   ```bash
   cp .env.example .env
   ```

2. Edite o arquivo `.env` com suas configurações

## Desenvolvimento

### Volumes

Os diretórios `backend/` e `ui/` são montados como volumes, permitindo desenvolvimento em tempo real sem necessidade de rebuild.

### Hot Reload

O Django está configurado para detectar mudanças automaticamente durante o desenvolvimento.

### Banco de Dados

Os dados do PostgreSQL são persistidos no volume `postgres_data`.

## Troubleshooting

### Container não inicia
```bash
# Verificar logs
docker-compose logs <nome_do_serviço>

# Reconstruir imagem
docker-compose build --no-cache <nome_do_serviço>
```

### Problemas de permissão
```bash
# Garantir que o script seja executável
chmod +x start.sh
```

### Reset completo
```bash
# Parar e remover tudo
docker-compose down -v

# Remover imagens (opcional)
docker-compose down --rmi all
```
