import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from sentence_transformers import CrossEncoder

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

INDEX_NAME = "manufacturing-rag"

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = PineconeVectorStore(index_name=INDEX_NAME, embedding=embeddings)
cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


def rerank(question: str, chunks: list[dict], n: int) -> list[dict]:
    pairs = []
    for chunk in chunks:
        pairs.append([question, chunk["content"]])

    scores = cross_encoder.predict(pairs)

    for i in range(len(chunks)):
        chunks[i]["score"] = round(float(scores[i]), 4)

    for i in range(len(chunks)):
        for j in range(i + 1, len(chunks)):
            if chunks[j]["score"] > chunks[i]["score"]:
                chunks[i], chunks[j] = chunks[j], chunks[i]

    return chunks[:n]


def retrieve(question: str, k: int = 10, n: int = 5) -> list[dict]:
    """
    Embed the question, search Pinecone for the top-k most similar chunks,
    rerank with a cross-encoder, and return the top n.
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

    return rerank(question, chunks, n)


if __name__ == "__main__":
    question = "What are the PPE requirements for manufacturing workers?"
    results = retrieve(question, k=10, n=5)

    for i, chunk in enumerate(results, 1):
        print(f"\n--- Result {i} (score: {chunk['score']}) ---")
        print(f"Source : {chunk['source']}  |  Page: {chunk['page']}")
        print(chunk["content"])
