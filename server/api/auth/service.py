from fastapi import HTTPException
from supabase import Client
from api.auth.schemas import SignUpRequest, SignInRequest, AuthResponse


def sign_up(request: SignUpRequest, supabase: Client) -> AuthResponse:
    try:
        response = supabase.auth.sign_up(
            {
                "email": request.email,
                "password": request.password,
                "options": {"data": {"role": request.role}},
            }
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    user = response.user
    session = response.session

    if not session:
        raise HTTPException(
            status_code=400,
            detail="Email confirmation required. Please verify your email before signing in.",
        )

    return AuthResponse(
        access_token=session.access_token,
        user_id=str(user.id),
        role=user.user_metadata.get("role", "user"),
    )


def sign_in(request: SignInRequest, supabase: Client) -> AuthResponse:
    try:
        response = supabase.auth.sign_in_with_password(
            {"email": request.email, "password": request.password}
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

    user = response.user
    session = response.session

    return AuthResponse(
        access_token=session.access_token,
        user_id=str(user.id),
        role=user.user_metadata.get("role", "user"),
    )
