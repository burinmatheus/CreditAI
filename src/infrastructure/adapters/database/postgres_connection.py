"""
Infrastructure Adapter: PostgreSQL Connection
Gerencia conexões com o banco PostgreSQL
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool
from contextlib import contextmanager
from src.config import POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB


class PostgresConnection:
    """Gerenciador de conexões PostgreSQL"""

    def __init__(self):
        self._pool = None

    def initialize(self, minconn=1, maxconn=10):
        """Inicializa o pool de conexões com o PostgreSQL"""
        if self._pool is None:
            self._pool = ThreadedConnectionPool(
                minconn,
                maxconn,
                user=POSTGRES_USER,
                password=POSTGRES_PASSWORD,
                host=POSTGRES_HOST,
                port=POSTGRES_PORT,
                database=POSTGRES_DB
            )
            print("✓ Pool de conexões PostgreSQL inicializado")

    def close_all(self):
        """Fecha todas as conexões do pool"""
        if self._pool is not None:
            self._pool.closeall()
            self._pool = None
            print("✓ Pool de conexões PostgreSQL fechado")

    @contextmanager
    def get_connection(self):
        """Context manager para obter uma conexão do pool"""
        if self._pool is None:
            self.initialize()
        
        conn = self._pool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self._pool.putconn(conn)

    @contextmanager
    def get_cursor(self, cursor_factory=RealDictCursor):
        """Context manager para obter um cursor"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=cursor_factory)
            try:
                yield cursor
            finally:
                cursor.close()
