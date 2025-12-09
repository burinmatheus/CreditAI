# CreditAI - Arquitetura Hexagonal

Este projeto utiliza **Arquitetura Hexagonal (Ports and Adapters)** para garantir separação de responsabilidades e facilitar testes e manutenção.

## 📁 Estrutura do Projeto

```
src/
├── domain/                  # Camada de Domínio (núcleo da aplicação)
│   ├── entities/           # Entidades de domínio (User, Health, etc)
│   └── ports/              # Interfaces (contratos) para adapters
│
├── application/            # Camada de Aplicação (casos de uso)
│   ├── services/          # Serviços de aplicação
│   └── use_cases/         # Casos de uso específicos
│
├── infrastructure/         # Camada de Infraestrutura (detalhes técnicos)
│   └── adapters/
│       ├── database/      # Adaptadores de banco de dados
│       └── cache/         # Adaptadores de cache
│
├── interfaces/            # Camada de Interface (entrada/saída)
│   └── http/             # Adaptadores HTTP (REST API)
│
├── config.py             # Configurações da aplicação
└── main.py              # Ponto de entrada com DI
```

## 🏗️ Princípios da Arquitetura

### 1. **Domain (Núcleo)**
- Contém a lógica de negócio pura
- Não depende de nenhuma camada externa
- Define **Ports** (interfaces) que outras camadas implementam

### 2. **Application**
- Orquestra casos de uso
- Usa as **Ports** definidas no domínio
- Não conhece detalhes de implementação

### 3. **Infrastructure**
- Implementa os **Adapters** para as **Ports**
- Contém detalhes técnicos (PostgreSQL, Redis, etc)
- Pode ser substituída sem afetar o domínio

### 4. **Interfaces**
- Adaptadores de entrada (HTTP, CLI, etc)
- Converte requisições externas em chamadas de aplicação

## 🔌 Fluxo de Dependências

```
Interfaces → Application → Domain ← Infrastructure
```

**Regra de Ouro:** Dependências apontam sempre para dentro (para o Domain)

## 📚 Exemplo de Uso

### Adicionar novo repositório

1. Criar porta no domínio:
```python
# src/domain/ports/my_repository.py
class MyRepositoryPort(ABC):
    @abstractmethod
    def save(self, entity): pass
```

2. Implementar adapter na infraestrutura:
```python
# src/infrastructure/adapters/database/my_repository.py
class PostgresMyRepository(MyRepositoryPort):
    def save(self, entity):
        # implementação específica do PostgreSQL
```

3. Injetar no main.py:
```python
my_repo = PostgresMyRepository(postgres_conn)
my_service = MyService(my_repo)
```

## 🎯 Benefícios

- ✅ **Testabilidade**: Fácil criar mocks das portas
- ✅ **Manutenibilidade**: Mudanças isoladas por camada
- ✅ **Flexibilidade**: Troca de tecnologias sem afetar o domínio
- ✅ **Clareza**: Separação clara de responsabilidades

## 🚀 Rodando a Aplicação

```bash
python src/main.py
```

## 📡 Endpoints Disponíveis

- `GET /` - Informações da API
- `GET /health` - Status dos serviços
- `GET /users` - Lista de usuários
