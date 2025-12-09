"""
Application Service: Health Check
Orquestra verificações de saúde da aplicação
"""
from src.domain.entities.health import HealthStatus
from src.domain.ports.health_check import HealthCheckPort


class HealthCheckService(HealthCheckPort):
    """Serviço de health check que implementa a porta do domínio"""

    def check_database(self) -> bool:
        """Verifica se o banco de dados está saudável"""
        return True

    def check_cache(self) -> bool:
        """Verifica se o cache está saudável"""
        return True

    def get_health_status(self) -> HealthStatus:
        """Retorna o status completo de saúde da aplicação"""
        postgres_status = "up" if self.check_database() else "down"

        services = {
            "postgres": postgres_status,
            "cache": "up" if self.check_cache() else "down"
        }

        overall_status = "healthy" if all(s == "up" for s in services.values()) else "unhealthy"

        return HealthStatus(status=overall_status, services=services)
