import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

INDEX_NAME = "manufacturing-rag"
FETCH_K = 10  # always pull at least this many candidates before reranking

# Initialise once at module level so the model isn't reloaded on every call
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = PineconeVectorStore(index_name=INDEX_NAME, embedding=embeddings)


def rerank(question: str, chunks: list[dict], top_n: int) -> list[dict]:
    question_words = set(question.lower().split())

    overlap_scores = []
    for chunk in chunks:
        chunk_words = set(chunk["content"].lower().split())
        overlap = len(question_words & chunk_words)
        overlap_scores.append(overlap)

    ranked = []
    for _ in range(top_n):
        if not overlap_scores:
            break
        best_idx = 0
        for i in range(1, len(overlap_scores)):
            if overlap_scores[i] > overlap_scores[best_idx]:
                best_idx = i
        ranked.append(chunks[best_idx])
        overlap_scores.pop(best_idx)
        chunks.pop(best_idx)

    return ranked


def retrieve(question: str, k: int = 10) -> list[dict]:
    """
    Embed the question, search Pinecone for the top-k most similar chunks,
    and return each chunk with its content and source metadata.
    """
    fetch_k = max(k, FETCH_K)
    results = vectorstore.similarity_search_with_score(question, k=fetch_k)

    chunks = []
    for doc, score in results:
        chunks.append(
            {
                "content": doc.page_content,
                "score": round(score, 4),
                "source": doc.metadata.get("source", "unknown"),
                "page": doc.metadata.get("page", "N/A"),
            }
        )

    return rerank(question, chunks, top_n=k)


if __name__ == "__main__":
    question = "What are the PPE requirements for manufacturing workers?"
    results = retrieve(question, k=3)

    for i, chunk in enumerate(results, 1):
        print(f"\n--- Result {i} (score: {chunk['score']}) ---")
        print(f"Source : {chunk['source']}  |  Page: {chunk['page']}")
        print(chunk["content"])
