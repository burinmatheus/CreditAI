"""
Application Service: Health Check
Retorna estado estático da API (sem dependências externas)
"""


class HealthCheckService:
    """Serviço simples de health check"""

    def get_health_status(self) -> dict:
        services = {"api": "up"}
        return {"status": "healthy", "services": services}
