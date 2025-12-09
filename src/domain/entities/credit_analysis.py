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
    persona_type: Optional[str]
    confidence: float
    persona_limits: Optional[Dict[str, float]] = None


@dataclass
class CreditLimit:
    """Limite de crédito calculado"""
    approved_limit: float
    calculation_factors: Dict[str, float]


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
    id: uuid.UUID
    credit_request_id: uuid.UUID
    status: ApprovalStatus
    approved_limit: float
    risk_score: float
    rejection_reasons: Optional[List[RejectionReason]] = None
    persona_type: Optional[str] = None
    confidence_score: float = 0.0
    analysis_details: Optional[dict] = None
    analyzed_at: datetime = None
    
    def __post_init__(self):
        if self.analyzed_at is None:
            self.analyzed_at = datetime.now()
        
        if self.rejection_reasons is None:
            self.rejection_reasons = []
    
    def add_rejection_reason(self, reason: RejectionReason):
        """Adiciona uma razão de rejeição"""
        if reason not in self.rejection_reasons:
            self.rejection_reasons.append(reason)
    
    def is_approved(self) -> bool:
        """Verifica se o crédito foi aprovado"""
        return self.status == ApprovalStatus.APPROVED
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            "id": str(self.id),
            "credit_request_id": str(self.credit_request_id),
            "status": self.status.value,
            "approved_limit": self.approved_limit,
            "risk_score": self.risk_score,
            "rejection_reasons": [r.value for r in self.rejection_reasons] if self.rejection_reasons else [],
            "persona_type": self.persona_type,
            "confidence_score": self.confidence_score,
            "analysis_details": self.analysis_details,
            "analyzed_at": self.analyzed_at.isoformat() if self.analyzed_at else None
        }
