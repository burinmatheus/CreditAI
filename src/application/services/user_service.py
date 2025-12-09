"""
Application Service: User Service
Orquestra operações relacionadas a usuários
"""
from typing import Optional, List
import uuid
from src.domain.entities.user import User
from src.domain.ports.user_repository import UserRepositoryPort
from src.domain.ports.cache_repository import CacheRepositoryPort
import json


class UserService:
    """Serviço de aplicação para operações de usuário"""

    def __init__(
        self,
        user_repository: UserRepositoryPort,
        cache_repository: CacheRepositoryPort
    ):
        self.user_repository = user_repository
        self.cache_repository = cache_repository

    def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Busca um usuário por ID com cache"""
        cache_key = f"user:{user_id}"
        
        # Tenta buscar no cache
        cached = self.cache_repository.get(cache_key)
        if cached:
            return self._deserialize_user(cached)
        
        # Se não encontrou no cache, busca no banco
        user = self.user_repository.find_by_id(user_id)
        
        # Salva no cache se encontrou
        if user:
            self.cache_repository.set(cache_key, self._serialize_user(user), ttl=300)
        
        return user

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Busca um usuário por email"""
        return self.user_repository.find_by_email(email)

    def get_all_users(self) -> List[User]:
        """Retorna todos os usuários"""
        return self.user_repository.find_all()

    def create_user(self, username: str, email: str, password_hash: str, full_name: Optional[str] = None) -> User:
        """Cria um novo usuário"""
        user = User(
            id=uuid.uuid4(),
            username=username,
            email=email,
            password_hash=password_hash,
            full_name=full_name
        )
        return self.user_repository.save(user)

    def _serialize_user(self, user: User) -> str:
        """Serializa um usuário para cache"""
        return json.dumps({
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "password_hash": user.password_hash,
            "full_name": user.full_name,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        })

    def _deserialize_user(self, data: str) -> User:
        """Desserializa um usuário do cache"""
        from datetime import datetime
        user_dict = json.loads(data)
        return User(
            id=uuid.UUID(user_dict["id"]),
            username=user_dict["username"],
            email=user_dict["email"],
            password_hash=user_dict["password_hash"],
            full_name=user_dict.get("full_name"),
            created_at=datetime.fromisoformat(user_dict["created_at"]) if user_dict.get("created_at") else None,
            updated_at=datetime.fromisoformat(user_dict["updated_at"]) if user_dict.get("updated_at") else None
        )
