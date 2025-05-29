import os

import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from openai import OpenAI
from wikipediaapi import Wikipedia

load_dotenv()

COLLECTION_NAME = "chatbot-bio"
MODEL_NAME = os.getenv('MODEL_NAME')
LLM_BASE_URL = os.getenv('LLM_BASE_URL')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

client = chromadb.PersistentClient(path="./data")
client.heartbeat()
embedding_function = embedding_functions.DefaultEmbeddingFunction()
collection = client.get_or_create_collection(name=COLLECTION_NAME, embedding_function=embedding_function)

wiki = Wikipedia("Chatbot Bio", "en")
doc = wiki.page("Sơn Tùng M-TP").text
paragraphs = doc.split("\n\n")

for index, paragraph in enumerate(paragraphs):
    if len(paragraph) > 0:
        collection.add(documents=[paragraph], ids=[str(index)])

query = "what is Sơn Tùng M-TP's real name?"
q = collection.query(query_texts=[query], n_results=3)
CONTEXT = q["documents"] # use the top 3 paragraphs as context

prompt = f"""
Use the CONTEXT below as the additional information to answer the QUESTION at the end.
User an appropriate tone and style for the question.
If you don't know the answer, say "I don't know".
CONTEXT: {CONTEXT}

QUESTION: {query}
"""

client = OpenAI(
    base_url=LLM_BASE_URL,
    api_key=OPENAI_API_KEY
)

response = client.chat.completions.create(
    model=MODEL_NAME,
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)

print(response.choices[0].message.content)
