from retriever import retrieve

from llm import generate_answer


question = input("Ask Question : ")

chunks = retrieve(question)

answer = generate_answer(question, chunks)

print("\n")

print(answer)

print("\nSources\n")

for chunk in chunks:

    print(chunk.metadata["source"])

    print("Page", chunk.metadata["page"] + 1)

    print()