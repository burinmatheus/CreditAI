"""
Domain Entity: Credit Request
Representa uma solicitação de crédito
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum
import uuid


class Gender(str, Enum):
    """Gênero do cliente"""
    MALE = "M"
    FEMALE = "F"
    OTHER = "O"


class MaritalStatus(str, Enum):
    """Estado civil do cliente"""
    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"


class ProductType(str, Enum):
    """Tipos de produtos de crédito"""
    PERSONAL_LOAN = "personal_loan"
    CREDIT_CARD = "credit_card"
    AUTO_LOAN = "auto_loan"
    HOME_LOAN = "home_loan"


@dataclass
class CustomerProfile:
    """Perfil completo do cliente para análise de crédito"""
    # Identificação
    customer_id: str
    name: str
    
    # Dados demográficos
    age: int
    gender: Gender
    marital_status: MaritalStatus
    
    # Dados financeiros
    income: float  # Renda mensal
    credit_score: int  # Score de crédito (300-900)
    debt_to_income_ratio: float  # Percentual de endividamento (0-1)
    
    # Emprego
    employment_status: str  # "employed", "self_employed", "unemployed"
    time_at_job_months: int  # Tempo no emprego atual
    
    # Histórico bancário
    has_bank_account: bool
    has_bacen_restriction: bool  # Restrição no BACEN
    
    # Histórico de crédito
    num_credit_inquiries: int  # Consultas de crédito recentes
    num_existing_loans: int  # Empréstimos ativos
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Valida o perfil do cliente"""
        if not 18 <= self.age <= 100:
            return False, "Idade deve estar entre 18 e 100 anos"
        
        if self.income <= 0:
            return False, "Renda deve ser maior que zero"
        
        if not 300 <= self.credit_score <= 900:
            return False, "Credit score deve estar entre 300 e 900"
        
        if not 0 <= self.debt_to_income_ratio <= 1:
            return False, "Debt-to-income ratio deve estar entre 0 e 1"
        
        if self.time_at_job_months < 0:
            return False, "Tempo de emprego não pode ser negativo"
        
        return True, None


@dataclass
class CreditRequest:
    """Solicitação de crédito completa"""
    customer_profile: CustomerProfile
    requested_amount: float
    product_type: ProductType
    purpose: Optional[str] = None
    requested_installments: int = 12
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Valida a solicitação de crédito"""
        # Validar perfil do cliente
        profile_valid, profile_error = self.customer_profile.validate()
        if not profile_valid:
            return False, profile_error
        
        if self.requested_amount <= 0:
            return False, "Valor solicitado deve ser maior que zero"
        
        if self.requested_installments <= 0:
            return False, "Número de parcelas deve ser maior que zero"
        
        return True, None
