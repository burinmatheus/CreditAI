import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool
from contextlib import contextmanager
from src.config import DATABASE_URL, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB


class DatabaseConnection:
    _pool = None

    @classmethod
    def initialize(cls, minconn=1, maxconn=10):
        """Inicializa o pool de conexões com o PostgreSQL"""
        if cls._pool is None:
            cls._pool = ThreadedConnectionPool(
                minconn,
                maxconn,
                user=POSTGRES_USER,
                password=POSTGRES_PASSWORD,
                host=POSTGRES_HOST,
                port=POSTGRES_PORT,
                database=POSTGRES_DB
            )
            print("✓ Pool de conexões PostgreSQL inicializado")

    @classmethod
    def close_all(cls):
        """Fecha todas as conexões do pool"""
        if cls._pool is not None:
            cls._pool.closeall()
            cls._pool = None
            print("✓ Pool de conexões PostgreSQL fechado")

    @classmethod
    @contextmanager
    def get_connection(cls):
        """Context manager para obter uma conexão do pool"""
        if cls._pool is None:
            cls.initialize()
        
        conn = cls._pool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cls._pool.putconn(conn)

    @classmethod
    @contextmanager
    def get_cursor(cls, cursor_factory=RealDictCursor):
        """Context manager para obter um cursor"""
        with cls.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=cursor_factory)
            try:
                yield cursor
            finally:
                cursor.close()

    @classmethod
    def health_check(cls):
        """Verifica se a conexão com o banco está saudável"""
        try:
            with cls.get_cursor() as cursor:
                cursor.execute("SELECT 1")
                return True
        except Exception as e:
            print(f"✗ Health check PostgreSQL falhou: {e}")
            return False


# Instância global para facilitar o uso
db = DatabaseConnection
