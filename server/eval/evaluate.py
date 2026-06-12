import json
import time
from dotenv import load_dotenv
from datasets import Dataset
from ragas import RunConfig, evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_recall,
    context_precision,
)
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper

from core.generator import generate
from core.retriever import retrieve


load_dotenv()


def main():
    evaluator_llm = LangchainLLMWrapper(
        ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0
        )
    )

    evaluator_embeddings = LangchainEmbeddingsWrapper(
        HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2")
    )

    with open("eval/rag_ground_truth.json") as f:
        entries = json.load(f)["ground_truth"]

    rows = {
        "user_input": [],
        "response": [],
        "retrieved_contexts": [],
        "reference": []
    }

    for i, entry in enumerate(entries, 1):
        question = entry["question"]
        expected_answer = entry["expected_answer"]

        print(f"[{i}/{len(entries)}] {question}")

        chunks = retrieve(question, k=3)
        answer = generate(question, chunks)

        rows["user_input"].append(question)
        rows["response"].append(answer)
        rows["retrieved_contexts"].append(
            [chunk["content"] for chunk in chunks])
        rows["reference"].append(expected_answer)

        time.sleep(5)

    dataset = Dataset.from_dict(rows)

    result = evaluate(
        dataset,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_recall,
            context_precision,
        ],
        llm=evaluator_llm,
        embeddings=evaluator_embeddings,
        run_config=RunConfig(
            max_workers=1,        # sequential, no parallel calls
            max_wait=120,         # wait up to 120s per call
            timeout=60,           # individual call timeout
        ),
        raise_exceptions=False,   # don't crash on individual failures, just score as NaN

    )

    print(result)

    result_df = result.to_pandas()
    result_df.to_json("eval/results.json", orient="records", indent=2)
    result_df.to_csv("eval/results.csv", index=False)


if __name__ == "__main__":
    main()
