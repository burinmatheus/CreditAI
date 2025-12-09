from pydantic import BaseModel
from typing import Optional, List


class CreditAnalysisResponseDTO(BaseModel):
    """DTO para resposta da análise"""
    request_id: str
    customer_id: str
    analysis_date: str
    approval_status: str
    rejection_reason: Optional[str]

    # Etapa 1: Filtro por Persona
    persona_filter_passed: bool
    persona_decision_path: List[str]

    # Etapa 2: Limite de Crédito
    credit_limit_amount: float
    max_installment_value: float
    max_installments: int
    interest_rate: float

    # Etapa 3: Avaliação de Risco
    risk_level: str
    risk_score: float
    risk_description: str

    # Etapa 4: Decisão Final
    neural_network_confidence: float

    # Valores Aprovados (se aplicável)
    approved_amount: float
    approved_installments: int
    monthly_payment: float
    total_to_pay: float

    summary: str
