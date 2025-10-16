# Credenciais de Teste - NeoCargo

Este documento contém as credenciais de teste para acessar diferentes perfis no sistema NeoCargo.

## 🔐 Usuário Dono (Administrador)

**Acesso completo ao sistema, incluindo:**
- Dashboard do Dono
- Gestão de Usuários
- Aprovação de Solicitações de Mudança de Perfil
- Todas as funcionalidades de cliente

### Credenciais:
- **Username:** `dono`
- **Email:** `dono@neocargo.com`
- **Senha:** `dono123`

### Como criar um novo usuário dono:
```bash
docker-compose -f infra/docker-compose.yml -p neocargo run --rm web python manage.py criar_dono
```

Com parâmetros personalizados:
```bash
docker-compose -f infra/docker-compose.yml -p neocargo run --rm web python manage.py criar_dono --username=novo_dono --email=novo@email.com --password=senha123
```

### Como atualizar um usuário existente para dono:
```bash
docker-compose -f infra/docker-compose.yml -p neocargo run --rm web python manage.py atualizar_dono <username>
```

Exemplo:
```bash
docker-compose -f infra/docker-compose.yml -p neocargo run --rm web python manage.py atualizar_dono dono
```

---

## 👤 Usuário Cliente (Padrão)

Qualquer novo usuário criado via cadastro normal será automaticamente um **Cliente**.

**Funcionalidades:**
- Criar pedidos de transporte
- Ver histórico de pedidos
- Gerar cotações
- Solicitar mudança de perfil (para Motorista)

### Como criar:
1. Acesse: http://localhost:8000/contas/signup/
2. Preencha o formulário de cadastro
3. O perfil de Cliente será criado automaticamente

---

## 🚚 Usuário Motorista

Para se tornar motorista, um cliente deve:
1. Fazer login como cliente
2. Acessar: **Menu Usuário → Solicitar Mudança de Perfil**
3. Preencher o formulário com:
   - Dados pessoais (telefone, CPF, endereço, data de nascimento)
   - Dados do veículo (tipo, modelo, placa, ano, cor)
4. Aguardar aprovação do Dono

**Funcionalidades (após aprovação):**
- Todas as funcionalidades de cliente
- Gerenciar veículos
- Aceitar entregas (em desenvolvimento)

---

## 📊 Tipos de Veículos Disponíveis

### 1. Carreta
- **Combustível:** Diesel
- **Rendimento:** 8 Km/L
- **Carga máxima:** 30 toneladas (30.000 Kg)
- **Velocidade média:** 60 Km/h
- **Redução de rendimento:** 0.0002 Km/L por Kg

### 2. Van
- **Combustível:** Diesel
- **Rendimento:** 10 Km/L
- **Carga máxima:** 3,5 toneladas (3.500 Kg)
- **Velocidade média:** 80 Km/h
- **Redução de rendimento:** 0.001 Km/L por Kg

### 3. Carro
- **Combustível:** Gasolina ou Álcool
- **Rendimento:** 14 Km/L (gasolina) / 12 Km/L (álcool)
- **Carga máxima:** 360 Kg
- **Velocidade média:** 100 Km/h
- **Redução de rendimento:** 0.025 Km/L (gasolina) / 0.0231 Km/L (álcool) por Kg

### 4. Moto
- **Combustível:** Gasolina ou Álcool
- **Rendimento:** 50 Km/L (gasolina) / 43 Km/L (álcool)
- **Carga máxima:** 50 Kg
- **Velocidade média:** 110 Km/h
- **Redução de rendimento:** 0.3 Km/L (gasolina) / 0.4 Km/L (álcool) por Kg

---

## 🔄 Fluxo de Mudança de Perfil

### Para Cliente → Motorista:
1. Cliente faz login
2. Acessa **Menu → Solicitar Mudança de Perfil**
3. Preenche formulário completo (dados pessoais + veículo)
4. Envia solicitação
5. Dono recebe notificação
6. Dono acessa **Dashboard do Dono → Solicitações**
7. Dono aprova ou rejeita
8. Se aprovado: perfil é atualizado automaticamente e veículo é cadastrado

### Observações:
- Não é possível solicitar mudança para **Dono** (apenas via admin)
- Apenas uma solicitação pendente por vez
- Dados do veículo são obrigatórios para motoristas

---

## 🛠️ Comandos Úteis

### Criar usuário dono:
```bash
docker-compose -f infra/docker-compose.yml -p neocargo run --rm web python manage.py criar_dono
```

### Popular especificações de veículos:
```bash
docker-compose -f infra/docker-compose.yml -p neocargo run --rm web python manage.py setup_veiculos
```

### Acessar admin Django:
- URL: http://localhost:8000/admin/
- Use as credenciais do usuário dono ou crie um superuser:
```bash
make superuser
```

---

## 📱 URLs Importantes

- **Home:** http://localhost:8000/
- **Login:** http://localhost:8000/contas/login/
- **Cadastro:** http://localhost:8000/contas/signup/
- **Dashboard Cliente:** http://localhost:8000/dashboard/cliente/
- **Dashboard Dono:** http://localhost:8000/gestao/dashboard/
- **Criar Pedido:** http://localhost:8000/pedidos/criar/
- **Meus Pedidos:** http://localhost:8000/pedidos/
- **Solicitar Mudança:** http://localhost:8000/gestao/solicitar-mudanca/
- **Admin Django:** http://localhost:8000/admin/

---

## ⚠️ Importante

- **Não use estas credenciais em produção!**
- As credenciais de teste devem ser alteradas em ambiente de produção
- O primeiro usuário criado no sistema automaticamente vira Dono
- Todos os demais usuários começam como Cliente

---

## 🔒 Segurança

Em produção:
1. Altere todas as senhas padrão
2. Use senhas fortes e únicas
3. Configure variáveis de ambiente para credenciais sensíveis
4. Ative autenticação de dois fatores (quando disponível)
5. Monitore logs de acesso

---

**Última atualização:** 09/10/2025
