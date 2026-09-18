from pathlib import Path
import shutil

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException,
    Depends,
    WebSocket,
    WebSocketDisconnect
)

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db, SessionLocal
from app import models
from app.document_service import extract_pdf_text, chunk_pages

from app.conversation_service import (
    create_conversation,
    add_message,
    get_conversation_messages,
    get_conversation_documents,
    add_document_to_conversation,
    remove_document_from_conversation
)

from app.schemas import (
    AskRequest,
    AskResponse,
    CreateConversationRequest,
    ConversationResponse,
    ConversationAskRequest,
    AskResponse
)

import hashlib
import json

from app.redis_service import (
    get_cache,
    set_cache,
    build_chat_cache_key
)

from app.llm_service import stream_answer
from app.rag_service import answer_question, stream_rag_answer
from app.agent import route_question_for_chat
from app.models import Conversation, Document
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Research & Knowledge Copilot",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@app.get("/")
def hello():
    return "Hello"


@app.get("/health")
def health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected"
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }


@app.post("/documents/upload")
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    file_path = UPLOAD_DIR / file.filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        pages = extract_pdf_text(str(file_path))
        chunks = chunk_pages(pages)

        file_size = file_path.stat().st_size

        document = models.Document(
            filename=file.filename,
            file_type=file.content_type,
            file_size=file_size,
            processing_status="processed",
            page_count=len(pages)
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        for chunk in chunks:
            document_chunk = models.DocumentChunk(
                document_id=document.id,
                chunk_index=chunk["chunk_index"],
                page_number=chunk["page_number"],
                source=file.filename,
                text=chunk["text"]
            )

            db.add(document_chunk)

        db.commit()

        return {
            "id": document.id,
            "filename": document.filename,
            "status": document.processing_status,
            "pages": document.page_count,
            "chunks": len(chunks),
            "file_size": document.file_size
        }

    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Document processing failed: {str(e)}"
        )
        
        
@app.post("/ask", response_model=AskResponse)
def ask_question(
    request: AskRequest,
    db: Session = Depends(get_db)
):
    normalized_question = request.question.strip().lower()

    cache_key = (
        "rag:"
        + hashlib.sha256(
            normalized_question.encode("utf-8")
        ).hexdigest()
    )

    # Check Redis
    cached_result = get_cache(cache_key)

    if cached_result:
        print("Redis cache HIT")

        return json.loads(cached_result)

    print("Redis cache MISS")

    # Run RAG
    result = answer_question(
        db,
        request.question
    )

    # Store result in Redis
    set_cache(
        cache_key,
        json.dumps(result),
        expire=3600
    )

    return result
    
    
@app.post(
    "/conversations",
    response_model=ConversationResponse
)
def create_new_conversation(
    request: CreateConversationRequest,
    db: Session = Depends(get_db)
):
    conversation = create_conversation(
        db,
        request.title
    )

    return {
        "id": conversation.id,
        "title": conversation.title
    }
    

@app.post(
    "/conversations/{conversation_id}/ask",
    response_model=AskResponse
)
def ask_in_conversation(
    conversation_id: int,
    request: ConversationAskRequest,
    db: Session = Depends(get_db)
):
    history = get_conversation_messages(
        db,
        conversation_id
    )

    documents = get_conversation_documents(
        db,
        conversation_id
    )

    document_ids = [
        document.id
        for document in documents
    ]

    add_message(
        db,
        conversation_id,
        "user",
        request.question
    )

    result = answer_question(
        db,
        request.question,
        conversation_history=history,
        document_ids=document_ids,
    )

    add_message(
        db,
        conversation_id,
        "assistant",
        result["answer"],
        result["sources"]
    )

    return result


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_json()

            conversation_id = data["conversation_id"]
            question = data["question"]

            db = SessionLocal()

            try:
                # Get conversation history
                history = get_conversation_messages(
                    db,
                    conversation_id
                )

                # Get attached documents
                documents = get_conversation_documents(
                    db,
                    conversation_id
                )

                document_ids = [
                    document.id
                    for document in documents
                ]

               # Save user message
                add_message(
                    db,
                    conversation_id,
                    "user",
                    question
                )

                # Decide route FIRST
                route = route_question_for_chat(
                    question,
                    history
                )

                print("WEBSOCKET ROUTE:", route)


                # Create route-aware cache key
                cache_key = build_chat_cache_key(
                    conversation_id,
                    question,
                    document_ids,
                    route
                )

                # Check Redis
                cached_result = get_cache(cache_key)

                if cached_result:
                    print("WebSocket Redis cache HIT")

                    cached_data = json.loads(cached_result)

                    await websocket.send_json({
                        "type": "route",
                        "route": cached_data["route"]
                    })

                    await websocket.send_json({
                        "type": "sources",
                        "sources": cached_data["sources"]
                    })

                    await websocket.send_json({
                        "type": "token",
                        "content": cached_data["answer"]
                    })

                    add_message(
                        db,
                        conversation_id,
                        "assistant",
                        cached_data["answer"],
                        cached_data["sources"]
                    )

                    await websocket.send_json({
                        "type": "done"
                    })

                    continue


                print("WebSocket Redis cache MISS")


                # RAG or GENERAL
                if route == "RAG":

                    result = stream_rag_answer(
                        db,
                        question,
                        conversation_history=history,
                        document_ids=document_ids
                    )

                else:

                    result = {
                        "sources": [],
                        "stream": stream_answer(question)
                    }


                # Send route
                await websocket.send_json({
                    "type": "route",
                    "route": route
                })


                # Send sources
                await websocket.send_json({
                    "type": "sources",
                    "sources": result["sources"]
                })


                full_answer = ""


                if result["stream"] is None:

                    full_answer = (
                        "The provided documents do not contain "
                        "enough information to answer this question."
                    )

                    await websocket.send_json({
                        "type": "token",
                        "content": full_answer
                    })

                else:

                    for chunk in result["stream"]:

                        full_answer += chunk

                        await websocket.send_json({
                            "type": "token",
                            "content": chunk
                        })
                # Save assistant response
                add_message(
                    db,
                    conversation_id,
                    "assistant",
                    full_answer,
                    result["sources"]
                )

                # Store complete result in Redis
                cache_data = {
                    "route": route,
                    "answer": full_answer,
                    "sources": result["sources"]
                }

                set_cache(
                    cache_key,
                    json.dumps(cache_data),
                    expire=3600
                )

                print("WebSocket result cached")

                await websocket.send_json({
                    "type": "done"
                })

            finally:
                db.close()

    except WebSocketDisconnect:
        print("WebSocket client disconnected")


        
@app.get("/conversations")
def get_conversations(db: Session = Depends(get_db)):
    conversations = (
        db.query(Conversation)
        .order_by(Conversation.created_at.desc())
        .all()
    )

    return [
        {
            "id": conversation.id,
            "title": conversation.title,
            "created_at": conversation.created_at,
        }
        for conversation in conversations
    ]
    
@app.get("/conversations/{conversation_id}/messages")
def get_messages(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    messages = get_conversation_messages(
        db,
        conversation_id
    )

    return [
        {
            "id": message.id,
            "role": message.role,
            "content": message.content,
            "created_at": message.created_at,
            "sources": message.sources
        }
        for message in messages
    ]
    
    
@app.get("/documents")
def get_documents(db: Session = Depends(get_db)):
    documents = db.query(Document).all()

    return [
        {
            "id": document.id,
            "filename": document.filename
        }
        for document in documents
    ]
    
@app.delete("/documents/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    # Delete vectors from Qdrant
    from app.qdrant_service import client, COLLECTION_NAME
    from qdrant_client.models import Filter, FieldCondition, MatchValue

    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(value=document_id)
                )
            ]
        )
    )

    # Delete document and its chunks from PostgreSQL
    db.delete(document)
    db.commit()

    return {
        "message": "Document deleted successfully",
        "document_id": document_id
    }
    
@app.get("/conversations/{conversation_id}/documents")
def get_documents_for_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    documents = get_conversation_documents(
        db,
        conversation_id
    )

    return [
        {
            "id": document.id,
            "filename": document.filename
        }
        for document in documents
    ]
    
@app.post("/conversations/{conversation_id}/documents/{document_id}")
def attach_document(
    conversation_id: int,
    document_id: int,
    db: Session = Depends(get_db)
):
    document = add_document_to_conversation(
        db,
        conversation_id,
        document_id
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Conversation or document not found"
        )

    return {
        "message": "Document attached successfully",
        "document": {
            "id": document.id,
            "filename": document.filename
        }
    }
    
@app.delete("/conversations/{conversation_id}/documents/{document_id}")
def detach_document(
    conversation_id: int,
    document_id: int,
    db: Session = Depends(get_db)
):
    success = remove_document_from_conversation(
        db,
        conversation_id,
        document_id
    )

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Conversation or document not found"
        )

    return {
        "message": "Document detached successfully"
    }