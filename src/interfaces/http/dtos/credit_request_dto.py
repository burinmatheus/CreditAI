from pydantic import BaseModel, Field
from typing import Optional

from src.interfaces.http.dtos.customer_profile_dto import CustomerProfileDTO
from src.interfaces.http.dtos.product_type_dto import ProductTypeDTO


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
                "customer_profile": CustomerProfileDTO.Config.json_schema_extra["example"],
                "product_type": "personal_loan",
                "requested_amount": 15000.00,
                "requested_installments": 24,
                "purpose": "Reforma residencial",
            }
        }
