from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:1234/v1",
    api_key="1234"
)

MODEL_NAME = "deepseek-r1-distill-qwen-7b"

def bot(prompt):
    while prompt != "exit":
        messages = [{
            "role": "user",
            "content": prompt
        }]

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            stream=True
        )

        for chunk in response:
            print(chunk.choices[0].delta.content or "", end="", flush=True)
        prompt = input("\n> ")

bot(input("How can I help you?\n"))
