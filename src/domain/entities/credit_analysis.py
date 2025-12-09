"""
Domain Entity: Credit Analysis Result
Representa o resultado de uma análise de crédito
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum
import uuid


class ApprovalStatus(str, Enum):
    """Status de aprovação do crédito"""
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING_REVIEW = "pending_review"


class RejectionReason(str, Enum):
    """Razões de rejeição de crédito"""
    LOW_INCOME = "low_income"
    HIGH_RISK = "high_risk"
    INSUFFICIENT_CREDIT_SCORE = "insufficient_credit_score"
    HIGH_DEBT_RATIO = "high_debt_ratio"
    PERSONA_MISMATCH = "persona_mismatch"
    EMPLOYMENT_ISSUES = "employment_issues"
    AGE_RESTRICTION = "age_restriction"
    PERSONA_FILTER = "persona_filter"
    OTHER = "other"


class RiskLevel(str, Enum):
    """Níveis de risco"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class PersonaFilterResult:
    """Resultado do filtro de persona"""
    passed: bool
    persona: Optional[str]
    confidence: float
    reason: Optional[str] = None
    decision_path: Optional[List[str]] = None


@dataclass
class CreditLimit:
    """Limite de crédito calculado"""
    approved_amount: float
    max_installment_value: float
    max_installments: int
    interest_rate: float
    factors: Dict[str, float]


@dataclass
class RiskAssessment:
    """Avaliação de risco de inadimplência"""
    risk_level: RiskLevel
    risk_score: float  # 0.0 - 1.0
    risk_factors: Dict[str, float]
    main_risk_factors: List[str]
    confidence_score: float
    fuzzy_memberships: Optional[Dict[str, float]] = None
    
    def should_reject(self, threshold: float = 0.7) -> bool:
        """Determina se o risco justifica rejeição"""
        return self.risk_score >= threshold or self.risk_level == RiskLevel.VERY_HIGH


@dataclass
class CreditAnalysisResult:
    """Resultado da análise de crédito"""
    request_id: str
    customer_id: str
    analysis_date: datetime
    persona_filter: PersonaFilterResult
    credit_limit: Optional[CreditLimit]
    risk_assessment: Optional[RiskAssessment]
    approval_status: ApprovalStatus
    rejection_reason: Optional[RejectionReason] = None
    approval_confidence: float = 0.0
    neural_network_probabilities: Optional[Dict[str, float]] = None
    approved_amount: float = 0.0
    approved_installments: int = 0
    approved_interest_rate: float = 0.0
    monthly_payment: float = 0.0
    neural_network_confidence: Optional[float] = None
    
    def __post_init__(self):
        if self.neural_network_confidence is None:
            self.neural_network_confidence = self.approval_confidence
