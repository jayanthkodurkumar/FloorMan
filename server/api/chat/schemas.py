from pydantic import BaseModel


class SessionResponse(BaseModel):
    session_id: str


class SessionInfo(BaseModel):
    id: str
    created_at: str
    first_message: str | None = None


class MessageItem(BaseModel):
    role: str
    content: str
    created_at: str


class ChatRequest(BaseModel):
    question: str
    session_id: str
    k: int = 3


class Source(BaseModel):
    file: str
    page: int | str
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]
