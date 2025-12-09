"""
Application Service: Health Check
Orquestra verificações de saúde da aplicação
"""
from src.domain.entities.health import HealthStatus
from src.domain.ports.health_check import HealthCheckPort
from src.domain.ports.user_repository import UserRepositoryPort
from src.domain.ports.cache_repository import CacheRepositoryPort


class HealthCheckService(HealthCheckPort):
    """Serviço de health check que implementa a porta do domínio"""

    def __init__(
        self,
        user_repository: UserRepositoryPort,
        cache_repository: CacheRepositoryPort
    ):
        self.user_repository = user_repository
        self.cache_repository = cache_repository

    def check_database(self) -> bool:
        """Verifica se o banco de dados está saudável"""
        try:
            # Tenta fazer uma operação simples no banco
            self.user_repository.find_all()
            return True
        except Exception:
            return False

    def check_cache(self) -> bool:
        """Verifica se o cache está saudável"""
        try:
            return self.cache_repository.ping()
        except Exception:
            return False

    def get_health_status(self) -> HealthStatus:
        """Retorna o status completo de saúde da aplicação"""
        postgres_status = "up" if self.check_database() else "down"
        redis_status = "up" if self.check_cache() else "down"

        services = {
            "postgres": postgres_status,
            "redis": redis_status
        }

        overall_status = "healthy" if all(s == "up" for s in services.values()) else "unhealthy"

        return HealthStatus(status=overall_status, services=services)
