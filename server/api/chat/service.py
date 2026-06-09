from fastapi import HTTPException
from supabase import Client
from core.retriever import retrieve
from core.generator import generate
from api.chat.schemas import ChatResponse, Source, SessionInfo, MessageItem


def create_session(user_id: str, supabase: Client) -> str:
    """Create a new chat session for the user and return its ID."""
    response = supabase.table("chat_sessions").insert({"user_id": user_id}).execute()
    return response.data[0]["id"]


GREETING_PATTERNS = {
    "hi", "hello", "hey", "howdy", "hiya", "greetings",
    "good morning", "good afternoon", "good evening", "good day",
    "how are you", "how are you doing", "what's up", "whats up",
}


def is_substantive(text: str) -> bool:
    """Return True if the message is a real question, not a greeting."""
    normalized = text.strip().lower().rstrip("!?.")
    return normalized not in GREETING_PATTERNS and len(text.strip()) >= 15


def get_sessions(supabase: Client) -> list[SessionInfo]:
    response = (
        supabase.table("chat_sessions")
        .select("id, created_at, chat_messages(content, role, created_at)")
        .order("created_at", desc=True)
        .execute()
    )
    sessions = []
    for row in response.data:
        messages = row.get("chat_messages") or []
        user_messages = sorted(
            [m for m in messages if m["role"] == "user"],
            key=lambda m: m["created_at"],
        )
        # Skip greetings — find the first substantive message
        first = next(
            (m["content"] for m in user_messages if is_substantive(m["content"])),
            None,
        )
        sessions.append(
            SessionInfo(id=row["id"], created_at=row["created_at"], first_message=first)
        )
    return sessions


def get_messages(session_id: str, supabase: Client) -> list[MessageItem]:
    response = (
        supabase.table("chat_messages")
        .select("role, content, created_at")
        .eq("session_id", session_id)
        .order("created_at")
        .execute()
    )
    return [MessageItem(**row) for row in response.data]


def save_message(session_id: str, role: str, content: str, supabase: Client) -> None:
    supabase.table("chat_messages").insert(
        {"session_id": session_id, "role": role, "content": content}
    ).execute()


def ask(question: str, session_id: str, supabase: Client, k: int = 3) -> ChatResponse:
    if not question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    # Verify session exists
    session = (
        supabase.table("chat_sessions")
        .select("id")
        .eq("id", session_id)
        .maybe_single()
        .execute()
    )
    if not session.data:
        raise HTTPException(status_code=404, detail="Session not found.")

    # Load history BEFORE saving current message to avoid duplication
    history = (
        supabase.table("chat_messages")
        .select("role, content")
        .eq("session_id", session_id)
        .order("created_at")
        .limit(10)
        .execute()
        .data
    )

    # Save user message
    save_message(session_id, "user", question, supabase)

    # RAG pipeline
    chunks = retrieve(question, k=k)
    answer = generate(question, chunks, chat_history=history)

    # Save assistant reply
    save_message(session_id, "assistant", answer, supabase)

    sources = [Source(file=c["source"], page=c["page"], score=c["score"]) for c in chunks]
    return ChatResponse(answer=answer, sources=sources)
