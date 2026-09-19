from langchain_chroma import Chroma

from rag.embeddings import get_embeddings
from rag.generator import generate_answer
from graph.critic import critic


print("🧠 Connecting to vector database...")

embeddings = get_embeddings()

vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings
)


question = input("\n❓ Ask a question: ")


print("\n🔎 Retrieving relevant information...")

results = vectorstore.similarity_search(
    question,
    k=3
)


context = "\n\n".join(
    result.page_content
    for result in results
)


print("🤖 Generating answer...\n")

answer = generate_answer(
    question,
    context
)


print("🧐 Critic checking answer...\n")

critique = critic(
    question,
    context,
    answer
)


print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("GENERATED ANSWER")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print(answer)

print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("🧐 CRITIC")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print(critique)

print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")