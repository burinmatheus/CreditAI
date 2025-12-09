"""
Domain Entity: User
Representa a entidade de usuário no núcleo do domínio
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class User:
    """Entidade User do domínio"""
    id: uuid.UUID
    username: str
    email: str
    password_hash: str
    full_name: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

    def update_name(self, full_name: str):
        """Atualiza o nome completo do usuário"""
        self.full_name = full_name
        self.updated_at = datetime.now()
