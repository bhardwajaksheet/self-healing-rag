from langchain_chroma import Chroma

from rag.embeddings import get_embeddings


print("🧠 Connecting to existing vector database...")

embeddings = get_embeddings()

vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings
)


question = "What is the minimum attendance required for the semester examination?"

print("\n🔎 Searching...\n")

results = vectorstore.similarity_search(
    question,
    k=3
)

print(f"Found {len(results)} chunks.\n")

for i, result in enumerate(results, 1):
    print(f"--- CHUNK {i} ---")
    print(result.page_content)
    print()