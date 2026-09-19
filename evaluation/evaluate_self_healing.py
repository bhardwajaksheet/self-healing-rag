import sys
import os
import json
import re
import time
import hashlib

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

from groq import Groq
from dotenv import load_dotenv


load_dotenv()


# -----------------------------------
# Configuration
# -----------------------------------

EVAL_MODEL = "openai/gpt-oss-20b"

RESULTS_PATH = "evaluation/self_healing_results.json"

CACHE_PATH = "evaluation/embedding_cache.json"

MAX_EMBEDDING_RETRIES = 3

EMBEDDING_RETRY_DELAY = 8


# -----------------------------------
# Groq client
# -----------------------------------

groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# -----------------------------------
# Text normalization
# -----------------------------------

def normalize_text(text):

    text = text.lower()

    # -----------------------------------
    # Normalize time formats
    # -----------------------------------

    text = re.sub(
        r'\b0?(\d{1,2}):00\s*(am|pm)\b',
        r'\1 \2',
        text
    )

    # -----------------------------------
    # Normalize percentages
    # -----------------------------------

    text = re.sub(
        r'(\d+)\s+%',
        r'\1%',
        text
    )

    # -----------------------------------
    # Normalize number words
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
    # Normalize common answer phrases
    # -----------------------------------

    text = text.replace(
        "may not use",
        "not permitted"
    )

    text = text.replace(
        "cannot use",
        "not permitted"
    )

    text = text.replace(
        "cannot be used",
        "not permitted"
    )

    text = text.replace(
        "may not be used",
        "not permitted"
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

    normalized_answer = normalize_text(answer)

    missing_facts = []

    for fact_group in required_facts:

        matched = False

        for fact in fact_group:

            normalized_fact = normalize_text(
                fact
            )

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
# Groq helper
# -----------------------------------

def groq_generate(prompt):

    response = groq_client.chat.completions.create(
        model=EVAL_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content.strip()


# -----------------------------------
# Evaluation answer generation
# -----------------------------------

def generate_eval_answer(question, context):

    prompt = f"""
You are a grounded question-answering system.

Answer the user's question using ONLY the
information contained in the provided context.

The answer must directly address the question.

If the context does not contain enough
information, say exactly:

I don't have enough information in the provided documents to answer this reliably.

Do not use outside knowledge.
Do not invent facts.
Do not answer a different question.

CONTEXT:
{context}

USER QUESTION:
{question}

ANSWER:
"""

    return groq_generate(prompt)


# -----------------------------------
# Critic
# -----------------------------------

def evaluate_critic(question, context, answer):

    prompt = f"""
You are a strict fact-checking critic for a
Self-Healing RAG system.

Evaluate whether the generated answer is both:

1. Relevant to the user's question.
2. Fully supported by the supplied context.

QUESTION:
{question}

CONTEXT:
{context}

GENERATED ANSWER:
{answer}

Return exactly:

VERDICT: PASS
REASON: <short explanation>

OR

VERDICT: FAIL
REASON: <short explanation>

Rules:

1. PASS only if the answer directly answers
   the user's question.

2. PASS only if the answer is supported by
   information in the context.

3. FAIL if the answer answers a different
   question, even if the information is true.

4. FAIL if required information is missing.

5. FAIL if the answer contains unsupported facts.

6. FAIL if the answer contradicts the context.

7. FAIL if the answer invents information.

8. If the answer says it does not have enough
   information, return FAIL.

9. Do not use outside knowledge.

Judge the answer against the actual question,
not merely against whether some related fact
appears in the context.
"""

    return groq_generate(prompt)


# -----------------------------------
# Query reformulation
# -----------------------------------

def reformulate_query(
    original_question,
    critique
):

    prompt = f"""
You are a query reformulation agent for a
Self-Healing RAG system.

The original user question is:

{original_question}

The previous RAG attempt failed because
the critic rejected the result.

Critic feedback:

{critique}

Rewrite the original question so that it becomes:

1. Clearer
2. More specific
3. Better suited for document retrieval
4. Faithful to the original meaning

IMPORTANT RULES:

- Do NOT introduce new subjects.
- Do NOT introduce countries.
- Do NOT introduce universities.
- Do NOT introduce curricula.
- Do NOT introduce organizations.
- Do NOT introduce people.
- Do NOT introduce assumptions.
- Do NOT invent information.
- Do NOT change the meaning.
- Only improve the wording for retrieval.

Return ONLY the rewritten question.
"""

    return groq_generate(prompt)


# -----------------------------------
# Weak queries
# -----------------------------------

weak_queries = [

    "campus transportation facilities",

    "student sports activities",

    "faculty office timings",

    "college canteen menu",

    "campus parking facilities",

    "student clubs and events",

    "career placement opportunities",

    "college transportation rules",

    "campus bus schedule",

    "student athletic facilities",

    "faculty meeting schedule",

    "food court services",

    "vehicle parking permits",

    "student cultural programs",

    "job placement companies",

    "campus travel services",

    "campus maintenance services",

    "sports competition schedule",

    "faculty department meetings",

    "cafeteria operating hours",

    "visitor parking areas",

    "student organization activities",

    "internship opportunities",

    "public transportation access"
]


# -----------------------------------
# Load dataset
# -----------------------------------

with open(
    "evaluation/test_questions.json",
    "r",
    encoding="utf-8"
) as file:

    test_questions = json.load(file)


# -----------------------------------
# Safety check
# -----------------------------------

if len(weak_queries) != len(test_questions):

    raise ValueError(
        f"Number of weak queries ({len(weak_queries)}) "
        f"does not match number of test questions "
        f"({len(test_questions)})."
    )


# -----------------------------------
# Benchmark identity
# -----------------------------------

benchmark_text = json.dumps(
    {
        "questions": test_questions,
        "weak_queries": weak_queries,
        "model": EVAL_MODEL
    },
    sort_keys=True
)

BENCHMARK_ID = hashlib.sha256(
    benchmark_text.encode("utf-8")
).hexdigest()[:16]


# -----------------------------------
# Result helpers
# -----------------------------------

def save_results(results):

    output = {
        "benchmark_id": BENCHMARK_ID,
        "evaluation_model": EVAL_MODEL,
        "results": results
    }

    with open(
        RESULTS_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            indent=4,
            ensure_ascii=False
        )


def load_previous_results():

    if not os.path.exists(RESULTS_PATH):

        return []


    try:

        with open(
            RESULTS_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)


        # New result-file format
        if isinstance(data, dict):

            if data.get("benchmark_id") != BENCHMARK_ID:

                print(
                    "\n⚠️ Existing results belong "
                    "to a different benchmark."
                )

                print(
                    "Starting a fresh evaluation."
                )

                return []

            return data.get("results", [])


        # Old result-file format
        print(
            "\n⚠️ Existing results use an older "
            "format."
        )

        print(
            "Starting a fresh evaluation."
        )

        return []


    except Exception:

        print(
            "\n⚠️ Could not read previous results."
        )

        print(
            "Starting a fresh evaluation."
        )

        return []


# -----------------------------------
# Embedding cache
# -----------------------------------

def load_embedding_cache():

    if not os.path.exists(CACHE_PATH):

        return {}


    try:

        with open(
            CACHE_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception:

        return {}


def save_embedding_cache(cache):

    with open(
        CACHE_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            cache,
            file,
            indent=2
        )


# -----------------------------------
# Embedding retry
# -----------------------------------

def retrieve_with_retry(
    vectorstore,
    query,
    k=3
):

    last_error = None

    for attempt in range(
        1,
        MAX_EMBEDDING_RETRIES + 1
    ):

        try:

            return (
                vectorstore.similarity_search_with_score(
                    query,
                    k=k
                )
            )

        except Exception as error:

            last_error = error

            print(
                f"\n⚠️ Embedding/retrieval error "
                f"(attempt {attempt}/"
                f"{MAX_EMBEDDING_RETRIES})"
            )

            print(
                f"   {error}"
            )

            if attempt < MAX_EMBEDDING_RETRIES:

                print(
                    f"⏳ Waiting "
                    f"{EMBEDDING_RETRY_DELAY} seconds..."
                )

                time.sleep(
                    EMBEDDING_RETRY_DELAY
                )

            else:

                raise last_error


# -----------------------------------
# Connect to ChromaDB
# -----------------------------------

print(
    "🧠 Connecting to vector database..."
)

embeddings = get_embeddings()

vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings
)


# -----------------------------------
# Load previous results
# -----------------------------------

previous_results = load_previous_results()

completed_questions = {
    result["question"]
    for result in previous_results
}


if previous_results:

    print(
        f"\n♻️ Found "
        f"{len(previous_results)} completed "
        f"questions from the current benchmark."
    )

    print(
        "The evaluator will resume from the "
        "first incomplete question."
    )


# -----------------------------------
# Evaluation state
# -----------------------------------

results = list(previous_results)


print(
    "\n🚀 STARTING SELF-HEALING "
    "RETRIEVAL ANALYSIS\n"
)

print(
    f"🧠 Evaluation model: {EVAL_MODEL}"
)

print(
    f"🆔 Benchmark ID: {BENCHMARK_ID}"
)

print(
    "💡 Production RAG generator remains unchanged."
)


# -----------------------------------
# Process questions
# -----------------------------------

try:

    for i, item in enumerate(
        test_questions,
        1
    ):

        original_question = item["question"]

        expected_answer = item["expected_answer"]

        required_facts = item["required_facts"]

        weak_query = weak_queries[i - 1]


        # -----------------------------------
        # Resume support
        # -----------------------------------

        if original_question in completed_questions:

            print(
                f"\n⏭️ Question {i}/"
                f"{len(test_questions)} "
                f"already completed."
            )

            continue


        print(
            "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )

        print(
            f"Question {i}/"
            f"{len(test_questions)}"
        )

        print(
            f"❓ {original_question}"
        )


        # -----------------------------------
        # ATTEMPT 1
        # -----------------------------------

        print(
            "\n🔎 ATTEMPT 1: "
            "Controlled weak retrieval"
        )

        print(
            f"⚠️ Weak query: {weak_query}"
        )


        initial_results = retrieve_with_retry(
            vectorstore,
            weak_query,
            k=3
        )


        initial_context = "\n\n".join(
            result.page_content
            for result, score in initial_results
        )


        initial_scores = [
            score
            for result, score in initial_results
        ]


        initial_top_score = initial_scores[0]


        print(
            f"📊 Initial top-1 distance: "
            f"{initial_top_score:.4f}"
        )


        # -----------------------------------
        # Initial answer
        # -----------------------------------

        initial_answer = generate_eval_answer(
            original_question,
            initial_context
        )


        print(
            "\n🤖 Initial answer:"
        )

        print(
            initial_answer
        )


        # -----------------------------------
        # Initial critic
        # -----------------------------------

        initial_critique = evaluate_critic(
            original_question,
            initial_context,
            initial_answer
        )


        print(
            "\n🧐 Initial critic:"
        )

        print(
            initial_critique
        )


        # -----------------------------------
        # Check initial result
        # -----------------------------------

        if "VERDICT: PASS" in initial_critique.upper():

            print(
                "\n⚠️ CONTROLLED FAILURE "
                "DID NOT TRIGGER"
            )


            answer_match, missing_facts = fact_match(
                initial_answer,
                required_facts
            )


            results.append({

                "question": original_question,

                "expected_answer": expected_answer,

                "required_facts": required_facts,

                "weak_query": weak_query,

                "healing_triggered": False,

                "initial_distance": initial_top_score,

                "initial_answer": initial_answer,

                "initial_critique": initial_critique,

                "initial_answer_match": answer_match,

                "initial_missing_facts": missing_facts,

                "healed": False,

                "recovered": False

            })


            completed_questions.add(
                original_question
            )

            save_results(results)

            continue


        # -----------------------------------
        # Healing triggered
        # -----------------------------------

        print(
            "\n❌ INITIAL RETRIEVAL FAILED"
        )

        print(
            "🔄 ACTIVATING SELF-HEALING..."
        )


        # -----------------------------------
        # Reformulate
        # -----------------------------------

        new_query = reformulate_query(
            original_question,
            initial_critique
        )


        print(
            "\n🔄 Reformulated query:"
        )

        print(
            new_query
        )


        # -----------------------------------
        # ATTEMPT 2
        # -----------------------------------

        healed_results = retrieve_with_retry(
            vectorstore,
            new_query,
            k=3
        )


        healed_context = "\n\n".join(
            result.page_content
            for result, score in healed_results
        )


        healed_scores = [
            score
            for result, score in healed_results
        ]


        healed_top_score = healed_scores[0]


        print(
            f"\n📊 Healed top-1 distance: "
            f"{healed_top_score:.4f}"
        )


        # -----------------------------------
        # Distance comparison
        # -----------------------------------

        distance_change = (
            initial_top_score -
            healed_top_score
        )


        retrieval_improved = (
            healed_top_score <
            initial_top_score
        )


        if retrieval_improved:

            print(
                f"📈 Retrieval improved by "
                f"{distance_change:.4f}"
            )

        else:

            print(
                "📉 Retrieval distance did "
                "not improve."
            )


        # -----------------------------------
        # Healed answer
        # -----------------------------------

        healed_answer = generate_eval_answer(
            original_question,
            healed_context
        )


        print(
            "\n🤖 Healed answer:"
        )

        print(
            healed_answer
        )


        # -----------------------------------
        # Deterministic answer evaluation
        # -----------------------------------

        answer_match, missing_facts = fact_match(
            healed_answer,
            required_facts
        )


        # -----------------------------------
        # Final critic
        # -----------------------------------

        if not answer_match:

            final_critique = (
                "VERDICT: FAIL\n"
                "REASON: The generated answer "
                "did not contain all required facts."
            )

            critic_pass = False

            print(
                "\n🧐 Final critic:"
            )

            print(
                final_critique
            )

        else:

            final_critique = evaluate_critic(
                original_question,
                healed_context,
                healed_answer
            )


            print(
                "\n🧐 Final critic:"
            )

            print(
                final_critique
            )


            critic_pass = (
                "VERDICT: PASS"
                in final_critique.upper()
            )


        # -----------------------------------
        # Determine recovery
        # -----------------------------------

        recovered = (
            critic_pass
            and answer_match
        )


        if recovered:

            print(
                "\n✅ SELF-HEALING SUCCESS"
            )

        else:

            print(
                "\n❌ SELF-HEALING FAILED"
            )

            if not critic_pass:

                print(
                    "   Reason: Final critic "
                    "rejected the answer."
                )

            if not answer_match:

                print(
                    "   Missing required facts: "
                    f"{missing_facts}"
                )


        # -----------------------------------
        # Save result
        # -----------------------------------

        results.append({

            "question": original_question,

            "expected_answer": expected_answer,

            "required_facts": required_facts,

            "weak_query": weak_query,

            "healing_triggered": True,

            "initial_distance": initial_top_score,

            "healed_distance": healed_top_score,

            "distance_change": distance_change,

            "retrieval_improved": retrieval_improved,

            "initial_answer": initial_answer,

            "initial_critique": initial_critique,

            "reformulated_query": new_query,

            "healed_answer": healed_answer,

            "final_critique": final_critique,

            "critic_pass": critic_pass,

            "answer_match": answer_match,

            "missing_facts": missing_facts,

            "recovered": recovered

        })


        completed_questions.add(
            original_question
        )


        # -----------------------------------
        # Save after every question
        # -----------------------------------

        save_results(results)


# -----------------------------------
# Handle interruption
# -----------------------------------

except KeyboardInterrupt:

    print(
        "\n\n⚠️ EVALUATION STOPPED BY USER"
    )

    save_results(results)

    print(
        f"💾 Saved {len(results)} completed "
        "questions."
    )


# -----------------------------------
# Handle API/network errors
# -----------------------------------

except Exception as error:

    print(
        "\n\n⚠️ EVALUATION INTERRUPTED"
    )

    print(
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )

    print(
        f"Error: {error}"
    )

    print(
        "\n💾 Saving all completed results..."
    )

    save_results(results)

    print(
        f"\nCompleted questions saved: "
        f"{len(results)}/"
        f"{len(test_questions)}"
    )

    print(
        "\nRun the evaluator again later."
    )

    print(
        "It will automatically resume from "
        "the incomplete questions."
    )

    # Don't print a giant traceback.
    sys.exit(1)


# -----------------------------------
# Metrics
# -----------------------------------

healing_cases = sum(
    1
    for result in results
    if result.get("healing_triggered")
)


recovered_cases = sum(
    1
    for result in results
    if result.get("recovered")
)


failed_cases = sum(
    1
    for result in results
    if result.get("healing_triggered")
    and not result.get("recovered")
)


retrieval_improvements = sum(
    1
    for result in results
    if result.get("healing_triggered")
    and result.get("retrieval_improved")
)


distance_improvements = [

    result["distance_change"]

    for result in results

    if result.get("healing_triggered")
    and result.get("retrieval_improved")
]


total_healing_attempts = healing_cases


# -----------------------------------
# Calculate metrics
# -----------------------------------

if healing_cases > 0:

    recovery_rate = (
        recovered_cases /
        healing_cases
    ) * 100

    healing_failure_rate = (
        failed_cases /
        healing_cases
    ) * 100

else:

    recovery_rate = 0

    healing_failure_rate = 0


if distance_improvements:

    average_distance_improvement = (
        sum(distance_improvements) /
        len(distance_improvements)
    )

else:

    average_distance_improvement = 0


average_healing_attempts = (
    total_healing_attempts /
    len(test_questions)
)


# -----------------------------------
# Final report
# -----------------------------------

print("\n")

print(
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
)

print(
    "📊 SELF-HEALING RAG EVALUATION"
)

print(
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
)


print(
    f"Total questions           : "
    f"{len(test_questions)}"
)


print(
    f"Completed questions       : "
    f"{len(results)}"
)


print(
    f"Queries requiring healing : "
    f"{healing_cases}"
)


print(
    f"Recovered queries         : "
    f"{recovered_cases}"
)


print(
    f"Failed healing cases      : "
    f"{failed_cases}"
)


print(
    f"Recovery rate             : "
    f"{recovery_rate:.2f}%"
)


print(
    f"Healing failure rate      : "
    f"{healing_failure_rate:.2f}%"
)


print(
    f"Retrieval improvements    : "
    f"{retrieval_improvements}"
)


print(
    f"Average distance improvement: "
    f"{average_distance_improvement:.4f}"
)


print(
    f"Average healing attempts  : "
    f"{average_healing_attempts:.2f}"
)


print(
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
)


# -----------------------------------
# Save final results
# -----------------------------------

save_results(results)


print(
    "\n💾 Results saved to:"
)

print(
    RESULTS_PATH
)