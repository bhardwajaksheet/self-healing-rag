# Self-Healing RAG

> A Retrieval-Augmented Generation system that evaluates its own answers, detects insufficient or irrelevant evidence, reformulates queries, and retries retrieval automatically.

## 🚀 Overview

Traditional RAG systems usually follow:

```text
User Query → Retrieval → Generation → Answer
```

The problem is that if retrieval returns poor or irrelevant information, the LLM may still generate an unreliable answer.

This project introduces a **Self-Healing RAG pipeline** that uses an LLM-based critic to verify both:

- Whether the answer actually addresses the user's question
- Whether the answer is supported by the retrieved evidence

If the critic rejects the answer, the system automatically reformulates the query and retries the retrieval process.

```text
User Question
      ↓
   Retriever
      ↓
Retrieved Evidence
      ↓
   Generator
      ↓
    Critic
   ↙      ↘
 PASS     FAIL
  ↓         ↓
Answer   Reformulate
             ↓
          Retrieve
             ↓
          Generate
             ↓
           Critic
```

## 🧠 Key Features

- PDF document ingestion
- Semantic document chunking
- Gemini embeddings
- ChromaDB vector search
- Groq LLM generation
- LLM-based answer verification
- Automatic query reformulation
- Controlled self-healing loop
- Retrieval score tracking
- Safe failure when evidence is insufficient
- LangGraph workflow orchestration
- Streamlit engineering dashboard
- Controlled RAG evaluation

## 🏗️ Architecture

```text
                    ┌─────────────────┐
                    │   User Query    │
                    └────────┬────────┘
                             ↓
                    ┌─────────────────┐
                    │    Retriever    │
                    │    ChromaDB     │
                    └────────┬────────┘
                             ↓
                    ┌─────────────────┐
                    │ Retrieved       │
                    │ Evidence        │
                    └────────┬────────┘
                             ↓
                    ┌─────────────────┐
                    │    Generator    │
                    │      Groq       │
                    └────────┬────────┘
                             ↓
                    ┌─────────────────┐
                    │     Critic      │
                    │ Relevance +     │
                    │ Evidence Check  │
                    └────────┬────────┘
                             ↓
                       ┌─────┴─────┐
                       ↓           ↓
                     PASS         FAIL
                       ↓           ↓
                  Final Answer  Reformulate
                                    ↓
                                Retrieve
                                    ↓
                                Generate
                                    ↓
                                  Critic
```

## ⚙️ Technology Stack

| Component | Technology |
|---|---|
| Language | Python |
| Workflow | LangGraph |
| RAG Framework | LangChain |
| Vector Database | ChromaDB |
| Embeddings | Gemini |
| LLM | Groq |
| PDF Processing | PyPDF |
| UI | Streamlit |
| Environment | python-dotenv |

## 📂 Project Structure

```text
self-healing-rag/
│
├── data/
│   └── documents/
│       └── college_rules_test.pdf
│
├── graph/
│   ├── critic.py
│   ├── nodes.py
│   ├── state.py
│   └── workflow.py
│
├── rag/
│   ├── loader.py
│   ├── chunker.py
│   ├── embeddings.py
│   ├── vectorstore.py
│   └── generator.py
│
├── evaluation/
│   ├── test_questions.json
│   ├── evaluate.py
│   ├── baseline_results.json
│   ├── evaluate_self_healing.py
│   ├── self_healing_results.json
│   └── analyze_retrieval_scores.py
│
├── app.py
├── build_database.py
├── build_rag.py
├── ask_rag.py
├── run_agent.py
├── requirements.txt
├── .gitignore
└── README.md
```

## 🔄 How Self-Healing Works

### 1. Retrieve

The user's question is converted into an embedding and searched against the ChromaDB vector database.

### 2. Generate

The retrieved context is passed to the LLM to generate an answer.

### 3. Critic

The generated answer is independently evaluated.

The critic checks:

- Question relevance
- Evidence support
- Unsupported claims
- Contradictions
- Whether sufficient information exists

### 4. Reformulate

If the critic returns `FAIL`, the system asks another LLM to rewrite the query for better retrieval.

### 5. Retry

The reformulated query goes through retrieval and generation again.

### 6. Safe Failure

If the maximum number of healing attempts is reached without obtaining reliable evidence, the system does not fabricate an answer.

## 🧪 Example

### Query

```text
What is the minimum attendance required for the semester examination?
```

### Retrieved Evidence

```text
Students must maintain a minimum attendance of
75% in each course to be eligible for the
semester-end examination.
```

### Result

```text
Students need a minimum attendance of 75% in each
course to be eligible for the semester-end examination.
```

### Critic

```text
VERDICT: PASS
```

## 🛡️ Failure Handling

For example:

```text
Query:
campus transportation facilities
```

If the knowledge base does not contain reliable transportation information:

```text
Retrieve
   ↓
Generate
   ↓
Critic
   ↓
FAIL
   ↓
Reformulate
   ↓
Retrieve Again
   ↓
Generate
   ↓
Critic
   ↓
FAIL
   ↓
Safe Failure
```

Instead of inventing information, the system reports that it could not produce a reliably grounded answer.

## 📊 Evaluation

### Baseline RAG

A controlled 24-question benchmark was used to evaluate normal RAG question answering.

```text
Total Questions : 24
Correct Answers : 23
Accuracy        : 95.83%
```

### Self-Healing Robustness

A separate benchmark containing 24 deliberately weak retrieval queries was used to evaluate recovery behavior.

```text
Total Queries               : 24
Queries Requiring Healing   : 11
Successfully Recovered      : 10
Recovery Rate               : 90.91%

Retrieval Improvements      : 11
Average Distance Improvement: 0.2231
Average Healing Attempts    : 0.46
```

> The baseline accuracy and self-healing recovery rate measure different objectives and should not be treated as competing accuracy metrics.

## 📈 Retrieval Observability

The system records retrieval distances for each retrieved chunk.

Example:

```text
Chunk 1: 0.4620
Chunk 2: 0.4742
Chunk 3: 0.5126
```

These values are used for monitoring and evaluation.

Lower distance represents a closer vector match in the current ChromaDB retrieval setup.

## 🖥️ Streamlit Dashboard

The project includes a Streamlit dashboard that exposes the internal RAG execution.

The interface provides:

- Query input
- Execution status
- Retrieval distances
- Healing attempts
- Critic verdict
- Final answer
- LangGraph execution trace
- Recovery summary
- Retrieved evidence
- Developer diagnostics

The goal is to make the internal RAG workflow observable rather than hiding it behind a simple chatbot interface.

## 🛠️ Installation

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd self-healing-rag
```

### 2. Create virtual environment

```bash
python -m venv .venv
```

### 3. Activate environment

Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure API keys

Create a `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key
```

Never commit `.env` to GitHub.

## ▶️ Running the Project

### Build the vector database

```bash
python build_database.py
```

### Run terminal version

```bash
python run_agent.py
```

### Run Streamlit application

```bash
streamlit run app.py
```

## ⚠️ Current Limitations

This is currently a portfolio/research prototype.

Current limitations include:

- Small evaluation knowledge base
- LLM-dependent critic decisions
- LLM-dependent query reformulation
- No hybrid BM25 + semantic retrieval
- No cross-encoder reranking
- No production-scale distributed vector database
- Limited evaluation dataset
- No production latency/cost optimization

## 🔮 Future Improvements

- Hybrid BM25 + semantic retrieval
- Cross-encoder reranking
- Adaptive retrieval depth
- Better retrieval confidence estimation
- Larger multi-document knowledge bases
- Automated evaluation dataset generation
- Hallucination benchmarking
- Faithfulness scoring
- Citation generation
- Docker deployment
- FastAPI backend
- Cloud vector database
- Production monitoring
- Cost and latency optimization

## 🎯 What This Project Demonstrates

This project demonstrates practical experience with:

- Retrieval-Augmented Generation
- Vector databases
- Semantic search
- Embeddings
- LangChain
- LangGraph
- LLM orchestration
- LLM-based verification
- Query reformulation
- Failure handling
- Evaluation methodology
- Retrieval observability
- Streamlit application development

The core idea is:

> **A RAG system should not blindly trust its first retrieval attempt.**

It should evaluate whether the retrieved evidence actually supports the generated answer and attempt recovery when retrieval fails.

## 👨‍💻 Author

**Aksheet Bhardwaj**

Computer Science & Machine Learning

GitHub: https://github.com/bhardwajaksheet
