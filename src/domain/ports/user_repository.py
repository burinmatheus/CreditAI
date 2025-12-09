"""
Port: User Repository (Interface)
Define o contrato para operações de persistência de usuários
"""
from abc import ABC, abstractmethod
from typing import Optional, List
import uuid
from src.domain.entities.user import User


class UserRepositoryPort(ABC):
    """Interface que define operações de repositório para User"""

    @abstractmethod
    def find_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Busca um usuário por ID"""
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        """Busca um usuário por email"""
        pass

    @abstractmethod
    def find_by_username(self, username: str) -> Optional[User]:
        """Busca um usuário por username"""
        pass

    @abstractmethod
    def find_all(self) -> List[User]:
        """Retorna todos os usuários"""
        pass

    @abstractmethod
    def save(self, user: User) -> User:
        """Salva ou atualiza um usuário"""
        pass

    @abstractmethod
    def delete(self, user_id: uuid.UUID) -> bool:
        """Remove um usuário"""
        pass
