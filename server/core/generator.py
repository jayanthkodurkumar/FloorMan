import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

GROQ_API_KEY = os.environ["GROQ_API_KEY"]
MODEL_NAME = os.environ["MODEL_NAME"]

SYSTEM_PROMPT = """You are a knowledgeable assistant for manufacturing industry workers.
You answer questions about standard operating procedures, workplace safety, \
equipment maintenance, quality control, and regulatory compliance.

Rules:
- If the user sends a greeting or casual message (e.g. "hi", "hello", "how are you"), respond naturally and politely without citing sources.
- For all other questions, answer only from the provided context. Do not use outside knowledge.
- Be clear and concise. Workers need practical answers, not lengthy explanations.
- Always cite your sources at the end of your answer in this format:
    [Source: <filename>, Page <page>]
- If the context does not contain enough information to answer, say:
    "I don't have enough information in the provided documents to answer this question."
- Never guess or fabricate information. Safety and compliance depend on accuracy.
"""

llm = ChatGroq(model=MODEL_NAME, api_key=GROQ_API_KEY, temperature=0)


def build_context_block(chunks: list[dict]) -> str:
    """Format retrieved chunks into a numbered context block for the prompt."""
    lines = []
    for i, chunk in enumerate(chunks, 1):
        lines.append(
            f"[{i}] (Source: {chunk['source']}, Page {chunk['page']})\n{chunk['content']}"
        )
    return "\n\n".join(lines)


def generate(
    question: str,
    chunks: list[dict],
    chat_history: list[dict] | None = None,
) -> str:
    """
    Build a prompt from the question, retrieved chunks, and prior chat history,
    send to Groq, and return the cited answer.
    """
    context = build_context_block(chunks)

    messages: list = [SystemMessage(content=SYSTEM_PROMPT)]

    # Inject prior turns so the LLM remembers the conversation
    for msg in (chat_history or []):
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))

    # Append current question with RAG context
    messages.append(
        HumanMessage(
            content=f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer based only on the context above and cite your sources."
        )
    )

    response = llm.invoke(messages)
    return response.content


if __name__ == "__main__":
    # Quick smoke test with dummy data
    dummy_chunks = [
        {
            "content": "All workers must wear hard hats, safety goggles, and steel-toed boots in production areas.",
            "source": "osha_manufacturing.pdf",
            "page": 12,
            "score": 0.91,
        }
    ]
    question = "What PPE is required on the production floor?"
    print(generate(question, dummy_chunks))
