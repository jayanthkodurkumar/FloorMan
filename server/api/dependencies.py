from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client
from api.supabase_client import get_supabase

bearer_scheme = HTTPBearer()


def get_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> str:
    return credentials.credentials


def get_current_user(
    token: str = Depends(get_token),
    supabase: Client = Depends(get_supabase),
) -> dict:
    """
    Validates the Bearer JWT from the Authorization header using Supabase
    and returns the user payload.
    """
    try:
        response = supabase.auth.get_user(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )

    if not response.user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )

    user = response.user
    return {
        "id": str(user.id),
        "email": user.email,
        "role": user.user_metadata.get("role", "user"),
        "token": token,
    }
