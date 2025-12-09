"""
Interface Adapter: FastAPI REST API with automatic OpenAPI/Swagger Documentation
"""
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid

from src.application.services.health_check_service import HealthCheckService
from src.application.services.user_service import UserService
from src.application.services.credit_analysis_service import CreditAnalysisService
from src.interfaces.http.credit_routes import create_credit_router


# Pydantic Models (DTOs)
class HealthServiceStatus(BaseModel):
    postgres: str = Field(..., example="up", description="Status do PostgreSQL")
    redis: str = Field(..., example="up", description="Status do Redis")


class HealthResponse(BaseModel):
    status: str = Field(..., example="healthy", description="Status geral da aplicação")
    services: HealthServiceStatus

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "services": {
                    "postgres": "up",
                    "redis": "up"
                }
            }
        }


class UserResponse(BaseModel):
    id: str = Field(..., example="123e4567-e89b-12d3-a456-426614174000", description="ID único do usuário")
    username: str = Field(..., example="johndoe", description="Nome de usuário")
    email: str = Field(..., example="john@example.com", description="Email do usuário")
    full_name: Optional[str] = Field(None, example="John Doe", description="Nome completo")
    created_at: Optional[str] = Field(None, example="2025-11-21T12:00:00", description="Data de criação")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "username": "johndoe",
                "email": "john@example.com",
                "full_name": "John Doe",
                "created_at": "2025-11-21T12:00:00"
            }
        }


class UsersListResponse(BaseModel):
    users: List[UserResponse]
    count: int = Field(..., example=10, description="Número total de usuários")


class APIInfo(BaseModel):
    status: str


class FastAPIApp:
    """Aplicação FastAPI com documentação OpenAPI/Swagger automática"""

    def __init__(
        self, 
        health_check_service: HealthCheckService, 
        user_service: UserService,
        credit_analysis_service: CreditAnalysisService
    ):
        self.health_check_service = health_check_service
        self.user_service = user_service
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
            """Rota raiz com informações da API"""
            return {
                "status": "CreditAI API 1",
            }
        
        @self.app.get(
            "/api/health",
            response_model=HealthResponse,
            tags=["Health"],
            summary="Health Check",
            description="Verifica o status de saúde da aplicação e seus serviços (PostgreSQL e Redis)",
            responses={
                200: {
                    "description": "Sistema saudável",
                    "content": {
                        "application/json": {
                            "example": {
                                "status": "healthy",
                                "services": {
                                    "postgres": "up",
                                    "redis": "up"
                                }
                            }
                        }
                    }
                },
                503: {
                    "description": "Sistema com problemas",
                    "content": {
                        "application/json": {
                            "example": {
                                "status": "unhealthy",
                                "services": {
                                    "postgres": "down",
                                    "redis": "up"
                                }
                            }
                        }
                    }
                }
            }
        )
        async def health_check():
            """Endpoint de health check"""
            health_status = self.health_check_service.get_health_status()
            status_code = status.HTTP_200_OK if health_status.is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
            
            return HealthResponse(
                status=health_status.status,
                services=HealthServiceStatus(
                    postgres=health_status.services["postgres"],
                    redis=health_status.services["redis"]
                )
            )
        
        @self.app.get(
            "/api/users",
            response_model=UsersListResponse,
            tags=["Users"],
            summary="Listar Usuários",
            description="Retorna a lista completa de todos os usuários cadastrados no sistema",
            responses={
                200: {
                    "description": "Lista de usuários retornada com sucesso"
                },
                500: {
                    "description": "Erro interno do servidor"
                }
            }
        )
        async def list_users():
            """Lista todos os usuários"""
            try:
                users = self.user_service.get_all_users()
                
                users_data = [
                    UserResponse(
                        id=str(user.id),
                        username=user.username,
                        email=user.email,
                        full_name=user.full_name,
                        created_at=user.created_at.isoformat() if user.created_at else None
                    )
                    for user in users
                ]
                
                return UsersListResponse(users=users_data, count=len(users_data))
                
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Erro ao buscar usuários: {str(e)}"
                )
        
        @self.app.get(
            "/api/users/{user_id}",
            response_model=UserResponse,
            tags=["Users"],
            summary="Buscar Usuário por ID",
            description="Busca e retorna as informações de um usuário específico através do seu ID único (UUID)",
            responses={
                200: {
                    "description": "Usuário encontrado com sucesso"
                },
                400: {
                    "description": "ID de usuário inválido (formato UUID incorreto)"
                },
                404: {
                    "description": "Usuário não encontrado"
                },
                500: {
                    "description": "Erro interno do servidor"
                }
            }
        )
        async def get_user(user_id: str):
            """Busca um usuário específico por ID"""
            try:
                user_uuid = uuid.UUID(user_id)
                user = self.user_service.get_user_by_id(user_uuid)
                
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Usuário com ID {user_id} não encontrado"
                    )
                
                return UserResponse(
                    id=str(user.id),
                    username=user.username,
                    email=user.email,
                    full_name=user.full_name,
                    created_at=user.created_at.isoformat() if user.created_at else None
                )
                
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="ID de usuário inválido. Deve ser um UUID válido"
                )
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Erro ao buscar usuário: {str(e)}"
                )

    def get_app(self):
        """Retorna a instância do FastAPI app"""
        return self.app

