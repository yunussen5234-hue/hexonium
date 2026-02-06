from fastapi import HTTPException


def api_error(code: str, message: str, details: dict | None = None, status_code: int = 400):
    raise HTTPException(status_code=status_code, detail={"code": code, "message": message, "details": details or {}})
