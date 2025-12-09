# CreditAI

CreditAI é um sistema inovador de análise de crédito desenvolvido com **Arquitetura Hexagonal** e **Inteligência Artificial**. O sistema implementa um **pipeline de 4 etapas** utilizando diferentes técnicas de IA para garantir decisões de crédito rápidas, precisas e seguras.

## 🧠 Pipeline de Análise de Crédito com IA

O CreditAI utiliza um pipeline sequencial de 4 etapas, onde cada etapa aplica uma técnica específica de IA:

| Etapa | Técnica de IA | Objetivo | Saída |
|-------|--------------|----------|-------|
| **1. Filtro de Persona** | **DFS (Depth-First Search)** | Validar se o cliente atende critérios básicos através de árvore de decisão | Aprovado/Rejeitado + Motivo |
| **2. Cálculo de Limite** | **BFS (Breadth-First Search)** | Calcular limite de crédito ideal explorando combinações de produtos | Limite, Parcelas, Taxa |
| **3. Avaliação de Risco** | **Lógica Fuzzy** | Avaliar risco de inadimplência com inferência fuzzy | Nível de Risco (Baixo/Médio/Alto) |
| **4. Decisão Final** | **Rede Neural (MLP)** | Decidir aprovação final usando rede neural treinada | Aprovado/Em Análise/Rejeitado |

### 📊 Fluxo do Pipeline

```
Cliente Solicita Crédito
         ↓
┌─────────────────────────┐
│  Etapa 1: DFS           │
│  Filtro de Persona      │ → Valida: Idade (18-75), Score (≥300), 
│  (Árvore de Decisão)    │   Emprego, BACEN, Renda, Dívidas (≤40%)
└─────────────────────────┘
         ↓ [Passa]
┌─────────────────────────┐
│  Etapa 2: BFS           │
│  Cálculo de Limite      │ → Explora produtos: Personal Loan, 
│  (Busca em Largura)     │   Credit Card, Auto Loan, Home Loan
└─────────────────────────┘
         ↓
┌─────────────────────────┐
│  Etapa 3: Fuzzy Logic   │
│  Avaliação de Risco     │ → Fuzzificação + Regras Fuzzy + 
│  (Lógica Fuzzy)         │   Defuzzificação = Risco (Baixo/Médio/Alto)
└─────────────────────────┘
         ↓
┌─────────────────────────┐
│  Etapa 4: RNA           │
│  Decisão Final          │ → Rede Neural (10→8→3) com Softmax
│  (Rede Neural)          │   Aprovado/Em Análise/Rejeitado
└─────────────────────────┘
         ↓
    Resultado Final
```

## 🏗️ Arquitetura Hexagonal

```
┌───────────────────────────────────────────────────────────┐
│                    DOMAIN LAYER (Core)                     │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ Entities: CreditRequest, CustomerProfile,           │  │
│  │           CreditAnalysisResult, RiskAssessment      │  │
│  │                                                       │  │
│  │ Services: PersonaFilterDFS, CreditLimitBFS,         │  │
│  │           RiskFuzzyLogic, ApprovalNeuralNetwork     │  │
│  └─────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────┘
                            ↕
┌───────────────────────────────────────────────────────────┐
│                  APPLICATION LAYER                         │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ CreditAnalysisService (Orchestrator)                │  │
│  │ - Executa pipeline completo de 4 etapas            │  │
│  │ - Coordena serviços de domínio                      │  │
│  │ - Gera resumo de análise                            │  │
│  └─────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────┘
                            ↕
┌───────────────────────────────────────────────────────────┐
│              INFRASTRUCTURE LAYER (Adapters)               │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ PostgreSQL: customer_profiles, credit_requests,     │  │
│  │             credit_analysis_results                 │  │
│  │ Redis: Cache de resultados                          │  │
│  └─────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────┘
                            ↕
┌───────────────────────────────────────────────────────────┐
│               INTERFACES LAYER (HTTP/API)                  │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ FastAPI REST API:                                    │  │
│  │ - POST /api/credit/analyze                          │  │
│  │ - GET  /api/credit/products                         │  │
│  │ - GET  /api/credit/health                           │  │
│  │                                                       │  │
│  │ Swagger UI: http://localhost:8000/docs              │  │
│  └─────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────┘
```

## 🚀 Início Rápido

### Pré-requisitos

- Docker & Docker Compose
- VS Code (recomendado com Dev Containers extension)

### Executando com DevContainer

1. Clone o repositório:
```bash
git clone <repository-url>
cd CreditAI
```

2. Abra no VS Code e use "Reopen in Container"

3. O container será iniciado automaticamente com:
   - PostgreSQL (porta 5432)
   - Redis (porta 16379)
   - Python 3.12
   - Todas as dependências instaladas

4. Acesse a aplicação:
   - API: http://localhost:8000
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## 📡 API Endpoints

### POST /api/credit/analyze
Executa análise completa de crédito em 4 etapas.

**Request Body:**
```json
{
  "customer_profile": {
    "age": 35,
    "gender": "M",
    "marital_status": "married",
    "income": 8500.0,
    "credit_score": 780,
    "employment_status": "employed",
    "time_at_job_months": 48,
    "has_bank_account": true,
    "debt_to_income_ratio": 0.25,
    "num_credit_inquiries": 2,
    "has_bacen_restriction": false,
    "num_existing_loans": 1
  },
  "credit_request": {
    "requested_amount": 25000.0,
    "product_type": "personal_loan",
    "purpose": "home_improvement"
  }
}
```

**Response:**
```json
{
  "stage_1_persona_filter": {
    "passed": true,
    "rejection_reason": null,
    "checked_rules": ["age", "credit_score", "employment", "bacen", "income", "debt_ratio"]
  },
  "stage_2_credit_limit": {
    "approved_limit": 25000.0,
    "max_installments": 48,
    "monthly_installment": 687.5,
    "interest_rate": 0.0299,
    "product_type": "personal_loan"
  },
  "stage_3_risk_assessment": {
    "risk_level": "LOW",
    "risk_score": 0.23,
    "risk_factors": {...}
  },
  "stage_4_approval_decision": {
    "final_status": "APPROVED",
    "confidence": 0.92,
    "reasons": ["Excellent credit profile", "Low risk assessment"]
  },
  "summary": "Credit analysis completed successfully..."
}
```

### GET /api/credit/products
Lista produtos de crédito disponíveis.

**Response:**
```json
{
  "products": [
    {
      "product_type": "personal_loan",
      "max_amount": 100000.0,
      "max_installments": 48,
      "interest_rate": 0.0299,
      "description": "Empréstimo pessoal com taxas competitivas"
    },
    ...
  ]
}
```

### GET /api/credit/health
Health check do serviço de análise de crédito.

## 🧪 Exemplos de Teste

Confira o arquivo `examples/credit_analysis_examples.json` com 8 cenários de teste diferentes:

1. ✅ Cliente Aprovado (Alto Score)
2. ❌ Cliente Rejeitado (Idade < 18)
3. ❌ Cliente Rejeitado (Restrição BACEN)
4. ❌ Cliente Rejeitado (Score Baixo)
5. ✅ Cliente Aprovado (Perfil Médio)
6. ✅ Cartão de Crédito Aprovado
7. ✅ Financiamento Imobiliário Aprovado
8. ❌ Cliente Rejeitado (Endividamento Alto)

### Testando com cURL

```bash
# Análise de crédito
curl -X POST http://localhost:8000/api/credit/analyze \
  -H "Content-Type: application/json" \
  -d @examples/credit_analysis_examples.json

# Listar produtos
curl http://localhost:8000/api/credit/products

# Health check
curl http://localhost:8000/api/credit/health
```

## 🔬 Detalhes das Técnicas de IA

### 1. DFS - Depth-First Search (Filtro de Persona)

Implementa uma **árvore de decisão** percorrida em profundidade:

```python
Raiz
├─ Idade [18-75]?
│  ├─ Sim → Score ≥ 300?
│  │  ├─ Sim → Empregado?
│  │  │  ├─ Sim → BACEN OK?
│  │  │  │  ├─ Sim → Renda Suficiente?
│  │  │  │  │  ├─ Sim → Dívidas ≤ 40%?
│  │  │  │  │  │  ├─ Sim → ✅ APROVADO
│  │  │  │  │  │  └─ Não → ❌ debt_ratio
│  │  │  │  │  └─ Não → ❌ income
│  │  │  │  └─ Não → ❌ bacen_restriction
│  │  │  └─ Não → ❌ employment
│  │  └─ Não → ❌ credit_score
│  └─ Não → ❌ age_requirement
```

### 2. BFS - Breadth-First Search (Cálculo de Limite)

Explora combinações de produtos em **largura** usando fila:

```python
Queue: [(produto1, parcelas1), (produto2, parcelas2), ...]

Para cada (produto, parcelas):
  - Calcula valor da parcela
  - Verifica se parcela ≤ 30% da renda
  - Se sim, adiciona à lista de opções viáveis
  - Retorna melhor combinação (maior limite aprovado)
```

**Produtos disponíveis:**
- Personal Loan: até R$ 100k, 48x, taxa 2.99%
- Credit Card: até R$ 50k, 12x, taxa 5.99%
- Auto Loan: até R$ 150k, 60x, taxa 1.49%
- Home Loan: até R$ 500k, 360x, taxa 0.89%

### 3. Fuzzy Logic (Avaliação de Risco)

Sistema de **inferência fuzzy** com 3 etapas:

**a) Fuzzificação** - Converte valores numéricos em graus de pertinência:
```
Credit Score:
  - Baixo:  [300, 500] → μ = trapezoidal
  - Médio:  [450, 650] → μ = triangular
  - Alto:   [600, 900] → μ = trapezoidal

Income:
  - Baixo:  [0, 3000]    → μ = trapezoidal
  - Médio:  [2000, 8000] → μ = triangular
  - Alto:   [6000, ∞]    → μ = sigmoid

Debt Ratio:
  - Baixo:  [0, 0.20]     → μ = trapezoidal
  - Médio:  [0.15, 0.35]  → μ = triangular
  - Alto:   [0.30, 1.00]  → μ = trapezoidal
```

**b) Regras Fuzzy** - 6 regras de inferência:
1. SE score ALTO E debt BAIXO → Risco BAIXO
2. SE score ALTO E debt MÉDIO → Risco BAIXO
3. SE score MÉDIO E debt BAIXO → Risco MÉDIO
4. SE score MÉDIO E debt MÉDIO → Risco MÉDIO
5. SE score BAIXO OU debt ALTO → Risco ALTO
6. SE income BAIXO E debt ALTO → Risco ALTO

**c) Defuzzificação** - Método do centroide para obter risco final.

### 4. Neural Network - MLP (Decisão Final)

Rede Neural **Feedforward Multi-Layer Perceptron**:

```
Input Layer (10 neurons):
  - age_normalized
  - credit_score_normalized
  - income_normalized
  - debt_ratio
  - employment_binary
  - bank_account_binary
  - num_inquiries_normalized
  - num_loans_normalized
  - risk_score (da etapa 3)
  - limit_ratio (limite/solicitado)

Hidden Layer (8 neurons):
  - Activation: Sigmoid
  - Pesos inicializados com heurística baseada em regras de negócio

Output Layer (3 neurons):
  - Activation: Softmax
  - [APPROVED, UNDER_REVIEW, REJECTED]
```

**Forward Propagation:**
```python
hidden = sigmoid(input @ weights_input_hidden + bias_hidden)
output = softmax(hidden @ weights_hidden_output + bias_output)
decision = argmax(output)
```

## 📂 Estrutura do Projeto

```
CreditAI/
├── src/
│   ├── domain/                      # Camada de Domínio (Core)
│   │   ├── entities/
│   │   │   ├── credit_request.py    # CustomerProfile, CreditRequest
│   │   │   └── credit_analysis.py   # CreditAnalysisResult, RiskAssessment
│   │   └── services/
│   │       ├── persona_filter_dfs.py        # Etapa 1: DFS
│   │       ├── credit_limit_bfs.py          # Etapa 2: BFS
│   │       ├── risk_fuzzy_logic.py          # Etapa 3: Fuzzy Logic
│   │       └── approval_neural_network.py   # Etapa 4: Neural Network
│   │
│   ├── application/                 # Camada de Aplicação
│   │   └── services/
│   │       └── credit_analysis_service.py   # Orchestrator (4 etapas)
│   │
│   ├── infrastructure/              # Camada de Infraestrutura
│   │   └── adapters/
│   │       ├── database/            # PostgreSQL
│   │       └── cache/               # Redis
│   │
│   ├── interfaces/                  # Camada de Interface
│   │   └── http/
│   │       ├── flask_app.py         # FastAPI App
│   │       └── credit_routes.py     # Credit endpoints
│   │
│   └── main.py                      # Bootstrap & DI
│
├── database/
│   └── init-db.sql                  # Schema com 3 tabelas
│
├── examples/
│   └── credit_analysis_examples.json # 8 cenários de teste
│
├── .devcontainer/
│   ├── devcontainer.json
│   └── docker-compose.yml
│
├── requirements.txt
└── README.md
```

## 🗄️ Banco de Dados

### Tabelas

**customer_profiles** - Perfil do cliente
- Dados demográficos: age, gender, marital_status
- Dados financeiros: income, credit_score, debt_to_income_ratio
- Dados de emprego: employment_status, time_at_job_months
- Restrições: has_bacen_restriction

**credit_requests** - Solicitação de crédito
- requested_amount
- product_type (personal_loan, credit_card, auto_loan, home_loan)
- purpose

**credit_analysis_results** - Resultados completos das 4 etapas
- stage_1: persona_filter_passed, rejection_reason
- stage_2: approved_limit, max_installments, interest_rate
- stage_3: risk_level, risk_score
- stage_4: final_status, confidence_score
- Timestamps e índices para queries otimizadas

## 🔧 Tecnologias

- **Python 3.12**
- **FastAPI** - Framework web moderno e rápido
- **NumPy** - Computação numérica (rede neural)
- **Pydantic** - Validação de dados
- **PostgreSQL 15** - Banco de dados relacional
- **Redis 7** - Cache de alta performance
- **Docker & Docker Compose** - Containerização
- **Uvicorn** - Servidor ASGI

## 📊 Diagrama de Sequência

```
Cliente → FastAPI → CreditAnalysisService
                          ↓
                    [Etapa 1: DFS]
                    PersonaFilterDFS
                          ↓ [passa]
                    [Etapa 2: BFS]
                    CreditLimitBFS
                          ↓
                    [Etapa 3: Fuzzy]
                    RiskFuzzyLogic
                          ↓
                    [Etapa 4: RNA]
                    ApprovalNeuralNetwork
                          ↓
                    CreditAnalysisResult
                          ↓
         PostgreSQL ← Store Result
                          ↓
Cliente ← Response com 4 etapas
```

## 🧑‍💻 Desenvolvimento

### Rodando localmente (sem Docker)

```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_USER=creditai
export POSTGRES_PASSWORD=creditai_dev
export POSTGRES_DB=creditai_db
export REDIS_HOST=localhost
export REDIS_PORT=6379

# Executar aplicação
python -m src.main
```

### Executando testes

```bash
# Instalar dependências de teste
pip install pytest pytest-cov

# Executar testes
pytest

# Com cobertura
pytest --cov=src --cov-report=html
```

## 📈 Próximos Passos

- [ ] Treinamento da rede neural com dados reais
- [ ] Implementar sistema de logging estruturado
- [ ] Adicionar autenticação JWT
- [ ] Criar dashboard de análises
- [ ] Implementar testes automatizados (pytest)
- [ ] Adicionar monitoramento (Prometheus/Grafana)
- [ ] Otimizar regras fuzzy com feedback de produção
- [ ] Implementar versionamento de modelos

## 📝 Licença

Este projeto é desenvolvido para fins educacionais e demonstração de arquitetura hexagonal com IA.

## 👥 Contribuindo

Contribuições são bem-vindas! Siga os princípios da arquitetura hexagonal:
1. Domain Layer não deve ter dependências externas
2. Application Layer coordena, não implementa lógica de negócio
3. Infrastructure Layer pode ser substituído sem afetar o core
4. Interfaces Layer é intercambiável (REST, GraphQL, CLI, etc.)

---

**CreditAI** - Análise de Crédito Inteligente com IA 🧠💳
