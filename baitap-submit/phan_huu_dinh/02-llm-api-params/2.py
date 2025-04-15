from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:1234/v1",
    api_key="1234"
)

MODEL_NAME = "hermes-3-llama-3.1-8b"

def bot(prompt):
    messages = [{
        "role": "assistant",
        "content": "How can I help you?"
    }]

    while prompt != "exit":
        messages.append({
            "role": "user",
            "content": prompt
        })
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            stream=True
        )

        full_response = ""
        for chunk in response:
            content = chunk.choices[0].delta.content or ""
            print(content, end="", flush=True)
            full_response += content
        messages.append({
            "role": "assistant",
            "content": full_response
        })

        prompt = input("\n> ")

prompt = input("How can I help you?\n")
bot(prompt)
