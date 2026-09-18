from sqlalchemy.orm import Session

from app.models import Conversation, Message, Document


def create_conversation(
    db: Session,
    title: str = "New Conversation"
):
    conversation = Conversation(
        title=title
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


def add_message(
    db,
    conversation_id,
    role,
    content,
    sources=None
):
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        sources=sources
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


def get_conversation_messages(
    db: Session,
    conversation_id: int
):
    return (
        db.query(Message)
        .filter(
            Message.conversation_id == conversation_id
        )
        .order_by(Message.created_at)
        .all()
    )


def add_document_to_conversation(
    db: Session,
    conversation_id: int,
    document_id: int
):
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id
        )
        .first()
    )

    if not conversation:
        return None

    document = (
        db.query(Document)
        .filter(
            Document.id == document_id
        )
        .first()
    )

    if not document:
        return None

    if document not in conversation.documents:
        conversation.documents.append(document)

        db.commit()
        db.refresh(conversation)

    return document


def get_conversation_documents(
    db: Session,
    conversation_id: int
):
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id
        )
        .first()
    )

    if not conversation:
        return []

    return conversation.documents


def remove_document_from_conversation(
    db,
    conversation_id,
    document_id
):
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )

    if not conversation:
        return False

    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if not document:
        return False

    if document in conversation.documents:
        conversation.documents.remove(document)
        db.commit()

    return True