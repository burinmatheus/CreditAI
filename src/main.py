"""
Main Entry Point - Dependency Injection & Application Bootstrap
Configura e inicializa a aplicação com arquitetura hexagonal
"""
import uvicorn
from src.config import APP_PORT

# Infrastructure Layer
from src.infrastructure.adapters.database.postgres_connection import PostgresConnection
from src.infrastructure.adapters.cache.redis_connection import RedisConnection
from src.infrastructure.adapters.cache.redis_cache_repository import RedisCacheRepository

# Application Layer
from src.application.services.health_check_service import HealthCheckService
from src.application.services.credit_analysis_service import CreditAnalysisService

# Interface Layer
from src.interfaces.http.fastapi_app import FastAPIApp


def bootstrap_application():
    """
    Bootstrap da aplicação com injeção de dependências
    Segue o padrão de arquitetura hexagonal
    """
    print("🚀 Inicializando CreditAI com Arquitetura Hexagonal...\n")

    # ===== INFRASTRUCTURE LAYER =====
    print("📦 Inicializando camada de infraestrutura...")
    
    # Conexões
    postgres_conn = PostgresConnection()
    postgres_conn.initialize()
    
    redis_conn = RedisConnection()
    redis_conn.initialize()
    
    # Repositories (Adapters)
    cache_repository = RedisCacheRepository(redis_conn)
    
    print("✓ Infraestrutura inicializada\n")

    # ===== APPLICATION LAYER =====
    print("⚙️  Inicializando camada de aplicação...")
    
    health_check_service = HealthCheckService(
        cache_repository=cache_repository
    )
    
    # Serviço de Análise de Crédito com IA (4 etapas)
    credit_analysis_service = CreditAnalysisService()
    
    print("✓ Serviços de aplicação inicializados\n")

    # ===== INTERFACE LAYER =====
    print("🌐 Inicializando camada de interface (FastAPI + OpenAPI)...")
    
    # Criar aplicação FastAPI
    fastapi_app = FastAPIApp(
        health_check_service=health_check_service,
        credit_analysis_service=credit_analysis_service
    )
    
    print("✓ Interface FastAPI + OpenAPI configurada\n")

    return postgres_conn, redis_conn, fastapi_app


def main():
    """Ponto de entrada principal da aplicação"""
    # Bootstrap com injeção de dependências
    postgres_conn, redis_conn, fastapi_app = bootstrap_application()

    # Mensagens de inicialização
    print("=" * 70)
    print(f"✓ Servidor FastAPI rodando na porta {APP_PORT}")
    print(f"  📍 API Root: http://localhost:{APP_PORT}/")
    print(f"  📖 Swagger UI: http://localhost:{APP_PORT}/docs")
    print(f"  📘 ReDoc: http://localhost:{APP_PORT}/redoc")
    print("=" * 70)
    print("\n🎯 Arquitetura Hexagonal + FastAPI aplicados com sucesso!")
    print("   Domain → Application → Infrastructure → Interfaces (FastAPI)\n")

    # Iniciar servidor Uvicorn
    try:
        uvicorn.run(
            fastapi_app.get_app(),
            host="0.0.0.0",
            port=APP_PORT,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n🛑 Encerrando servidor...")
        postgres_conn.close_all()
        redis_conn.close()
        print("✓ Aplicação encerrada com sucesso")


if __name__ == "__main__":
    main()
