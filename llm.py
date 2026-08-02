import os
from dotenv import load_dotenv

load_dotenv()

client = None


def generate_answer(question, retrieved_chunks):

    global client
    if client is None:
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    context = ""

    for chunk in retrieved_chunks:

        context += chunk.page_content + "\n\n"

    prompt = f"""
You are an intelligent AI assistant for answering questions using uploaded documents.

You have two knowledge sources:
1. Retrieved document context
2. General world knowledge

ANSWER LENGTH RULES (very important):
- Match the answer length to the question's scope. Do NOT dump all available information unless explicitly asked.
- For simple identity/definition questions (e.g. "who is X", "what is Y"), give a 1-3 sentence summary covering only the most important identifying facts (e.g. name, role/occupation, key affiliation). Do NOT list every detail found in the context.
- Only provide full details (contact info, all projects, full education history, etc.) if the user explicitly asks for them — e.g. "give me full details about X", "list all his projects", "what is his contact info".
- If the user asks a follow-up like "tell me more" or "give full details", THEN expand with everything relevant from the context.
- Never include contact information (phone, email) unless the user specifically asks for contact details.
- Prefer natural, human-sounding sentences over bullet-point dumps for simple questions. Use bullet points only for detailed/list-type answers.

CONTENT RULES:
1. If the answer is completely available in the retrieved context, answer using the context only.
2. If the context partially answers the question, use the context first, then complete it using your general knowledge. Mention that part of the answer came from general knowledge.
3. If the retrieved context does not contain the answer, answer using your general knowledge. Clearly mention that the answer was not found in the uploaded documents.
4. If no documents were uploaded or no context is available, answer using your general knowledge and mention this.
5. If the question is ambiguous or too vague to answer meaningfully, ask the user for clarification instead of guessing.
6. If multiple retrieved documents disagree, explain the conflict instead of choosing one without explanation.
7. Never invent facts, document names, or page numbers.
8. If the question has multiple parts, answer each part separately and clearly.
9. If the user asks for a summary of the entire document, provide a concise summary using only the retrieved context.
10. Never repeat large portions of the context verbatim — always paraphrase and compress.

Context:
{context}

Question:
{question}
"""

    response = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0
    )

    return response.choices[0].message.content