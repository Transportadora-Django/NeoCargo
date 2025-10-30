# App Motoristas

Aplicação responsável pelo gerenciamento de motoristas e atribuição automática de pedidos.

## Funcionalidades

### 1. Modelos

- **Motorista**: Cadastro de motoristas com informações de CNH, sede atual e histórico de entregas
- **AtribuicaoPedido**: Relaciona pedidos com motoristas e veículos, controlando o status da entrega
- **CategoriaCNH**: Enum com categorias B, C, D e E
- **StatusAtribuicao**: Enum com status PENDENTE, EM_ANDAMENTO, CONCLUIDO e CANCELADO

### 2. Serviço de Atribuição Automática

O `AtribuicaoService` implementa a lógica de designação automática de motoristas e veículos para pedidos:

#### Hierarquia de CNH
- CNH B: Pode dirigir apenas veículos categoria B
- CNH C: Pode dirigir veículos categoria B e C
- CNH D: Pode dirigir veículos categoria B, C e D
- CNH E: Pode dirigir veículos categoria B, C, D e E

#### Algoritmo de Atribuição
1. Busca veículo disponível na cidade de origem do pedido
2. Busca motorista disponível na cidade com CNH compatível
3. Prioriza motoristas com menos entregas concluídas
4. Cria atribuição com status PENDENTE

#### Métodos Principais
- `atribuir_pedido(pedido)`: Atribui motorista e veículo automaticamente
- `buscar_motorista_disponivel(cidade, cnh_minima)`: Busca motorista compatível
- `buscar_veiculo_disponivel(cidade, motorista)`: Busca veículo disponível
- `concluir_entrega(atribuicao)`: Finaliza entrega e atualiza estatísticas
- `cancelar_atribuicao(atribuicao)`: Cancela atribuição e libera recursos

## Comandos de Gerenciamento

### seed_motoristas

Popula o banco de dados com motoristas e veículos de teste.

**Uso:**
```bash
# Criar dados de seed
python manage.py seed_motoristas

# Remover e recriar dados de seed
python manage.py seed_motoristas --clear
```

**Dados Criados:**

**8 Motoristas:**
- João Silva (CNH D) - São Paulo/SP - 45 entregas
- Maria Santos (CNH E) - Rio de Janeiro/RJ - 78 entregas
- Pedro Costa (CNH C) - Belo Horizonte/MG - 32 entregas
- Ana Oliveira (CNH D) - Curitiba/PR - 56 entregas
- Carlos Ferreira (CNH E) - Porto Alegre/RS - 91 entregas
- Lúcia Almeida (CNH B) - Salvador/BA - 12 entregas
- Roberto Mendes (CNH C) - São Paulo/SP - 67 entregas
- Fernanda Lima (CNH D) - Rio de Janeiro/RJ - 43 entregas

**10 Veículos:**
- SEED-001: Mercedes-Benz Actros 2651 (Carreta, CNH E) - São Paulo
- SEED-002: Volvo FH 540 (Carreta, CNH E) - Rio de Janeiro
- SEED-003: Iveco Daily 70C16 (Van, CNH D) - Belo Horizonte
- SEED-004: Volkswagen Constellation 24.280 (Carreta, CNH D) - Curitiba
- SEED-005: Renault Master (Van, CNH C) - Porto Alegre
- SEED-006: Fiat Ducato (Van, CNH C) - Salvador
- SEED-007: Toyota Hilux (Carro, CNH B) - São Paulo
- SEED-008: Ford Cargo 1719 (Carreta, CNH D) - Rio de Janeiro
- SEED-009: Chevrolet S10 (Carro, CNH B) - Belo Horizonte
- SEED-010: Honda CG 160 (Moto, CNH B) - Curitiba

**Credenciais:**
- Usuários: `motorista_joao`, `motorista_maria`, etc.
- Senha padrão: `senha123`

**Dependências:**
O comando requer que as seguintes tabelas estejam populadas:
- Cidades: `python manage.py popular_cidades`
- Especificações de veículos: `python manage.py popular_especificacoes`

## Testes

A aplicação possui cobertura de testes de 89%:

### test_models.py
- Criação de motoristas e atribuições
- Validações de campos únicos
- Métodos `__str__`
- Valores padrão

### test_services.py
- Hierarquia de CNH (8 testes)
- Busca de motoristas disponíveis (4 testes)
- Busca de veículos disponíveis (3 testes)
- Atribuição de pedidos (3 testes)
- Conclusão de entregas (1 teste)
- Cancelamento de atribuições (1 teste)

**Executar testes:**
```bash
make test
```

## Integração com Outros Apps

- **contas**: Profile de motorista com Role.MOTORISTA
- **veiculos**: Veículo com especificação e categoria mínima de CNH
- **pedidos**: Pedido com status e cidade de origem/destino
- **rotas**: Cidade para localização de motoristas e veículos

## TODO

- [ ] Interface web para visualização de atribuições
- [ ] Dashboard de motoristas com estatísticas
- [ ] Notificações para motoristas sobre novas atribuições
- [ ] Histórico de entregas por motorista
- [ ] Relatórios de desempenho
