"""
API Endpoints para Análise de Crédito
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

from src.domain.entities.credit_request import (
    CreditRequest, CustomerProfile, Gender, MaritalStatus, ProductType
)
from src.application.services.credit_analysis_service import CreditAnalysisService


# ===== DTOs (Data Transfer Objects) =====

class GenderDTO(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class MaritalStatusDTO(str, Enum):
    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"


class ProductTypeDTO(str, Enum):
    PERSONAL_LOAN = "personal_loan"
    CREDIT_CARD = "credit_card"
    VEHICLE_FINANCING = "vehicle_financing"
    HOME_EQUITY = "home_equity"


class CustomerProfileDTO(BaseModel):
    """DTO para perfil do cliente"""
    customer_id: str = Field(..., description="ID único do cliente")
    name: str = Field(..., description="Nome completo")
    age: int = Field(..., ge=18, le=100, description="Idade (18-100)")
    gender: GenderDTO = Field(..., description="Gênero")
    marital_status: MaritalStatusDTO = Field(..., description="Estado civil")
    profession: str = Field(..., description="Profissão")
    monthly_income: float = Field(..., gt=0, description="Renda mensal bruta")
    net_income: float = Field(..., gt=0, description="Renda líquida")
    employment_time_months: int = Field(..., ge=0, description="Tempo de emprego em meses")
    credit_score: int = Field(..., ge=0, le=1000, description="Score de crédito (0-1000)")
    has_bacen_restrictions: bool = Field(..., description="Possui restrições BACEN")
    has_bureau_restrictions: bool = Field(..., description="Possui restrições em birô")
    late_payments_count: int = Field(..., ge=0, description="Quantidade de atrasos")
    distance_from_branch_km: float = Field(..., ge=0, description="Distância da agência (km)")
    existing_debt: float = Field(..., ge=0, description="Dívidas existentes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": "CUST-12345",
                "name": "João da Silva",
                "age": 35,
                "gender": "male",
                "marital_status": "married",
                "profession": "Engenheiro",
                "monthly_income": 8000.00,
                "net_income": 6500.00,
                "employment_time_months": 48,
                "credit_score": 720,
                "has_bacen_restrictions": False,
                "has_bureau_restrictions": False,
                "late_payments_count": 1,
                "distance_from_branch_km": 15.5,
                "existing_debt": 1200.00
            }
        }


class CreditRequestDTO(BaseModel):
    """DTO para solicitação de crédito"""
    customer_profile: CustomerProfileDTO
    product_type: ProductTypeDTO
    requested_amount: float = Field(..., gt=0, description="Valor solicitado")
    requested_installments: int = Field(..., gt=0, le=120, description="Número de parcelas")
    purpose: Optional[str] = Field(None, description="Finalidade do crédito")
    
    class Config:
        json_schema_extra = {
            "example": {
                "customer_profile": {
                    "customer_id": "CUST-12345",
                    "name": "João da Silva",
                    "age": 35,
                    "gender": "male",
                    "marital_status": "married",
                    "profession": "Engenheiro",
                    "monthly_income": 8000.00,
                    "net_income": 6500.00,
                    "employment_time_months": 48,
                    "credit_score": 720,
                    "has_bacen_restrictions": False,
                    "has_bureau_restrictions": False,
                    "late_payments_count": 1,
                    "distance_from_branch_km": 15.5,
                    "existing_debt": 1200.00
                },
                "product_type": "personal_loan",
                "requested_amount": 15000.00,
                "requested_installments": 24,
                "purpose": "Reforma residencial"
            }
        }


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


# ===== Router =====

router = APIRouter(prefix="/api/credit", tags=["Análise de Crédito"])

# Instância do serviço (singleton)
credit_analysis_service = CreditAnalysisService()


@router.post(
    "/analyze",
    response_model=CreditAnalysisResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Analisa solicitação de crédito",
    description="""
    Executa análise completa de crédito usando pipeline de 4 técnicas de IA:
    
    1. **Busca em Profundidade (DFS)**: Filtro por persona
    2. **Busca em Amplitude (BFS)**: Cálculo de limite de crédito
    3. **Lógica Fuzzy**: Avaliação de risco de inadimplência
    4. **Rede Neural Artificial**: Decisão final de aprovação
    
    Retorna decisão completa com detalhes de cada etapa.
    """
)
async def analyze_credit(request: CreditRequestDTO):
    """Analisa solicitação de crédito"""
    try:
        # Converte DTO para entidade de domínio
        customer_profile = CustomerProfile(
            customer_id=request.customer_profile.customer_id,
            name=request.customer_profile.name,
            age=request.customer_profile.age,
            gender=Gender(request.customer_profile.gender.value),
            marital_status=MaritalStatus(request.customer_profile.marital_status.value),
            profession=request.customer_profile.profession,
            monthly_income=request.customer_profile.monthly_income,
            net_income=request.customer_profile.net_income,
            employment_time_months=request.customer_profile.employment_time_months,
            credit_score=request.customer_profile.credit_score,
            has_bacen_restrictions=request.customer_profile.has_bacen_restrictions,
            has_bureau_restrictions=request.customer_profile.has_bureau_restrictions,
            late_payments_count=request.customer_profile.late_payments_count,
            distance_from_branch_km=request.customer_profile.distance_from_branch_km,
            existing_debt=request.customer_profile.existing_debt
        )
        
        credit_request = CreditRequest(
            request_id=f"REQ-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            customer_profile=customer_profile,
            product_type=ProductType(request.product_type.value),
            requested_amount=request.requested_amount,
            requested_installments=request.requested_installments,
            request_date=datetime.now(),
            purpose=request.purpose
        )
        
        # Executa análise
        result = credit_analysis_service.analyze(credit_request)
        
        # Converte resultado para DTO
        return CreditAnalysisResponseDTO(
            request_id=result.request_id,
            customer_id=result.customer_id,
            analysis_date=result.analysis_date.isoformat(),
            approval_status=result.approval_status.value,
            rejection_reason=result.rejection_reason.value if result.rejection_reason else None,
            
            # Etapa 1
            persona_filter_passed=not result.persona_filter.should_reject,
            persona_decision_path=result.persona_filter.decision_path,
            
            # Etapa 2
            credit_limit_amount=result.credit_limit.approved_amount if result.credit_limit else 0.0,
            max_installment_value=result.credit_limit.max_installment_value if result.credit_limit else 0.0,
            max_installments=result.credit_limit.max_installments if result.credit_limit else 0,
            interest_rate=result.credit_limit.interest_rate if result.credit_limit else 0.0,
            
            # Etapa 3
            risk_level=result.risk_assessment.risk_level.value if result.risk_assessment else "unknown",
            risk_score=result.risk_assessment.risk_score if result.risk_assessment else 0.0,
            risk_description=result.risk_assessment.get_risk_description() if result.risk_assessment else "",
            
            # Etapa 4
            neural_network_confidence=result.neural_network_confidence or 0.0,
            
            # Valores aprovados
            approved_amount=result.approved_amount,
            approved_installments=result.approved_installments,
            monthly_payment=result.monthly_payment,
            total_to_pay=result.monthly_payment * result.approved_installments,
            
            summary=credit_analysis_service.get_analysis_summary(result)
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dados inválidos: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar análise: {str(e)}"
        )


@router.get(
    "/products",
    summary="Lista produtos de crédito disponíveis",
    description="Retorna informações sobre os produtos de crédito oferecidos"
)
async def list_products():
    """Lista produtos de crédito"""
    from src.domain.services.credit_limit_bfs import CreditLimitBFS
    
    config = CreditLimitBFS.PRODUCT_CONFIG
    
    products = []
    for product_type, settings in config.items():
        products.append({
            "type": product_type.value,
            "name": product_type.value.replace("_", " ").title(),
            "min_amount": settings['min_amount'],
            "max_amount": settings['max_amount'],
            "max_installments": settings['max_installments'],
            "base_rate": settings['base_rate'],
            "base_rate_percent": settings['base_rate'] * 100
        })
    
    return {"products": products}


@router.get(
    "/health",
    summary="Health check",
    description="Verifica se o serviço de análise está operacional"
)
async def health_check():
    """Health check do serviço de análise de crédito"""
    return {
        "status": "healthy",
        "service": "credit_analysis",
        "techniques": [
            "DFS (Depth-First Search)",
            "BFS (Breadth-First Search)",
            "Fuzzy Logic",
            "Neural Network"
        ],
        "timestamp": datetime.now().isoformat()
    }
