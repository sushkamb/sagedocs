import jwt
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel

from app.config import settings

router = APIRouter(prefix="/api/admin", tags=["Admin Auth"])

TOKEN_EXPIRY_HOURS = 24


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    expires_in: int


def create_token(username: str) -> str:
    payload = {
        "sub": username,
        "exp": datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRY_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


async def verify_admin_token(authorization: str = Header(...)) -> str:
    """Dependency to protect admin endpoints. Returns the username."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = authorization[7:]
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/login", response_model=LoginResponse)
async def login(req: LoginRequest):
    if req.username != settings.admin_username or req.password != settings.admin_password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token(req.username)
    return LoginResponse(token=token, expires_in=TOKEN_EXPIRY_HOURS * 3600)


@router.get("/verify")
async def verify(user: str = Header(None, alias="authorization")):
    """Quick check if the current token is still valid."""
    if not user or not user.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = user[7:]
    try:
        jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        return {"valid": True}
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
