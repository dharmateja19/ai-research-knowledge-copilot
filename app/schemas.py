from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str


class SourceResponse(BaseModel):
    source_id: int
    document: str
    page: int
    chunk_id: int
    rerank_score: float


class AskResponse(BaseModel):
    answer: str
    sources: list[SourceResponse]
    
class CreateConversationRequest(BaseModel):
    title: str = "New Conversation"


class ConversationResponse(BaseModel):
    id: int
    title: str


class ConversationAskRequest(BaseModel):
    question: str