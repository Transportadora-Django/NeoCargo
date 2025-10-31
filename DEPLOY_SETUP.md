# Setup de Deploy - NeoCargo

Este documento descreve como configurar o deploy inicial do NeoCargo no Render ou outro serviço de hospedagem.

## Variáveis de Ambiente Necessárias

### Configuração do Superuser Inicial

O sistema cria automaticamente um superuser/owner no primeiro deploy. Configure as seguintes variáveis de ambiente:

```bash
DJANGO_SUPERUSER_USERNAME=admin          # Username do superuser (padrão: admin)
DJANGO_SUPERUSER_EMAIL=admin@neocargo.com  # Email do superuser
DJANGO_SUPERUSER_PASSWORD=SuaSenhaSegura123!  # OBRIGATÓRIO: Senha do superuser
```

**⚠️ IMPORTANTE:** A variável `DJANGO_SUPERUSER_PASSWORD` é **obrigatória**. Sem ela, o superuser não será criado.

### Configuração de Email (Mailgun)

```bash
# SMTP Mailgun
EMAIL_HOST=smtp.mailgun.org
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=postmaster@seu-dominio.mailgun.org
EMAIL_HOST_PASSWORD=sua-senha-smtp-do-mailgun

# Email de envio padrão
DEFAULT_FROM_EMAIL=NeoCargo <noreply@seu-dominio.mailgun.org>
SERVER_EMAIL=NeoCargo <noreply@seu-dominio.mailgun.org>
```

**📧 Veja [MAILGUN_SETUP.md](MAILGUN_SETUP.md) para instruções detalhadas de configuração do Mailgun.**

### Outras Variáveis de Ambiente

```bash
# Django
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=False
DJANGO_SETTINGS_MODULE=frete_proj.settings.prod
ALLOWED_HOSTS=seu-dominio.onrender.com

# Database
DATABASE_URL=postgresql://user:password@host:port/database
```

## Processo de Deploy Automático

Quando você faz o deploy no Render, o sistema executa automaticamente:

1. **Migrações do banco de dados** - Cria todas as tabelas necessárias
2. **Criação do superuser** - Cria o primeiro usuário admin/owner
3. **População de rotas e cidades** - Adiciona cidades e rotas principais do Brasil
4. **População de veículos** - Adiciona especificações e veículos de exemplo
5. **Coleta de arquivos estáticos** - Prepara CSS, JS e imagens

## Dados Populados Automaticamente

### Cidades (28 cidades principais)
- São Paulo, Campinas, Santos, Ribeirão Preto
- Rio de Janeiro, Niterói
- Belo Horizonte, Uberlândia, Juiz de Fora
- Curitiba, Londrina, Maringá
- Porto Alegre, Caxias do Sul
- Florianópolis, Joinville, Blumenau
- Salvador, Recife, Fortaleza, Brasília, Goiânia
- E outras...

### Rotas (14 rotas principais)
- São Paulo ↔ Rio de Janeiro, Belo Horizonte, Curitiba, Brasília
- Rio de Janeiro ↔ Belo Horizonte, Vitória, Salvador
- Curitiba ↔ Florianópolis, Porto Alegre
- E outras rotas importantes

### Especificações de Veículos
- Van (1.500kg)
- Caminhão 3/4 (3.500kg)
- Caminhão Toco (6.000kg)
- Caminhão Truck (14.000kg)
- Carreta (30.000kg)
- Bitrem (45.000kg)

### Veículos de Exemplo (5 veículos)
- Mercedes-Benz Sprinter (Van)
- Ford Cargo 816 (Caminhão 3/4)
- Volkswagen Delivery 11.180 (Caminhão Toco)
- Scania P 320 (Caminhão Truck)
- Volvo FH 540 (Carreta)

## Primeiro Acesso

Após o deploy, você pode fazer login com:

- **Username:** O valor de `DJANGO_SUPERUSER_USERNAME` (padrão: admin)
- **Senha:** O valor de `DJANGO_SUPERUSER_PASSWORD`
- **Role:** Owner (acesso total ao sistema)

## Comandos de Gerenciamento

Caso precise executar os comandos manualmente:

```bash
# Criar superuser
python manage.py setup_initial_superuser

# Popular rotas e cidades
python manage.py populate_rotas

# Popular especificações e veículos
python manage.py populate_veiculos

# Testar envio de email
python manage.py test_email seu-email@example.com
```

## Troubleshooting

### Superuser não foi criado

Verifique se a variável `DJANGO_SUPERUSER_PASSWORD` está definida nas variáveis de ambiente do Render.

### Dados não foram populados

Os comandos verificam se já existem dados antes de popular. Se você quiser repopular, delete os dados existentes primeiro.

### Erro ao fazer login

Certifique-se de usar o username e senha corretos definidos nas variáveis de ambiente.

### Emails não estão sendo enviados

1. Verifique se as variáveis de email estão configuradas corretamente
2. Confirme que o domínio Mailgun está verificado
3. Se usar sandbox, verifique se o destinatário está autorizado
4. Veja [MAILGUN_SETUP.md](MAILGUN_SETUP.md) para mais detalhes

## Segurança

- **Nunca** commite senhas ou credenciais no código
- Use senhas fortes com letras, números e caracteres especiais
- Altere a senha do superuser após o primeiro acesso
- Configure as variáveis de ambiente diretamente no painel do Render
- Rotacione as credenciais SMTP periodicamente
