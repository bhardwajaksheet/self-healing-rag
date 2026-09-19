import sys
import os
import json
import re

# -----------------------------------
# Add project root to Python path
# -----------------------------------

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)


from langchain_chroma import Chroma

from rag.embeddings import get_embeddings
from rag.generator import generate_answer


# -----------------------------------
# Text normalization
# -----------------------------------

def normalize_text(text):
    """
    Normalize text so small formatting differences
    do not cause false evaluation failures.
    """

    text = text.lower()

    # -----------------------------------
    # Normalize common time formats
    #
    # 10:00 PM -> 10 PM
    # 06:00 AM -> 6 AM
    # -----------------------------------

    text = re.sub(
        r'\b0?(\d{1,2}):00\s*(am|pm)\b',
        r'\1 \2',
        text
    )

    # -----------------------------------
    # Normalize percentages
    #
    # 75 % -> 75%
    # -----------------------------------

    text = re.sub(
        r'(\d+)\s+%',
        r'\1%',
        text
    )

    # -----------------------------------
    # Normalize number words
    #
    # three books -> 3 books
    # fourteen days -> 14 days
    # -----------------------------------

    number_words = {
        "zero": "0",
        "one": "1",
        "two": "2",
        "three": "3",
        "four": "4",
        "five": "5",
        "six": "6",
        "seven": "7",
        "eight": "8",
        "nine": "9",
        "ten": "10",
        "eleven": "11",
        "twelve": "12",
        "thirteen": "13",
        "fourteen": "14",
        "fifteen": "15",
        "sixteen": "16",
        "seventeen": "17",
        "eighteen": "18",
        "nineteen": "19",
        "twenty": "20"
    }

    for word, number in number_words.items():

        text = re.sub(
            rf'\b{word}\b',
            number,
            text
        )

    # -----------------------------------
    # Normalize punctuation
    # -----------------------------------

    text = re.sub(
        r'[^\w\s%]',
        ' ',
        text
    )

    # -----------------------------------
    # Normalize whitespace
    # -----------------------------------

    text = re.sub(
        r'\s+',
        ' ',
        text
    ).strip()

    return text


# -----------------------------------
# Required fact matching
# -----------------------------------

def fact_match(answer, required_facts):
    """
    Evaluate whether all required fact groups
    are present in the answer.

    Each fact group contains acceptable variations.

    Example:

        ["3 books", "three books"]

    means either expression is acceptable.

    Every group must have at least one
    matching variation.
    """

    normalized_answer = normalize_text(answer)

    missing_facts = []

    for fact_group in required_facts:

        matched = False

        for fact in fact_group:

            normalized_fact = normalize_text(fact)

            if normalized_fact in normalized_answer:

                matched = True
                break

        if not matched:

            missing_facts.append(
                " / ".join(fact_group)
            )

    return (
        len(missing_facts) == 0,
        missing_facts
    )


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
# Evaluation
# -----------------------------------

results = []

retrieval_hits = 0
answer_matches = 0


print("\n🚀 Starting baseline RAG evaluation...\n")


for i, item in enumerate(
    test_questions,
    1
):

    question = item["question"]

    expected_answer = item["expected_answer"]

    required_facts = item["required_facts"]


    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    print(
        f"Question {i}/{len(test_questions)}"
    )

    print(
        f"❓ {question}"
    )


    # -----------------------------------
    # Retrieve documents
    # -----------------------------------

    documents = vectorstore.similarity_search(
        question,
        k=3
    )


    context = "\n\n".join(
        document.page_content
        for document in documents
    )


    # -----------------------------------
    # Evaluate retrieval
    # -----------------------------------

    retrieval_match, retrieval_missing = fact_match(
        context,
        required_facts
    )


    if retrieval_match:

        retrieval_hits += 1


    # -----------------------------------
    # Generate answer
    # -----------------------------------

    answer = generate_answer(
        question,
        context
    )


    # -----------------------------------
    # Evaluate answer
    # -----------------------------------

    answer_match, missing_facts = fact_match(
        answer,
        required_facts
    )


    if answer_match:

        answer_matches += 1


    # -----------------------------------
    # Store result
    # -----------------------------------

    result = {

        "question": question,

        "expected_answer": expected_answer,

        "required_facts": required_facts,

        "generated_answer": answer,

        "retrieval_hit": retrieval_match,

        "retrieval_missing_facts": retrieval_missing,

        "answer_match": answer_match,

        "answer_missing_facts": missing_facts
    }


    results.append(result)


    # -----------------------------------
    # Print retrieval result
    # -----------------------------------

    print(
        f"🔎 Retrieval: "
        f"{'PASS' if retrieval_match else 'FAIL'}"
    )


    if retrieval_missing:

        print(
            "   Missing retrieval facts: "
            f"{retrieval_missing}"
        )


    # -----------------------------------
    # Print generated answer
    # -----------------------------------

    print(
        f"🤖 Answer: {answer}"
    )


    # -----------------------------------
    # Print answer evaluation
    # -----------------------------------

    print(
        f"📌 Answer match: "
        f"{'PASS' if answer_match else 'FAIL'}"
    )


    if missing_facts:

        print(
            "   Missing answer facts: "
            f"{missing_facts}"
        )


# -----------------------------------
# Calculate metrics
# -----------------------------------

total = len(test_questions)


retrieval_rate = (
    retrieval_hits / total
) * 100


answer_rate = (
    answer_matches / total
) * 100


# -----------------------------------
# Print final metrics
# -----------------------------------

print("\n")

print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

print("📊 BASELINE RAG EVALUATION")

print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


print(
    f"Total questions      : {total}"
)


print(
    f"Retrieval hits       : "
    f"{retrieval_hits}"
)


print(
    f"Retrieval hit rate   : "
    f"{retrieval_rate:.2f}%"
)


print(
    f"Correct answers      : "
    f"{answer_matches}"
)


print(
    f"Answer match rate    : "
    f"{answer_rate:.2f}%"
)


print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


# -----------------------------------
# Save results
# -----------------------------------

with open(
    "evaluation/baseline_results.json",
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        results,
        file,
        indent=4,
        ensure_ascii=False
    )


print("\n💾 Results saved to:")

print(
    "evaluation/baseline_results.json"
)