# Configuração do Mailgun - NeoCargo

Este guia explica como configurar o Mailgun para envio de emails no NeoCargo.

## 1. Configuração no Mailgun

### 1.1. Obter Credenciais SMTP

1. Acesse [Mailgun](https://www.mailgun.com/) e faça login
2. Vá para **Sending** → **Domains**
3. Selecione seu domínio (ou use o domínio sandbox para testes)
4. Clique em **SMTP** ou **Domain Settings**
5. Anote as seguintes informações:
   - **SMTP Hostname:** `smtp.mailgun.org`
   - **Port:** `587` (TLS) ou `465` (SSL)
   - **Username:** `postmaster@seu-dominio.mailgun.org`
   - **Password:** Sua senha SMTP (clique em "Reset Password" se necessário)

### 1.2. Domínio Sandbox vs Domínio Próprio

**Domínio Sandbox (para testes):**
- Formato: `sandboxXXXXXXXX.mailgun.org`
- Limitação: Só envia emails para endereços autorizados
- Ideal para: Desenvolvimento e testes

**Domínio Próprio (para produção):**
- Formato: `mg.seu-dominio.com` ou `seu-dominio.com`
- Requer: Configuração de DNS (SPF, DKIM, MX)
- Ideal para: Produção

### 1.3. Autorizar Destinatários (Sandbox)

Se estiver usando domínio sandbox:

1. Vá para **Sending** → **Domains** → Seu domínio sandbox
2. Clique em **Authorized Recipients**
3. Adicione os emails que poderão receber mensagens
4. Confirme o email de verificação enviado para cada destinatário

## 2. Configuração no Render

### 2.1. Variáveis de Ambiente

No painel do Render, adicione as seguintes variáveis de ambiente:

```bash
# Configuração SMTP do Mailgun
EMAIL_HOST=smtp.mailgun.org
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=postmaster@seu-dominio.mailgun.org
EMAIL_HOST_PASSWORD=sua-senha-smtp-do-mailgun

# Email de envio padrão
DEFAULT_FROM_EMAIL=NeoCargo <noreply@seu-dominio.mailgun.org>
SERVER_EMAIL=NeoCargo <noreply@seu-dominio.mailgun.org>
```

### 2.2. Exemplo com Domínio Sandbox

```bash
EMAIL_HOST=smtp.mailgun.org
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=postmaster@sandbox1234567890abcdef.mailgun.org
EMAIL_HOST_PASSWORD=abc123def456ghi789
DEFAULT_FROM_EMAIL=NeoCargo <noreply@sandbox1234567890abcdef.mailgun.org>
```

## 3. Configuração de DNS (Domínio Próprio)

Se você estiver usando um domínio próprio, configure os seguintes registros DNS:

### 3.1. Registros Necessários

O Mailgun fornecerá os valores exatos. Exemplo:

**TXT (SPF):**
```
Hostname: seu-dominio.com
Value: v=spf1 include:mailgun.org ~all
```

**TXT (DKIM):**
```
Hostname: k1._domainkey.seu-dominio.com
Value: k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC...
```

**CNAME (Tracking):**
```
Hostname: email.seu-dominio.com
Value: mailgun.org
```

**MX (Recebimento - Opcional):**
```
Priority: 10
Hostname: seu-dominio.com
Value: mxa.mailgun.org

Priority: 10
Hostname: seu-dominio.com
Value: mxb.mailgun.org
```

### 3.2. Verificação

1. Após configurar os registros DNS, aguarde a propagação (pode levar até 48h)
2. No painel do Mailgun, clique em **Verify DNS Settings**
3. Aguarde até que todos os registros estejam verificados (✓)

## 4. Testar Envio de Email

### 4.1. Via Django Shell

```bash
# Acessar o shell do Django
python manage.py shell

# Testar envio de email
from django.core.mail import send_mail

send_mail(
    'Teste NeoCargo',
    'Este é um email de teste do NeoCargo.',
    'noreply@seu-dominio.mailgun.org',
    ['seu-email@example.com'],
    fail_silently=False,
)
```

### 4.2. Via Comando de Gerenciamento

```bash
# Usar o comando de teste de email existente
python manage.py test_email seu-email@example.com
```

### 4.3. Via Interface do Sistema

1. Faça login no NeoCargo
2. Vá para **Perfil** → **Alterar Email**
3. Solicite alteração de email
4. Verifique se o email de confirmação foi recebido

## 5. Monitoramento

### 5.1. Logs do Mailgun

1. Acesse **Sending** → **Logs**
2. Visualize todos os emails enviados, entregues, bounces, etc.
3. Filtre por data, destinatário, status, etc.

### 5.2. Estatísticas

1. Acesse **Analytics** → **Overview**
2. Visualize métricas de:
   - Emails enviados
   - Taxa de entrega
   - Bounces e reclamações
   - Cliques e aberturas (se tracking habilitado)

## 6. Limites e Quotas

### 6.1. Plano Free (Sandbox)

- **Limite:** 5.000 emails/mês (primeiros 3 meses)
- **Após 3 meses:** 100 emails/dia
- **Destinatários:** Apenas emails autorizados

### 6.2. Plano Pago

- **Foundation:** A partir de $35/mês
- **Limite:** 50.000 emails/mês
- **Destinatários:** Ilimitados
- **Domínio próprio:** Sim

## 7. Troubleshooting

### 7.1. Email não está sendo enviado

**Verificar:**
1. Credenciais SMTP estão corretas?
2. Variáveis de ambiente estão configuradas no Render?
3. Destinatário está autorizado (se usando sandbox)?
4. Verificar logs do Mailgun

**Comando de debug:**
```bash
python manage.py debug_email seu-email@example.com
```

### 7.2. Email vai para spam

**Soluções:**
1. Configure SPF, DKIM e DMARC corretamente
2. Use domínio próprio verificado
3. Evite palavras spam no assunto/corpo
4. Mantenha boa reputação de envio

### 7.3. Erro de autenticação

**Verificar:**
1. Username está no formato: `postmaster@seu-dominio.mailgun.org`
2. Senha SMTP está correta (não é a senha da conta Mailgun)
3. Porta e TLS estão configurados corretamente

## 8. Boas Práticas

1. **Use domínio próprio** para produção
2. **Configure DNS corretamente** (SPF, DKIM, DMARC)
3. **Monitore bounces** e remova emails inválidos
4. **Implemente unsubscribe** para emails marketing
5. **Teste antes de produção** usando domínio sandbox
6. **Mantenha templates** profissionais e responsivos
7. **Respeite limites** de envio para evitar bloqueios

## 9. Segurança

1. **Nunca commite** credenciais no código
2. **Use variáveis de ambiente** para todas as configurações sensíveis
3. **Rotacione senhas** periodicamente
4. **Monitore logs** para detectar uso indevido
5. **Configure webhooks** para receber notificações de bounces/spam

## 10. Recursos Adicionais

- [Documentação Oficial Mailgun](https://documentation.mailgun.com/)
- [Guia de SMTP](https://documentation.mailgun.com/en/latest/user_manual.html#sending-via-smtp)
- [Configuração DNS](https://documentation.mailgun.com/en/latest/user_manual.html#verifying-your-domain)
- [API Reference](https://documentation.mailgun.com/en/latest/api_reference.html)
