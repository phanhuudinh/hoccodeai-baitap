import inspect
import json
import os

import requests
import yfinance as yf
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import TypeAdapter

load_dotenv()


def get_symbol(company: str) -> str:
    """
    Retrieve the stock symbol for a specified company using the Yahoo Finance API.
    :param company: The name of the company for which to retrieve the stock symbol, e.g., 'Nvidia'.
    :output: The stock symbol for the specified company.
    """
    url = "https://query2.finance.yahoo.com/v1/finance/search"
    params = {"q": company, "country": "United States"}
    user_agents = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"}
    res = requests.get(
        url=url,
        params=params,
        headers=user_agents)

    data = res.json()
    symbol = data['quotes'][0]['symbol']
    return symbol


def get_stock_price(symbol: str):
    """
    Retrieve the most recent stock price data for a specified company using the Yahoo Finance API via the yfinance Python library.
    :param symbol: The stock symbol for which to retrieve data, e.g., 'NVDA' for Nvidia.
    :output: A dictionary containing the most recent stock price data.
    """
    stock = yf.Ticker(symbol)
    hist = stock.history(period="1d", interval="1m")
    latest = hist.iloc[-1]
    return {
        "timestamp": str(latest.name),
        "open": latest["Open"],
        "high": latest["High"],
        "low": latest["Low"],
        "close": latest["Close"],
        "volume": latest["Volume"]
    }

tool_map = {
    "get_symbol": get_symbol,
    "get_stock_price": get_stock_price
}

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_symbol",
            "description": inspect.getdoc(get_symbol),
            "parameters": TypeAdapter(get_symbol).json_schema(),
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": inspect.getdoc(get_stock_price),
            "parameters": TypeAdapter(get_stock_price).json_schema(),
        },
    }
]

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
LLM_BASE_URL = "http://127.0.0.1:1234/v1"
MODEL_NAME = "hermes-3-llama-3.1-8b"
client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=LLM_BASE_URL,
)


def get_completion(messages):
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        tools=tools,
        temperature=0.1
    )
    return response


def bot(prompt):
    messages = [{
        "role": "system",
        "content": "You are a helpful customer support assistant. Use the supplied tools to assist the user. You're analytical and sarcasm"
    }, {
        "role": "assistant",
        "content": "How can I help you?"
    }]

    while prompt != "exit":
        messages.append({
            "role": "user",
            "content": prompt
        })
        response = get_completion(messages)
        first_choice = response.choices[0]
        finish_reason = first_choice.finish_reason

        while finish_reason != "stop":
            messages.append(first_choice.message)
            tool = first_choice.message.tool_calls[0]
            function_name = tool.function.name
            arguments = json.loads(tool.function.arguments)
            if function_name in tool_map:
                data = tool_map[function_name](**arguments)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool.id,
                    "name": function_name,
                    "content": json.dumps(data)
                })
            function_response = get_completion(messages)
            first_choice = function_response.choices[0]
            finish_reason = first_choice.finish_reason

        messages.append({
            "role": "assistant",
            "content": first_choice.message.content
        })
        print(first_choice.message.content)
        prompt = input("\n> ")


def main():
    prompt = input("How can I help you?\n> ")
    bot(prompt)


if __name__ == "__main__":
    main()