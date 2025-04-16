from openai import OpenAI
from bs4 import BeautifulSoup
from requests import request

client = OpenAI(
    base_url="http://127.0.0.1:1234/v1",
    api_key="1234"
)

MODEL_NAME = "deepseek-r1-distill-qwen-7b"

def bot(paper_url):
    while paper_url != "exit":
        # validate url
        if not paper_url.startswith("https://tuoitre.vn"):
            paper_url = input("Invalid URL, please try again.\n> ")
            continue

        page_content = get_page_content(paper_url)
        prompt = f"""Summarize the paper in the CONTENT below by keeping the same language as the original paper.
        CONTENT: {page_content}
        """

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
        paper_url = input("\nInput another url to continue\n> ")

def get_page_content(url):
    page_content = request("GET", url)
    soup = BeautifulSoup(page_content.text, "html.parser")
    main_content = soup.find("div", {"id": "main-detail"})
    return main_content.getText()

url = input("Give me the URL of a scientific paper (from tuoitre.vn), I will summarize it.\n> ")
bot(url)
