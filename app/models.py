from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Float,
    Table,
    Column,
    JSON
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

conversation_documents = Table(
    "conversation_documents",
    Base.metadata,

    Column(
        "conversation_id",
        ForeignKey("conversations.id"),
        primary_key=True
    ),

    Column(
        "document_id",
        ForeignKey("documents.id"),
        primary_key=True
    )
)

class Document(Base):
    __tablename__ = "documents"

    id : Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    filename : Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    file_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    upload_date: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    processing_status: Mapped[str] = mapped_column(
        String(50),
        default="uploaded",
        nullable=False
    )

    page_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    chunks: Mapped[list["DocumentChunk"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan"
    )
    
    conversations: Mapped[list["Conversation"]] = relationship(
        secondary=conversation_documents,
        back_populates="documents"
    )


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id"),
        nullable=False
    )

    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    page_number: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    source: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )  

    text: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    
    document: Mapped[Document] = relationship(
        back_populates="chunks"
    )  
    
    
class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan"
    )
    
    documents: Mapped[list["Document"]] = relationship(
        secondary=conversation_documents,
        back_populates="conversations"
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id"),
        nullable=False
    )

    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    sources: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    conversation: Mapped[Conversation] = relationship(
        back_populates="messages"
    )