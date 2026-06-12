import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

INDEX_NAME = "manufacturing-rag"

# Initialise once at module level so the model isn't reloaded on every call
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = PineconeVectorStore(index_name=INDEX_NAME, embedding=embeddings)


def retrieve(question: str, k: int = 5) -> list[dict]:
    """
    Embed the question, search Pinecone for the top-k most similar chunks,
    and return each chunk with its content and source metadata.
    """
    results = vectorstore.similarity_search_with_score(question, k=k)

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

    return chunks


if __name__ == "__main__":
    question = "What are the PPE requirements for manufacturing workers?"
    results = retrieve(question, k=3)

    for i, chunk in enumerate(results, 1):
        print(f"\n--- Result {i} (score: {chunk['score']}) ---")
        print(f"Source : {chunk['source']}  |  Page: {chunk['page']}")
        print(chunk["content"])
