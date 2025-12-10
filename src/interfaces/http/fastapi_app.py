"""
Interface Adapter: FastAPI REST API with automatic OpenAPI/Swagger Documentation
"""
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from src.application.services.health_check_service import HealthCheckService
from src.application.services.credit_analysis_service import CreditAnalysisService
from src.interfaces.http.credit_routes import create_credit_router


# Pydantic Models (DTOs)
class HealthResponse(BaseModel):
    status: str = Field(..., example="healthy", description="Status geral da aplicação")
    services: dict

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "services": {
                    "api": "up"
                }
            }
        }


class APIInfo(BaseModel):
    status: str


class FastAPIApp:
    """Aplicação FastAPI com documentação OpenAPI/Swagger automática"""

    def __init__(
        self,
        health_check_service: HealthCheckService,
        credit_analysis_service: CreditAnalysisService,
    ):
        self.health_check_service = health_check_service
        self.credit_analysis_service = credit_analysis_service

        # Criar app FastAPI
        self.app = FastAPI(
            title="CreditAI API",
            description="API de análise de crédito com arquitetura hexagonal e IA (DFS, BFS, Fuzzy Logic, Neural Network)",
            version="1.0.0",
            docs_url="/docs",  # Swagger UI
            redoc_url="/redoc",  # ReDoc
            openapi_url="/openapi.json"
        )

        # Registrar rotas
        self._register_routes()

        # Incluir router de análise de crédito
        credit_router = create_credit_router(self.credit_analysis_service)
        self.app.include_router(credit_router)

    def _register_routes(self):
        """Registra todas as rotas da API"""

        @self.app.get(
            "/",
            response_model=APIInfo,
            tags=["Root"],
            summary="Informações da API",
            description="Retorna informações básicas sobre a API e seus endpoints"
        )
        async def root():
            return {"status": "CreditAI API 1"}

        @self.app.get(
            "/api/health",
            response_model=HealthResponse,
            tags=["Health"],
            summary="Health Check",
            description="Verifica o status de saúde da aplicação",
        )
        async def health_check():
            health_status = self.health_check_service.get_health_status()
            is_healthy = all(s == "up" for s in health_status["services"].values())
            status_code = status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
            return HealthResponse(
                status=health_status["status"],
                services=health_status["services"],
            )

    def get_app(self):
        """Retorna a instância do FastAPI app"""
        return self.app
