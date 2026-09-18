from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from app.llm_service import generate_answer, stream_answer
from app.tools import search_knowledge_base


class AgentState(TypedDict):
    question: str
    route: str
    conversation_history: list
    document_ids: list
    retrieved_context: str
    answer: str
    sources: list
    evidence_sufficient: bool
    
def evidence_check_node(state: AgentState):

    if not state["retrieved_context"]:
        return {
            "evidence_sufficient": False
        }

    prompt = f"""
You are an evidence verification system.

Determine whether the retrieved document context contains
enough information to answer the user's question.

Return ONLY:

YES

or

NO

Rules:

- YES only if the context directly contains information that
  can answer the question.
- NO if the context is unrelated.
- NO if the context only contains vaguely related information.
- Do not use outside knowledge.
- Do not answer the question.

Retrieved Context:

{state["retrieved_context"]}

User Question:

{state["question"]}

Decision:
"""

    decision = generate_answer(prompt).strip().upper()

    return {
        "evidence_sufficient": decision.startswith("YES")
    }
    
def route_after_evidence_check(state: AgentState):

    if state["evidence_sufficient"]:
        return "rag_answer"

    return "insufficient_evidence"


def insufficient_evidence_node(state: AgentState):

    return {
        "answer": (
            "The provided documents do not contain enough "
            "information to answer this question."
        ),
        "sources": []
    }


def router_node(state: AgentState):
    question = state["question"].strip().lower()

    # Clear programming/coding requests should always be GENERAL
    programming_patterns = [
        "write a python",
        "write python",
        "write a program",
        "write code",
        "python program",
        "python code",
        "javascript code",
        "javascript program",
        "c++ code",
        "c++ program",
        "java code",
        "java program",
        "implement in python",
        "implement in javascript",
        "implement in c++",
        "implement in java",
        "debug this code",
        "fix this code",
        "code for",
        "program for",
    ]

    if any(pattern in question for pattern in programming_patterns):
        return {"route": "GENERAL"}

    history = state.get("conversation_history", [])

    history_text = ""

    if history:
        history_parts = []

        for message in history[-6:]:
            history_parts.append(
                f"{message.role}: {message.content}"
            )

        history_text = "\n".join(history_parts)

    prompt = f"""
You are a routing classifier for an AI research assistant.

Classify the CURRENT USER QUESTION into exactly one category:

RAG
GENERAL

====================
RAG
====================

Choose RAG ONLY when the user explicitly asks about:
- the uploaded document
- the PDF
- the lecture
- research material
- information contained in the uploaded documents
- a follow-up to information that clearly came from the uploaded documents

Examples:

"What does the PDF say about CNN?"
RAG

"According to the lecture, what is backpropagation?"
RAG

"Explain supervised learning from the uploaded document."
RAG

"What are the advantages mentioned in the document?"
RAG

"According to the previous explanation from the document, why is this important?"
RAG


====================
GENERAL
====================

Choose GENERAL for everything else.

This includes:
- programming questions
- Python questions
- JavaScript questions
- C++ questions
- coding problems
- DSA questions
- mathematics
- general AI/ML questions
- general computer science questions
- writing requests
- emails
- casual conversation
- general knowledge
- questions that do NOT explicitly require the uploaded documents

Examples:

"What is Python?"
GENERAL

"Explain machine learning."
GENERAL

"What is deep learning?"
GENERAL

"Write a Python program to reverse a string."
GENERAL

"Explain binary search."
GENERAL

"What is a linked list?"
GENERAL

"How does React work?"
GENERAL

"Write a professional email."
GENERAL

"What is 2 + 2?"
GENERAL


IMPORTANT RULE:

The existence of uploaded documents does NOT mean the question is RAG.

If the user does not explicitly refer to the PDF, document, lecture,
research material, or previously retrieved document information,
choose GENERAL.

Only choose RAG when there is clear evidence that the uploaded
documents are required.

Conversation History:
{history_text}

CURRENT USER QUESTION:
{state["question"]}

Return ONLY one word:

RAG

or

GENERAL

CLASSIFICATION:
"""

    route = generate_answer(prompt).strip().upper()

    if route.startswith("RAG"):
        return {"route": "RAG"}

    return {"route": "GENERAL"}


def knowledge_tool_node(state: AgentState):
    results = search_knowledge_base(
        state["question"],
        top_k=5,
        document_ids=state.get("document_ids", [])
    )

    if not results:
        return {
            "retrieved_context": "",
            "sources": []
        }

    context_parts = []

    sources = []

    for i, result in enumerate(results, start=1):

        context_parts.append(
            f"""
[Source {i}]
Document: {result["document"]}
Page: {result["page"]}

{result["text"]}
"""
        )

        sources.append({
            "source_id": i,
            "document": result["document"],
            "page": result["page"],
            "chunk_id": result["chunk_id"],
            "score": result["score"]
        })

    return {
        "retrieved_context": "\n".join(context_parts),
        "sources": sources
    }


def rag_answer_node(state: AgentState):

    if not state["retrieved_context"]:
        return {
            "answer": (
                "The provided documents do not contain enough "
                "information to answer this question."
            )
        }

    prompt = f"""
You are an AI research assistant.

Answer the user's question using ONLY the retrieved
knowledge below.

STRICT RULES:

1. Use only the provided context.
2. Every factual claim must have a citation.
3. Use exactly this citation format:

[Source N, Page X]

4. Never invent a source.
5. Never change source numbers or page numbers.
6. Only cite a source that actually supports the claim.
7. Do not use outside knowledge.
8. Keep the answer concise.
9. If the context does not contain enough information,
say:

"The provided documents do not contain enough information
to answer this question."

Retrieved Knowledge:

{state["retrieved_context"]}

User Question:

{state["question"]}

Answer:
"""

    answer = generate_answer(prompt)

    return {
        "answer": answer
    }


def general_node(state: AgentState):

    answer = generate_answer(
        state["question"]
    )

    return {
        "answer": answer,
        "sources": []
    }


def route_question(state: AgentState):

    if state["route"] == "RAG":
        return "knowledge_tool"

    return "general"


graph_builder = StateGraph(AgentState)

graph_builder.add_node(
    "router",
    router_node
)

graph_builder.add_node(
    "knowledge_tool",
    knowledge_tool_node
)

graph_builder.add_node(
    "rag_answer",
    rag_answer_node
)

graph_builder.add_node(
    "general",
    general_node
)


graph_builder.add_edge(
    START,
    "router"
)

graph_builder.add_conditional_edges(
    "router",
    route_question,
    {
        "knowledge_tool": "knowledge_tool",
        "general": "general"
    }
)

graph_builder.add_edge(
    "knowledge_tool",
    "evidence_check"
)

graph_builder.add_conditional_edges(
    "evidence_check",
    route_after_evidence_check,
    {
        "rag_answer": "rag_answer",
        "insufficient_evidence": "insufficient_evidence"
    }
)

graph_builder.add_edge(
    "rag_answer",
    END
)

graph_builder.add_edge(
    "insufficient_evidence",
    END
)

graph_builder.add_edge(
    "general",
    END
)

graph_builder.add_node(
    "evidence_check",
    evidence_check_node
)

graph_builder.add_node(
    "insufficient_evidence",
    insufficient_evidence_node
)


research_graph = graph_builder.compile()

def classify_question(
    question: str,
    conversation_history: list = None
):
    state = {
        "question": question,
        "conversation_history": conversation_history or [],
        "document_ids": [],
        "route": "",
        "retrieved_context": "",
        "answer": "",
        "sources": []
    }

    result = research_graph.invoke(state)

    return result["route"]


def route_question_for_chat(
    question: str,
    conversation_history: list = None
):
    state = {
        "question": question,
        "conversation_history": conversation_history or [],
        "document_ids": [],
        "route": "",
        "retrieved_context": "",
        "answer": "",
        "sources": []
    }

    result = router_node(state)

    return result["route"]


def run_research_agent(
    question: str,
    conversation_history: list = None,
    document_ids: list = None
):
    state = {
        "question": question,
        "conversation_history": conversation_history or [],
        "document_ids": document_ids or [],
        "route": "",
        "retrieved_context": "",
        "answer": "",
        "sources": []
    }

    result = research_graph.invoke(state)

    return {
        "route": result.get("route"),
        "answer": result.get("answer", ""),
        "sources": result.get("sources", [])
    }