from datetime import datetime, timedelta, timezone

from cryptography.fernet import Fernet
from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SecurityService:
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        return pwd_context.verify(password, hashed)

    @staticmethod
    def create_token(subject: str, minutes: int, token_type: str = "access") -> str:
        exp = datetime.now(timezone.utc) + timedelta(minutes=minutes)
        payload = {"sub": subject, "exp": exp, "type": token_type}
        return jwt.encode(payload, settings.secret_key, algorithm="HS256")

    @staticmethod
    def encrypt_value(value: str) -> str:
        return Fernet(settings.iban_encryption_key.encode()).encrypt(value.encode()).decode()

    @staticmethod
    def decrypt_value(value: str) -> str:
        return Fernet(settings.iban_encryption_key.encode()).decrypt(value.encode()).decode()
