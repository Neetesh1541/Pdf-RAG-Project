from typing import TypedDict, List

from langgraph.graph import StateGraph, END

from chat.models import Conversation, Message
from .generator import generate_grounded_answer
from .retriever import retrieve_chunks


class RAGState(TypedDict, total=False):
    conversation_id: str
    question: str
    document_ids: list[str]
    history: list[dict]
    chunks: list[object]
    answer: str
    citations: list[dict]
    confidence: str
    grounded: bool


def load_history_node(state: RAGState):
    conversation = Conversation.objects.filter(id=state['conversation_id']).first()
    history = []
    if conversation:
        messages = conversation.messages.order_by('-created_at')[:10]
        history = [
            {'role': message.role, 'content': message.content}
            for message in reversed(messages)
        ]
    return {'history': history}


def retrieve_node(state: RAGState):
    chunks = retrieve_chunks(
        state['question'],
        document_ids=state.get('document_ids'),
    )
    return {'chunks': chunks}


def generate_node(state: RAGState):
    result = generate_grounded_answer(
        state['question'],
        state.get('history', []),
        state.get('chunks', []),
    )
    return {
        'answer': result['answer'],
        'citations': result['citations'],
        'confidence': result['confidence'],
        'grounded': result['grounded'],
    }


def build_rag_graph():
    graph = StateGraph(RAGState)
    graph.add_node('load_history', load_history_node)
    graph.add_node('retrieve', retrieve_node)
    graph.add_node('generate', generate_node)

    graph.set_entry_point('load_history')
    graph.add_edge('load_history', 'retrieve')
    graph.add_edge('retrieve', 'generate')
    graph.add_edge('generate', END)
    return graph.compile()


RAG_GRAPH = build_rag_graph()


def run_rag_workflow(conversation_id: str, question: str, document_ids: list[str] | None = None):
    return RAG_GRAPH.invoke({
        'conversation_id': str(conversation_id),
        'question': question,
        'document_ids': document_ids or [],
    })
