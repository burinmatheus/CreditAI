"""
API Endpoints para Análise de Crédito.
"""
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from src.domain.entities.credit_request import (
    CreditRequest,
    CustomerProfile,
    Gender,
    MaritalStatus,
    ProductType,
)
from src.application.services.credit_analysis_service import CreditAnalysisService
from src.interfaces.http.dtos.credit_request_dto import CreditRequestDTO
from src.interfaces.http.dtos.credit_analysis_response_dto import CreditAnalysisResponseDTO

router = APIRouter(prefix="/api/credit", tags=["Análise de Crédito"])

# Serviço é injetado no bootstrap
credit_analysis_service: CreditAnalysisService | None = None


class TrainRequestDTO(BaseModel):
    epochs: int = Field(30, ge=1, le=200)
    lr: float = Field(1e-3, gt=0, le=1e-1)
    batch_size: int = Field(64, ge=8, le=512)


class TrainResponseDTO(BaseModel):
    status: str
    loss: float
    samples: int
    epochs: int
    model_path: str


class GenerateDataRequestDTO(BaseModel):
    num_samples: int = Field(1000, ge=100, le=20000)
    filename: str | None = Field(None, description="Nome opcional do arquivo JSONL")


class GenerateDataResponseDTO(BaseModel):
    status: str
    samples: int
    path: str


def create_credit_router(service: CreditAnalysisService) -> APIRouter:
    global credit_analysis_service
    credit_analysis_service = service
    return router


@router.post(
    "/analyze",
    response_model=CreditAnalysisResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Analisa solicitação de crédito",
    description="""
    Executa análise completa de crédito usando pipeline de 4 técnicas de IA:
    1. DFS: Filtro por persona
    2. BFS: Limite de crédito
    3. Lógica Fuzzy: Risco
    4. RNA (PyTorch): Decisão final
    """,
)
async def analyze_credit(request: CreditRequestDTO):
    if credit_analysis_service is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="CreditAnalysisService não configurado")
    try:
        customer_profile = CustomerProfile(
            customer_id=request.customer_profile.customer_id,
            name=request.customer_profile.name,
            age=request.customer_profile.age,
            gender=Gender(request.customer_profile.gender.value),
            marital_status=MaritalStatus(request.customer_profile.marital_status.value),
            income=request.customer_profile.income,
            credit_score=request.customer_profile.credit_score,
            debt_to_income_ratio=request.customer_profile.debt_to_income_ratio,
            employment_status=request.customer_profile.employment_status,
            time_at_job_months=request.customer_profile.time_at_job_months,
            has_bank_account=request.customer_profile.has_bank_account,
            has_bacen_restriction=request.customer_profile.has_bacen_restriction,
            num_credit_inquiries=request.customer_profile.num_credit_inquiries,
            num_existing_loans=request.customer_profile.num_existing_loans,
        )
        credit_request = CreditRequest(
            customer_profile=customer_profile,
            product_type=ProductType(request.product_type.value),
            requested_amount=request.requested_amount,
            requested_installments=request.requested_installments,
            purpose=request.purpose,
        )
        result = credit_analysis_service.analyze(credit_request)
        return CreditAnalysisResponseDTO(
            request_id=result.request_id,
            customer_id=result.customer_id,
            analysis_date=result.analysis_date.isoformat(),
            approval_status=result.approval_status.value,
            rejection_reason=result.rejection_reason.value if result.rejection_reason else None,
            persona_filter_passed=result.persona_filter.passed,
            persona_decision_path=result.persona_filter.decision_path or [],
            credit_limit_amount=result.credit_limit.approved_amount if result.credit_limit else 0.0,
            max_installment_value=result.credit_limit.max_installment_value if result.credit_limit else 0.0,
            max_installments=result.credit_limit.max_installments if result.credit_limit else 0,
            interest_rate=result.credit_limit.interest_rate if result.credit_limit else 0.0,
            risk_level=result.risk_assessment.risk_level.value if result.risk_assessment else "unknown",
            risk_score=result.risk_assessment.risk_score if result.risk_assessment else 0.0,
            risk_description="",
            neural_network_confidence=result.neural_network_confidence or 0.0,
            approved_amount=result.approved_amount,
            approved_installments=result.approved_installments,
            monthly_payment=result.monthly_payment,
            total_to_pay=result.monthly_payment * result.approved_installments,
            summary=credit_analysis_service.get_analysis_summary(result),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Dados inválidos: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao processar análise: {str(e)}")


@router.get(
    "/products",
    summary="Lista produtos de crédito disponíveis",
    description="Retorna informações sobre os produtos de crédito oferecidos",
)
async def list_products():
    from src.domain.services.credit_limit_bfs import CreditLimitBFS
    config = CreditLimitBFS.PRODUCT_CONFIG
    products = []
    for product_type, settings in config.items():
        products.append(
            {
                "type": product_type.value,
                "name": product_type.value.replace("_", " ").title(),
                "min_amount": settings["min_amount"],
                "max_amount": settings["max_amount"],
                "max_installments": settings["max_installments"],
                "base_rate": settings["base_rate"],
                "base_rate_percent": settings["base_rate"] * 100,
            }
        )
    return {"products": products}


@router.get(
    "/health",
    summary="Health check",
    description="Verifica se o serviço de análise está operacional",
)
async def health_check():
    return {
        "status": "healthy",
        "service": "credit_analysis",
        "techniques": [
            "DFS (Depth-First Search)",
            "BFS (Breadth-First Search)",
            "Fuzzy Logic",
            "Neural Network",
        ],
        "timestamp": datetime.now().isoformat(),
    }


@router.post(
    "/generate-data",
    response_model=GenerateDataResponseDTO,
    summary="Gera dataset sintético em JSONL",
    description="Cria um arquivo JSONL com dados de treino sintéticos no diretório data/training.",
)
async def generate_data(body: GenerateDataRequestDTO):
    if credit_analysis_service is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="CreditAnalysisService não configurado")
    try:
        path = credit_analysis_service.approval_network.generate_dataset_jsonl(
            num_samples=body.num_samples,
            filename=body.filename,
        )
        return GenerateDataResponseDTO(status="ok", samples=body.num_samples, path=str(path))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao gerar dados: {str(e)}")


@router.post(
    "/train-from-file",
    response_model=TrainResponseDTO,
    summary="Treina a RNA a partir de um JSONL existente",
    description="Lê um JSONL (features/label) no diretório data/training e treina a rede, salvando e recarregando pesos.",
)
async def train_from_file(filename: str, body: TrainRequestDTO):
    if credit_analysis_service is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="CreditAnalysisService não configurado")
    jsonl_path = Path("/workspaces/CreditAI/data/training") / filename
    if not jsonl_path.exists():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Arquivo não encontrado: {jsonl_path}")
    try:
        result = credit_analysis_service.approval_network.train_from_jsonl(
            jsonl_path=jsonl_path,
            epochs=body.epochs,
            lr=body.lr,
            batch_size=body.batch_size,
        )
        return TrainResponseDTO(
            status="ok",
            loss=result["loss"],
            samples=result.get("samples", 0),
            epochs=body.epochs,
            model_path=str(credit_analysis_service.approval_network.model_path),
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao treinar a partir do arquivo: {str(e)}")
