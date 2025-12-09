"""
Infrastructure Adapter: Redis Cache Repository
Implementa a porta CacheRepositoryPort usando Redis
"""
from typing import Optional, Any
import json
from src.domain.ports.cache_repository import CacheRepositoryPort
from src.infrastructure.adapters.cache.redis_connection import RedisConnection


class RedisCacheRepository(CacheRepositoryPort):
    """Implementação do repositório de cache usando Redis"""

    def __init__(self, redis_connection: RedisConnection):
        self.redis = redis_connection

    def get(self, key: str) -> Optional[Any]:
        """Obtém um valor do cache"""
        try:
            client = self.redis.get_client()
            value = client.get(key)
            return value
        except Exception as e:
            print(f"Erro ao buscar chave {key} do cache: {e}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Armazena um valor no cache com TTL opcional"""
        try:
            client = self.redis.get_client()
            if ttl:
                client.setex(key, ttl, value)
            else:
                client.set(key, value)
            return True
        except Exception as e:
            print(f"Erro ao salvar chave {key} no cache: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Remove um valor do cache"""
        try:
            client = self.redis.get_client()
            return client.delete(key) > 0
        except Exception as e:
            print(f"Erro ao deletar chave {key} do cache: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Verifica se uma chave existe no cache"""
        try:
            client = self.redis.get_client()
            return client.exists(key) > 0
        except Exception as e:
            print(f"Erro ao verificar existência da chave {key}: {e}")
            return False

    def ping(self) -> bool:
        """Verifica se o cache está disponível"""
        try:
            client = self.redis.get_client()
            return client.ping()
        except Exception:
            return False
