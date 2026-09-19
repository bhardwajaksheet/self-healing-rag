import sys
import os
import json

# Add project root to Python path
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from langchain_chroma import Chroma
from rag.embeddings import get_embeddings


# -----------------------------------
# Load evaluation dataset
# -----------------------------------

with open(
    "evaluation/test_questions.json",
    "r",
    encoding="utf-8"
) as file:

    test_questions = json.load(file)


# -----------------------------------
# Connect to ChromaDB
# -----------------------------------

print("🧠 Connecting to vector database...")

embeddings = get_embeddings()

vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings
)


# -----------------------------------
# Collect retrieval scores
# -----------------------------------

all_scores = []


print("\n")
print("🚀 ANALYZING RETRIEVAL SCORES")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


for i, item in enumerate(test_questions, 1):

    question = item["question"]

    print("\n")
    print(f"Question {i}/{len(test_questions)}")
    print(f"❓ {question}")

    results = vectorstore.similarity_search_with_score(
        question,
        k=3
    )

    scores = [
        score
        for document, score in results
    ]

    all_scores.extend(scores)

    print("\n📊 Scores:")

    for j, score in enumerate(scores, 1):

        print(
            f"   Chunk {j}: {score:.4f}"
        )


# -----------------------------------
# Statistics
# -----------------------------------

print("\n")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("📊 RETRIEVAL SCORE SUMMARY")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

print(f"Total scores collected : {len(all_scores)}")

print(
    f"Minimum distance       : "
    f"{min(all_scores):.4f}"
)

print(
    f"Maximum distance       : "
    f"{max(all_scores):.4f}"
)

print(
    f"Average distance       : "
    f"{sum(all_scores) / len(all_scores):.4f}"
)

print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


# -----------------------------------
# Top-1 score summary
# -----------------------------------

top1_scores = []


for item in test_questions:

    question = item["question"]

    results = vectorstore.similarity_search_with_score(
        question,
        k=1
    )

    top1_scores.append(
        results[0][1]
    )


print("\n")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("🎯 TOP-1 RETRIEVAL SCORES")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


for i, score in enumerate(top1_scores, 1):

    print(
        f"Q{i}: {score:.4f}"
    )


print("\n")
print(
    f"Top-1 minimum : "
    f"{min(top1_scores):.4f}"
)

print(
    f"Top-1 maximum : "
    f"{max(top1_scores):.4f}"
)

print(
    f"Top-1 average : "
    f"{sum(top1_scores) / len(top1_scores):.4f}"
)

print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")