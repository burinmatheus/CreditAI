from pydantic import BaseModel, Field

from src.interfaces.http.dtos.gender_dto import GenderDTO
from src.interfaces.http.dtos.marital_status_dto import MaritalStatusDTO


class CustomerProfileDTO(BaseModel):
    """DTO para perfil do cliente"""
    customer_id: str = Field(..., description="ID único do cliente")
    name: str = Field(..., description="Nome completo")
    age: int = Field(..., ge=18, le=100, description="Idade (18-100)")
    gender: GenderDTO = Field(..., description="Gênero")
    marital_status: MaritalStatusDTO = Field(..., description="Estado civil")
    employment_status: str = Field(..., description="Status de emprego")
    income: float = Field(..., gt=0, description="Renda mensal")
    debt_to_income_ratio: float = Field(..., ge=0, le=1, description="Razão dívida/renda (0-1)")
    credit_score: int = Field(..., ge=300, le=900, description="Score de crédito (300-900)")
    time_at_job_months: int = Field(..., ge=0, description="Tempo de emprego em meses")
    has_bank_account: bool = Field(..., description="Possui conta bancária")
    has_bacen_restriction: bool = Field(..., description="Possui restrição no BACEN")
    num_credit_inquiries: int = Field(..., ge=0, description="Consultas de crédito recentes")
    num_existing_loans: int = Field(..., ge=0, description="Empréstimos ativos")

    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": "CUST-12345",
                "name": "João da Silva",
                "age": 35,
                "gender": "male",
                "marital_status": "married",
                "employment_status": "employed",
                "income": 8000.00,
                "debt_to_income_ratio": 0.25,
                "credit_score": 720,
                "time_at_job_months": 48,
                "has_bank_account": True,
                "has_bacen_restriction": False,
                "num_credit_inquiries": 1,
                "num_existing_loans": 1,
            }
        }
