from typing import TypedDict


class RAGState(TypedDict):
    question: str
    context: str
    answer: str
    critique: str
    attempts: int
    retrieval_scores: list[float]