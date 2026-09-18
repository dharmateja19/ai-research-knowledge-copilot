from app.database import SessionLocal
from app.conversation_service import (
    create_conversation,
    add_document_to_conversation,
    get_conversation_documents
)
from app.rag_service import answer_question


db = SessionLocal()

try:
    # Create a new conversation
    conversation = create_conversation(
        db,
        "Document Scoped Chat"
    )

    print("Conversation ID:", conversation.id)

    # Attach document 2
    document = add_document_to_conversation(
        db,
        conversation.id,
        2
    )

    print("Attached:", document.filename)

    # Get documents for this conversation
    documents = get_conversation_documents(
        db,
        conversation.id
    )

    document_ids = [
        doc.id
        for doc in documents
    ]

    print("Document IDs:", document_ids)

    # Ask question using ONLY conversation documents
    result = answer_question(
        db,
        "What is deep learning?",
        document_ids=document_ids
    )

    print("\nANSWER:")
    print(result["answer"])

    print("\nSOURCES:")

    for source in result["sources"]:
        print(
            f"[Source {source['source_id']}] "
            f"Document ID: {source['document']}"
            f" | Page: {source['page']}"
        )

finally:
    db.close()