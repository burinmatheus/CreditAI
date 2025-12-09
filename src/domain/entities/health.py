"""
Domain Entity: Health Status
Representa o status de saúde dos serviços
"""
from dataclasses import dataclass
from typing import Dict


@dataclass
class HealthStatus:
    """Entidade que representa o status de saúde da aplicação"""
    status: str  # "healthy" ou "unhealthy"
    services: Dict[str, str]  # {"postgres": "up", "redis": "down"}

    @property
    def is_healthy(self) -> bool:
        """Verifica se todos os serviços estão saudáveis"""
        return all(status == "up" for status in self.services.values())
