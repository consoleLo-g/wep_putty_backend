from fastapi import APIRouter, HTTPException, Header
from schemas.auth import LoginRequest, LoginResponse
from core.security import (
    verify_access_password,
    create_access_token,
    verify_token,
)

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest):
    if not verify_access_password(payload.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid password"
        )

    token = create_access_token()

    return LoginResponse(
        access_token=token
    )


@router.get("/verify")
def verify(
    authorization: str = Header(None)
):
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Missing token"
        )

    try:
        scheme, token = authorization.split(" ")
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token format"
        )

    if scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Invalid auth scheme"
        )

    if not verify_token(token):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    return {
        "valid": True
    }