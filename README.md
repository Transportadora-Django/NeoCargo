# NeoCargo

**Projeto de disciplina Técnicas de Programação para Plataformas Emergentes**

## Descrição

NeoCargo é um sistema de gerenciamento de transportadora desenvolvido como projeto da disciplina TPPE. O sistema visa fornecer uma solução completa para o controle de operações de transporte, incluindo gestão de cargas, veículos, motoristas e rotas.

## Estrutura do Projeto

```
NeoCargo/
├── backend/          # Aplicação Django
│   ├── .env.example  # Exemplo de variáveis de ambiente
│   └── ...
├── ui/              # Interface do usuário (Frontend)
├── infra/           # Configurações Docker
│   ├── docker-compose.yml
│   ├── Dockerfile
│   └── scripts...
├── Makefile         # Comandos automatizados
├── .gitignore       # Regras de exclusão do Git
├── README.md        # Documentação do projeto
└── LICENSE          # Licença do projeto
```

## Como executar

### Usando Docker (Recomendado)

1. **Pré-requisitos**:
   - Docker
   - Docker Compose
   - Make (opcional, mas recomendado)

2. **Configuração inicial**:
   ```bash
   make setup
   ```

3. **Inicialização**:
   ```bash
   make start
   ```

4. **Acessar aplicação**:
   - 🌐 **Web**: http://localhost:8000
   - 📧 **MailHog**: http://localhost:8025
   - 🗄️ **PostgreSQL**: localhost:5432

### Comandos úteis

**Com Makefile (recomendado):**
```bash
# Configuração inicial
make setup

# Gerenciar serviços
make start             # Iniciar
make stop              # Parar
make restart           # Reiniciar
make logs              # Ver logs

# Django commands
make migrate           # Executar migrações
make shell             # Shell Django
make createsuperuser   # Criar superusuário

# Ver todos os comandos
make help
```

**Comandos diretos (alternativos):**
```bash
cd infra

# Gerenciar serviços
./manage.sh start          # Iniciar
./manage.sh stop           # Parar
./manage.sh restart        # Reiniciar
./manage.sh logs           # Ver logs

# Django commands
./manage.sh migrate        # Executar migrações
./manage.sh shell          # Shell Django
./manage.sh createsuperuser # Criar superusuário

# Ver todos os comandos
./manage.sh
```

### Desenvolvimento local

Para desenvolvimento sem Docker, consulte a documentação em [`backend/README.md`](backend/README.md).

## Próximos Passos

- [x] Criar projeto Django no diretório `backend/`
- [x] Configurar infraestrutura Docker
- [ ] Implementar modelos de dados
- [ ] Desenvolver APIs
- [ ] Criar interface de usuário

## Tecnologias

- **Backend**: Python, Django
- **Frontend**: Django Templates, HTML5, CSS3, JavaScript
- **Banco de Dados**: PostgreSQL (produção), SQLite (desenvolvimento local)
- **Email**: MailHog (desenvolvimento)
- **Infraestrutura**: Docker, Docker Compose
- **Deploy**: Configurado para ambientes de desenvolvimento e produção

## Licença

Este projeto está sob a licença especificada no arquivo [LICENSE](LICENSE).