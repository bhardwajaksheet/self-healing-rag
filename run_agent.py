from graph.workflow import build_graph


app = build_graph()


question = input("\n❓ Ask your question: ")


initial_state = {
    "question": question,
    "context": "",
    "answer": "",
    "critique": "",
    "attempts": 0,
    "retrieval_scores": []
}


print("\n🚀 Starting Self-Healing RAG...")


final_state = app.invoke(initial_state)


print("\n")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("🎯 FINAL ANSWER")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


if "VERDICT: PASS" in final_state["critique"].upper():

    print(final_state["answer"])

else:

    print(
        "The system could not produce a reliably grounded "
        "answer after the maximum number of healing attempts."
    )


print("\n")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("📊 FINAL RETRIEVAL SCORES")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


for i, score in enumerate(
    final_state["retrieval_scores"],
    1
):

    print(
        f"Chunk {i}: {score:.4f}"
    )


print("\n")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("🧠 FINAL CRITIC")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

print(final_state["critique"])


print("\n")
print(
    f"🔄 Healing attempts: "
    f"{final_state['attempts']}"
)

print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")