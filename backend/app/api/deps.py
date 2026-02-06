from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.entities import Role, User
from app.utils.errors import api_error

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        email = payload.get("sub")
    except JWTError:
        api_error("UNAUTHORIZED", "Geçersiz oturum", status_code=401)
    user = db.query(User).filter(User.email == email).first()
    if not user:
        api_error("UNAUTHORIZED", "Kullanıcı bulunamadı", status_code=401)
    return user


def require_roles(*roles: Role):
    def checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            api_error("FORBIDDEN", "Bu işlem için yetkiniz yok", status_code=403)
        return current_user

    return checker
