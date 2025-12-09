"""
Port: Cache Repository (Interface)
Define o contrato para operações de cache
"""
from abc import ABC, abstractmethod
from typing import Optional, Any


class CacheRepositoryPort(ABC):
    """Interface que define operações de cache"""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Obtém um valor do cache"""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Armazena um valor no cache com TTL opcional"""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Remove um valor do cache"""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Verifica se uma chave existe no cache"""
        pass

    @abstractmethod
    def ping(self) -> bool:
        """Verifica se o cache está disponível"""
        pass
