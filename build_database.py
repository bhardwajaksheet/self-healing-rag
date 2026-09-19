from rag.loader import load_pdf
from rag.chunker import split_documents
from rag.vectorstore import create_vectorstore


PDF_PATH = "data/documents/college_rules_test.pdf"


print("📄 Loading PDF...")

documents = load_pdf(PDF_PATH)

print(f"Loaded {len(documents)} pages.")

print("✂️ Splitting document...")

chunks = split_documents(documents)

print(f"Created {len(chunks)} chunks.")

print("🧠 Creating vector database...")

create_vectorstore(chunks)

print("✅ Vector database created successfully!")