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
│                    DOMAIN LAYER (Core)                    │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ Entities: CreditRequest, CustomerProfile,           │  │
│  │           CreditAnalysisResult, RiskAssessment      │  │
│  │                                                     │  │
│  │ Services: PersonaFilterDFS, CreditLimitBFS,         │  │
│  │           RiskFuzzyLogic, ApprovalNeuralNetwork     │  │
│  └─────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────┘
                            ↕
┌───────────────────────────────────────────────────────────┐
│                  APPLICATION LAYER                        │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ CreditAnalysisService (Orchestrator)                │  │
│  │ - Executa pipeline completo de 4 etapas             │  │
│  │ - Coordena serviços de domínio                      │  │
│  │ - Gera resumo de análise                            │  │
│  └─────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────┘
                            ↕
┌───────────────────────────────────────────────────────────┐
│              INFRASTRUCTURE LAYER (Adapters)              │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ (Não utilizado no momento)                          │  │
│  └─────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────┘
                            ↕
┌───────────────────────────────────────────────────────────┐
│               INTERFACES LAYER (HTTP/API)                 │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ FastAPI REST API:                                   │  │
│  │ - POST /api/credit/analyze                          │  │
│  │ - GET  /api/credit/products                         │  │
│  │ - GET  /api/credit/health                           │  │
│  │                                                     │  │
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
  - Python 3.12
  - Todas as dependências instaladas

4. Acesse a aplicação:
   - API: http://localhost:8000
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc
CreditAI/ 
## 📡 API Endpoints

### POST /api/credit/analyze
Executa análise completa de crédito em 4 etapas.

**Request Body:** (usa DTO `CreditRequestDTO`)
```json
{
  "customer_profile": {
    "customer_id": "CUST-001",
    "name": "João da Silva",
    "age": 35,
    "gender": "M",
    "marital_status": "married",
    "employment_status": "employed",
    "income": 8500.0,
│   │   └── adapters/                # (vazio no momento)
    "time_at_job_months": 48,
    "has_bank_account": true,
    "has_bacen_restriction": false,
    "num_credit_inquiries": 2,
    "num_existing_loans": 1
  },
  "product_type": "personal_loan",
  "requested_amount": 25000.0,
```

**Response:** (DTO `CreditAnalysisResponseDTO`)
```json
{
  "request_id": "REQ-123e4567-e89b-12d3-a456-426614174000",
  "customer_id": "CUST-001",
  "analysis_date": "2025-12-09T12:30:15.123Z",
  "approval_status": "APPROVED",
  "rejection_reason": null,

  "persona_filter_passed": true,
  "persona_decision_path": ["age_ok", "bacen_ok", "score_ok"],

  "credit_limit_amount": 25000.0,
  "max_installment_value": 850.0,
  "risk_score": 2.1,
  "risk_description": "Low default risk",
  "approved_amount": 25000.0,
  "approved_installments": 36,
```

### GET /api/credit/products
      "type": "personal_loan",
      "name": "Personal Loan",
      "min_amount": 1000.0,
      "max_amount": 50000.0,
      "max_installments": 48,
      "base_rate": 0.025,
      "base_rate_percent": 2.5
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

## 📈 MLflow – acompanhando os treinos

O projeto registra treinos da rede neural no MLflow.

### Subir a UI local do MLflow
```bash
mlflow ui \
  --backend-store-uri file:///workspaces/CreditAI/mlruns \
  --host 0.0.0.0 \
  --port 5050 \
  --allowed-hosts="*" \
  --cors-allowed-origins="*"
```
- Acesse via port-forward do devcontainer: http://localhost:5050 (ajuste o port-forward se necessário).
  - Se aparecer 403/host não autorizado, confirme que o port-forward usa `localhost` ou `127.0.0.1`; com `--allowed-hosts "localhost,127.0.0.1"` ambos são aceitos.

### O que é logado
- Parâmetros: epochs, lr, batch_size, weight_decay, método (synthetic/jsonl), num_samples/samples.
- Métricas: loss por época, loss final.

### Fluxo rápido
1. Gere dados sintéticos: `POST /api/credit/generate-data`.
2. Treine a partir de JSONL existente: `POST /api/credit/train-from-file` (forneça `filename`).
3. Abra a UI do MLflow (comando acima) e visualize runs, métricas e artefatos.
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
│   │       └── (vazio)              # Sem dependências externas
│   │
│   ├── interfaces/                  # Camada de Interface
│   │   └── http/
│   │       ├── fastapi_app.py       # FastAPI App
│   │       └── credit_routes.py     # Credit endpoints
│   │
│   └── main.py                      # Bootstrap & DI
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

## 🔧 Tecnologias

- **Python 3.12**
- **FastAPI** - Framework web moderno e rápido
- **NumPy** - Computação numérica (rede neural)
- **Pydantic** - Validação de dados
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

# Executar aplicação
python -m src.main
```

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
