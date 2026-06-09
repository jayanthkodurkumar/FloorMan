import os
import glob
from dotenv import load_dotenv
from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

PINECONE_API_KEY = os.environ["PINECONE_API_KEY"]
INDEX_NAME = "manufacturing-rag"
DOCS_PATH = "docs"


def ingest_docs():
    # Load all PDFs from the docs folder
    pdf_files = glob.glob(f"{DOCS_PATH}/*.pdf")
    documents = []
    for pdf_file in pdf_files:
        reader = PdfReader(pdf_file)
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if text.strip():
                documents.append(
                    Document(
                        page_content=text,
                        metadata={"source": os.path.basename(pdf_file), "page": page_num + 1},
                    )
                )
    print(f"Loaded {len(documents)} pages from {len(pdf_files)} PDFs in '{DOCS_PATH}/'")

    # Split by paragraph boundaries first, then sentence, then word
    # Tuned for structured government/OSHA/NIST/EPA docs with numbered sections
    splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ". ", " ", ""],
        chunk_size=800,
        chunk_overlap=100,
        add_start_index=True,  # tracks char offset — useful for citing source location
    )
    chunks = splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks")

    # Embeddings (local, no API key needed)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Create Pinecone index if it doesn't exist
    pc = Pinecone(api_key=PINECONE_API_KEY)
    existing_indexes = [i.name for i in pc.list_indexes()]

    if INDEX_NAME not in existing_indexes:
        pc.create_index(
            name=INDEX_NAME,
            dimension=384,  # all-MiniLM-L6-v2 output dimension
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        print(f"Created Pinecone index '{INDEX_NAME}'")
    else:
        print(f"Using existing Pinecone index '{INDEX_NAME}'")

    # Upsert chunks into Pinecone
    PineconeVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings,
        index_name=INDEX_NAME,
    )
    print("Ingestion complete. All chunks stored in Pinecone.")


if __name__ == "__main__":
    ingest_docs()
