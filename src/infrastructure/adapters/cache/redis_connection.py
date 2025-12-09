"""
Infrastructure Adapter: Redis Connection
Gerencia conexão com o Redis
"""
import redis
from src.config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD


class RedisConnection:
    """Gerenciador de conexão Redis"""

    def __init__(self):
        self._client = None

    def initialize(self):
        """Inicializa a conexão com o Redis"""
        if self._client is None:
            self._client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                password=REDIS_PASSWORD,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            print("✓ Conexão Redis inicializada")

    def get_client(self):
        """Retorna o cliente Redis"""
        if self._client is None:
            self.initialize()
        return self._client

    def close(self):
        """Fecha a conexão com o Redis"""
        if self._client is not None:
            self._client.close()
            self._client = None
            print("✓ Conexão Redis fechada")
