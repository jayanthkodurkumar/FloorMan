from fastapi import APIRouter, Depends
from supabase import Client
from api.auth.schemas import SignUpRequest, SignInRequest, AuthResponse
from api.auth.service import sign_up, sign_in
from api.supabase_client import get_supabase

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/signup", response_model=AuthResponse, status_code=201)
def signup(request: SignUpRequest, supabase: Client = Depends(get_supabase)):
    return sign_up(request, supabase)


@router.post("/signin", response_model=AuthResponse)
def signin(request: SignInRequest, supabase: Client = Depends(get_supabase)):
    return sign_in(request, supabase)
