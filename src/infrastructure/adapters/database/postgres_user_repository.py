"""
Infrastructure Adapter: PostgreSQL User Repository
Implementa a porta UserRepositoryPort usando PostgreSQL
"""
from typing import Optional, List
import uuid
from src.domain.entities.user import User
from src.domain.ports.user_repository import UserRepositoryPort
from src.infrastructure.adapters.database.postgres_connection import PostgresConnection


class PostgresUserRepository(UserRepositoryPort):
    """Implementação do repositório de usuários usando PostgreSQL"""

    def __init__(self, db_connection: PostgresConnection):
        self.db = db_connection

    def find_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Busca um usuário por ID"""
        with self.db.get_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE id = %s",
                (str(user_id),)
            )
            row = cursor.fetchone()
            return self._row_to_user(row) if row else None

    def find_by_email(self, email: str) -> Optional[User]:
        """Busca um usuário por email"""
        with self.db.get_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE email = %s",
                (email,)
            )
            row = cursor.fetchone()
            return self._row_to_user(row) if row else None

    def find_by_username(self, username: str) -> Optional[User]:
        """Busca um usuário por username"""
        with self.db.get_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE username = %s",
                (username,)
            )
            row = cursor.fetchone()
            return self._row_to_user(row) if row else None

    def find_all(self) -> List[User]:
        """Retorna todos os usuários"""
        with self.db.get_cursor() as cursor:
            cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
            rows = cursor.fetchall()
            return [self._row_to_user(row) for row in rows]

    def save(self, user: User) -> User:
        """Salva ou atualiza um usuário"""
        with self.db.get_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (id, username, email, password_hash, full_name, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    username = EXCLUDED.username,
                    email = EXCLUDED.email,
                    password_hash = EXCLUDED.password_hash,
                    full_name = EXCLUDED.full_name,
                    updated_at = EXCLUDED.updated_at
                RETURNING *
                """,
                (
                    str(user.id),
                    user.username,
                    user.email,
                    user.password_hash,
                    user.full_name,
                    user.created_at,
                    user.updated_at
                )
            )
            row = cursor.fetchone()
            return self._row_to_user(row)

    def delete(self, user_id: uuid.UUID) -> bool:
        """Remove um usuário"""
        with self.db.get_cursor() as cursor:
            cursor.execute(
                "DELETE FROM users WHERE id = %s",
                (str(user_id),)
            )
            return cursor.rowcount > 0

    def _row_to_user(self, row: dict) -> User:
        """Converte uma linha do banco para entidade User"""
        return User(
            id=uuid.UUID(row['id']) if isinstance(row['id'], str) else row['id'],
            username=row['username'],
            email=row['email'],
            password_hash=row['password_hash'],
            full_name=row.get('full_name'),
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at')
        )
