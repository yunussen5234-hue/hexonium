from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.utils.errors import api_error
from app.utils.security import SecurityService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not SecurityService.verify_password(payload.password, user.hashed_password):
        api_error("INVALID_CREDENTIALS", "E-posta veya şifre hatalı", status_code=401)
    return TokenResponse(
        access_token=SecurityService.create_token(user.email, 60),
        refresh_token=SecurityService.create_token(user.email, 60 * 24 * 7, token_type="refresh"),
    )
