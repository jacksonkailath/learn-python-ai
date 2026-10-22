import os 
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / "project" / ".env")

MODEL = "gemini-3.6-flash"
PROMPT = "In one friendly sentence, what can a Python script do once it can call an AI model?"

def main() -> None:
    if not os.environ.get("GEMINI_API_KEY"):
        print("GEMINI_API_KEY is not set — no API call was made.") 
        print("Get a free key (no card needed): aistudio.google.com -> Get API key.")
        print("Then copy project/.env.example to project/.env and paste it in.")
        return

    from google import genai  # imported only when a key exists

    client = genai.Client()  # picks up GEMINI_API_KEY from the environment

    response = client.models.generate_content(model=MODEL, contents=PROMPT)
    print(f"\n{response.text}")

if __name__ == "__main__":
    main()
