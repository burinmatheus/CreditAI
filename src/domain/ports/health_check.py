"""
Port: Health Check Service (Interface)
Define o contrato para verificação de saúde dos serviços
"""
from abc import ABC, abstractmethod
from src.domain.entities.health import HealthStatus


class HealthCheckPort(ABC):
    """Interface que define operações de health check"""

    @abstractmethod
    def check_database(self) -> bool:
        """Verifica se o banco de dados está saudável"""
        pass

    @abstractmethod
    def check_cache(self) -> bool:
        """Verifica se o cache está saudável"""
        pass

    @abstractmethod
    def get_health_status(self) -> HealthStatus:
        """Retorna o status completo de saúde da aplicação"""
        pass
