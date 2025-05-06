import inspect
import json

from openai import OpenAI
from pydantic import TypeAdapter
from requests import request

JINA_HOST = "https://r.jina.ai"
JINA_API_KEY = "jina_d2c32587125a45b4814f1c8dc84181a2b6rmETjBy7b4p1_k7mbo814yv1BB"

MODEL_NAME = "hermes-3-llama-3.1-8b"
LLM_BASE_URL = "http://127.0.0.1:1234/v1"
LLM_API_KEY = "local"

client = OpenAI(
    base_url=LLM_BASE_URL,
    api_key=LLM_API_KEY
)


def view_website(url: str) -> str:
    """
    View the content of a website using Jina API.
    :param url: str of the website URL
    :return: str of the website content in MARKDOWN format
    """

    headers = {
        "Authorization": f"Bearer {JINA_API_KEY}"
    }

    page_content = request(
        "GET",
        f"{JINA_HOST}/{url}",
        headers=headers
    )
    return page_content.text

tool_map = {
    "view_website": view_website
}

tools = [{
    "type": "function",
    "function": {
        "name": "view_website",
        "description": inspect.getdoc(view_website),
        "parameters": TypeAdapter(view_website).json_schema(),
    }
}]


def bot(prompt):
    messages = [{
        "role": "system",
        "content": """You are a smart chatbot, let help user by answer their questions, if you don't know just let them know that you don't know
        Return response in English."""
    }, {
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
            # stream=True,
            tools=tools,
        )

        if response.choices[0].finish_reason == "tool_calls":
            messages.append(response.choices[0].message)
            tool = response.choices[0].message.tool_calls[0]
            function_name = tool.function.name
            arguments = json.loads(tool.function.arguments)
            if function_name in tool_map:
                data = tool_map[function_name](**arguments)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool.id,
                    "name": function_name,
                    "content": data
                })
            function_response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages
            )
            messages.append({
                "role": "assistant",
                "content": function_response.choices[0].message.content
            })
            print(function_response.choices[0].message.content)
            prompt = input("\n> ")
            continue

        messages.append({
            "role": "assistant",
            "content": response.choices[0].message.content
        })
        print(response.choices[0].message.content)
        prompt = input("\n> ")


def main():
    prompt = input("How can I help you?\n> ")
    bot(prompt)


if __name__ == "__main__":
    main()
