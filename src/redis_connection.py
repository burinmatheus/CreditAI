import redis
from src.config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD


class RedisConnection:
    _client = None

    @classmethod
    def initialize(cls):
        """Inicializa a conexão com o Redis"""
        if cls._client is None:
            cls._client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                password=REDIS_PASSWORD,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            print("✓ Conexão Redis inicializada")

    @classmethod
    def get_client(cls):
        """Retorna o cliente Redis"""
        if cls._client is None:
            cls.initialize()
        return cls._client

    @classmethod
    def close(cls):
        """Fecha a conexão com o Redis"""
        if cls._client is not None:
            cls._client.close()
            cls._client = None
            print("✓ Conexão Redis fechada")

    @classmethod
    def health_check(cls):
        """Verifica se a conexão com o Redis está saudável"""
        try:
            client = cls.get_client()
            return client.ping()
        except Exception as e:
            print(f"✗ Health check Redis falhou: {e}")
            return False


# Instância global para facilitar o uso
redis_client = RedisConnection
