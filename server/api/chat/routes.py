from fastapi import APIRouter, Depends
from api.chat.schemas import ChatRequest, ChatResponse, SessionResponse, SessionInfo, MessageItem
from api.chat.service import ask, create_session, get_sessions, get_messages
from api.supabase_client import get_authed_supabase
from api.dependencies import get_current_user

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.get("/sessions", response_model=list[SessionInfo])
def list_sessions(current_user: dict = Depends(get_current_user)):
    supabase = get_authed_supabase(current_user["token"])
    return get_sessions(supabase)


@router.get("/sessions/{session_id}/messages", response_model=list[MessageItem])
def list_messages(session_id: str, current_user: dict = Depends(get_current_user)):
    supabase = get_authed_supabase(current_user["token"])
    return get_messages(session_id, supabase)


@router.post("/session", response_model=SessionResponse, status_code=201)
def new_session(current_user: dict = Depends(get_current_user)):
    supabase = get_authed_supabase(current_user["token"])
    session_id = create_session(current_user["id"], supabase)
    return SessionResponse(session_id=session_id)


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    supabase = get_authed_supabase(current_user["token"])
    return ask(request.question, request.session_id, supabase, request.k)
