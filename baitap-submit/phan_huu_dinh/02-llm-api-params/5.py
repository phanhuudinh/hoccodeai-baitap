import os
import time
from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:1234/v1",
    api_key="1234"
)

MODEL_NAME = "hermes-3-llama-3.1-8b"

PROMPT_TEMPLATE = """
You are a senior developer, you can answer any code related question.
Write a python code to solve the QUESTION below.
The code should be optimized, readable and easy to understand.
Return only raw python code, no explanation, no test case, no markdown.
QUESTION: {question}
"""

def bot(question):
    while question != "exit":
        messages = [{
            "role": "user",
            "content": PROMPT_TEMPLATE.format(question=question)
        }]

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            stream=True
        )

        base = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(base, f"assets/{time.time()}_output.py")
        with open(output_path, 'w', encoding='utf-8') as outfile:
            for chunk in response:
                piece = chunk.choices[0].delta.content or ""
                outfile.write(piece)
                print(piece, end="", flush=True)
        question = input("\n> ")

def main():
    question = input("I'm a smart bot can help you solve any code related question. How can I help you?\n> ")
    bot(question)

if __name__ == "__main__":
    main()