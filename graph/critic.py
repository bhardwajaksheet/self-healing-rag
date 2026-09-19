import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def critic(question, context, answer):

    prompt = f"""
You are a strict verification critic for a Self-Healing RAG system.

Your job is to decide whether the generated answer is reliable enough
to be returned to the user.

You MUST evaluate TWO separate things:

1. QUESTION RELEVANCE
   Does the answer actually answer the user's specific question?

2. EVIDENCE SUPPORT
   Is the answer fully supported by the retrieved context?

An answer must satisfy BOTH conditions to receive PASS.

--------------------------------------------------
USER QUESTION
--------------------------------------------------

{question}

--------------------------------------------------
RETRIEVED CONTEXT
--------------------------------------------------

{context}

--------------------------------------------------
GENERATED ANSWER
--------------------------------------------------

{answer}

--------------------------------------------------
VERIFICATION RULES
--------------------------------------------------

PASS only if ALL of the following are true:

1. The answer directly addresses the user's question.

2. The answer contains the information needed to answer
   the user's question.

3. The claims in the answer are supported by the retrieved context.

4. The answer does not introduce unsupported facts.

5. The answer does not contradict the retrieved context.

6. The answer does not answer a different question merely because
   the retrieved context contains information related to the topic.

7. If the context does not contain enough information to answer
   the question, return FAIL.

8. If the answer says:
   "I don't have enough information"
   or any equivalent statement indicating insufficient evidence,
   return FAIL.

IMPORTANT:

A factually correct statement is NOT enough for PASS.

The answer must answer the ACTUAL USER QUESTION.

Example:

Question:
"What must a student have to enter the semester-end examination?"

Context:
"The semester-end examination requires students to carry
a valid college ID card and examination hall ticket."

Answer:
"Students must carry their valid college ID card and
examination hall ticket."

→ PASS

But:

Question:
"What must a student have to enter the semester-end examination?"

Context:
"Students with 75% attendance are eligible for the examination."

Answer:
"Students need 75% attendance to be eligible."

→ FAIL

The answer is supported by the context, but it does not answer
what the student must HAVE to enter the examination.

--------------------------------------------------
OUTPUT FORMAT
--------------------------------------------------

Return EXACTLY this format:

VERDICT: PASS
REASON: <short explanation>

OR

VERDICT: FAIL
REASON: <short explanation>

Do not output anything else.
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content