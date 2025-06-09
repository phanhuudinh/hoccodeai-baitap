import hashlib
import inspect
import json
import logging
import os
from typing import Dict, Optional, Any

import chromadb
import requests
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import TypeAdapter
from wikipediaapi import Wikipedia

load_dotenv()

COLLECTION_NAME = "chatbot-ask"
MODEL_NAME = os.getenv('MODEL_NAME')
LLM_BASE_URL = os.getenv('LLM_BASE_URL')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

ai_client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=LLM_BASE_URL,
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
wiki = Wikipedia("Chatbot Ask", "en")

db_client = chromadb.PersistentClient(path="./data")
db_client.heartbeat()
embedding_function = embedding_functions.DefaultEmbeddingFunction()
collection = db_client.get_or_create_collection(name=COLLECTION_NAME, embedding_function=embedding_function)


def internal_search(query: str, person_name: str, n_results: int = 3) -> Dict[str, Any]:
    """
    Search for relevant context in ChromaDB
    :param query: The search user's question
    :param person_name: Name of the person, required
    :param n_results: Number of results to return
    :output: Dictionary with search results
    """
    logger.info(f"Searching for {person_name} in {query}")
    try:
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            where={"person_name": {"$eq": person_name.lower()}}
        )

        if results['documents'] and results['documents'][0]:
            relevant_results = []
            for doc, meta in zip(
                    results['documents'][0],
                    results['metadatas'][0]
            ):
                relevant_results.append({
                    'content': doc,
                    'metadata': meta
                })

            if relevant_results:
                return {
                    "found": True,
                    "results": relevant_results,
                    "message": f"Found {len(relevant_results)} relevant chunks about {person_name}"
                }

        return {
            "found": False,
            "results": [],
            "message": f"No information found about {person_name} in knowledge base"
        }

    except Exception as e:
        logger.error(f"Error searching ChromaDB: {e}")
        return {
            "found": False,
            "results": [],
            "message": f"Error searching database: {str(e)}"
        }

def get_external_info(person_name: str) -> Dict[str, Any]:
    """
    Get information about a person from Wikipedia and automatically store it in ChromaDB
    :param person_name: Name of the person to search for
    :output: Dictionary with person's information or error message
    """
    try:
        page_title = _get_wikipedia_page_title(person_name)
        if not page_title:
            return {
                "success": False,
                "message": f"No Wikipedia page found for: {person_name}",
                "stored": False
            }

        page = wiki.page(page_title)
        if not page.exists():
            return {
                "success": False,
                "message": f"Wikipedia page does not exist for: {person_name}",
                "stored": False
            }

        person_info = {
            'name': person_name.lower(),
            'title': page_title,
            'content': page.text,
        }

        _store_in_chromadb_with_chunks(person_info)

        return {
            "success": True,
            "message": f"Successfully found and stored Wikipedia information for {person_name}",
            "stored": True,
        }

    except Exception as e:
        logger.error(f"Error getting Wikipedia info: {e}")
        return {
            "success": False,
            "message": f"Error accessing Wikipedia: {str(e)}",
            "stored": False
        }

def _get_wikipedia_page_title(person_name: str) -> Optional[str]:
    """
    Get the Wikipedia page title for a person
    :param person_name: Name of the person to search for
    :output: Title of the Wikipedia page or None if not found
    """
    response = requests.get("https://en.wikipedia.org/w/api.php", {
        "action": "query",
        "list": "search",
        "srsearch": person_name,
        "format": "json"
    })

    search_results = response.json()["query"]["search"]
    if len(search_results) == 0:
        logger.warning(f"No Wikipedia results found for: {person_name}")
        return None
    return search_results[0]["title"]

def _store_in_chromadb_with_chunks(person_info: Dict) -> None:
    """
    Store person information in ChromaDB using text chunking
    :param person_info: Dictionary containing person's information
    :output: Dictionary with storage result
    """
    try:
        person_name = person_info['name']
        title = person_info['title']
        content = person_info['content']
        chunks = content.split("\n\n")

        documents = []
        ids = []
        metadatas = []
        for i, chunk in enumerate(chunks):
            chunk_id = f"{hashlib.md5(person_name.lower().encode()).hexdigest()}_{i}"

            documents.append(chunk)
            ids.append(chunk_id)
            metadatas.append({
                'person_name': person_name,
                'title': title,
                'chunk_index': i,
            })

        collection.add(
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )

        logger.info(f"Stored {len(chunks)} chunks for {person_name} in ChromaDB")

    except Exception as e:
        logger.error(f"Error storing chunks in ChromaDB: {e}")

tool_map = {
    "internal_search": internal_search,
    "get_external_info": get_external_info
}

tools = [
    {
        "type": "function",
        "function": {
            "name": "internal_search",
            "description": inspect.getdoc(internal_search),
            "parameters": TypeAdapter(internal_search).json_schema(),
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_external_info",
            "description": inspect.getdoc(get_external_info),
            "parameters": TypeAdapter(get_external_info).json_schema(),
        },
    }
]

def get_completion(messages):
    response = ai_client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        tools=tools,
        temperature=0.1
    )
    return response


def bot(prompt):
    messages = [{
        "role": "system",
        "content": """You are a helpful assistant that answers questions about popular people. 
                
                Follow this workflow:
                1. First, use internal_search to look for existing information about the person
                2. If no information is found by internal_search, use get_external_info to get information from Wikipedia (this will automatically store it in internal vector database)
                3. After Wikipedia information is retrieved and stored, then use internal_search again to retrieve information from the internal database
                4. Use the retrieved context to provide a comprehensive answer
                
                Always be factual and mention that information comes from Wikipedia when relevant."""
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