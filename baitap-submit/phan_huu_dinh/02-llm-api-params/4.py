import os
import sys
from re import error

from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:1234/v1",
    api_key="1234"
)

MODEL_NAME = "hermes-3-llama-3.1-8b"
CHUNK_SIZE = 10 # Number of lines to process at once
def translate_file(file_path):
    try:
        base, ext = os.path.splitext(file_path)
        output_path = f"{base}_translated{ext}"
        with open(file_path, 'r', encoding='utf-8') as file, open(output_path, 'w', encoding='utf-8') as outfile:
            while True:
                lines = [file.readline() for _ in range(CHUNK_SIZE)]
                lines = [line for line in lines if line]
                if not lines:
                    break
                outfile.write(translate(''.join(lines)))
    except error:
        print(f"Error during translation: {error}")

def translate(text):
    prompt = f"""Translate the TEXT below into Vietnamese using comedy style, return only the translated text.
    TEXT: {text}"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )

    return response.choices[0].message.content

def main():
    if len(sys.argv) != 2:
        print("Usage: python 4.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    translate_file(file_path)

if __name__ == "__main__":
    main()