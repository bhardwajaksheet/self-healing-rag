from langchain_chroma import Chroma

from rag.embeddings import get_embeddings
from rag.generator import generate_answer
from graph.critic import critic

from groq import Groq
import os

from dotenv import load_dotenv


load_dotenv()


# -----------------------------------
# Groq client
# -----------------------------------

groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# -----------------------------------
# Retrieval
# -----------------------------------

def retrieve(state):
    print("\n🔎 RETRIEVING...")

    embeddings = get_embeddings()

    vectorstore = Chroma(
        persist_directory="./chroma_db",
        embedding_function=embeddings
    )

    question = state["question"].strip()

    # Safety guard: never send an empty query
    # to the embedding model.
    if not question:
        raise ValueError(
            "Retrieval query is empty. "
            "The system refused to send an empty query "
            "to the embedding model."
        )

    results = vectorstore.similarity_search_with_score(
        question,
        k=3
    )

    context = "\n\n".join(
        result.page_content
        for result, score in results
    )

    scores = [
        score
        for result, score in results
    ]

    print("\n📊 Retrieval scores:")

    for i, score in enumerate(scores, 1):
        print(f"   Chunk {i}: {score:.4f}")

    return {
        "context": context,
        "retrieval_scores": scores
    }


# -----------------------------------
# Generation
# -----------------------------------

def generate(state):

    print("\n🤖 GENERATING...")

    answer = generate_answer(
        state["question"],
        state["context"]
    )

    return {
        "answer": answer
    }


# -----------------------------------
# Critic
# -----------------------------------

def evaluate(state):

    print("\n🧐 CRITIC EVALUATING...")

    critique = critic(
        state["question"],
        state["context"],
        state["answer"]
    )

    return {
        "critique": critique
    }


# -----------------------------------
# Query reformulation
# -----------------------------------

def reformulate(state):
    print("\n🔄 SELF-HEALING: REFORMULATING QUERY...")

    question = state["question"].strip()
    critique = state["critique"]

    new_question_prompt = f"""
You are a query reformulation agent for a Self-Healing RAG system.

Original user question:

{question}

The previous RAG attempt was rejected by the critic.

Critic feedback:

{critique}

Rewrite the original question so that it is:

1. Clearer
2. More specific
3. Better suited for document retrieval
4. Faithful to the original meaning

IMPORTANT:
- Do not introduce new subjects.
- Do not introduce countries, universities, curricula,
  organizations, people, or assumptions.
- Do not change the meaning of the original question.
- Do not invent information.
- Only improve the wording for retrieval.
- The rewritten question MUST NOT be empty.

Return ONLY the rewritten question.
"""

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": new_question_prompt
            }
        ],
        temperature=0
    )

    new_question = (
        response.choices[0].message.content or ""
    ).strip()

    # --------------------------------------------------------
    # SAFETY GUARD
    # Never allow an empty query to reach the embedding model.
    # --------------------------------------------------------

    if not new_question:
        print(
            "\n⚠️ Reformulation returned an empty query."
        )

        print(
            "↩️ Falling back to the previous query."
        )

        new_question = question.strip()

    if not new_question:
        raise ValueError(
            "Self-healing produced an empty retrieval query."
        )

    print(f"\n🔄 New query: {new_question}")

    return {
        "question": new_question,
        "attempts": state["attempts"] + 1
    }
