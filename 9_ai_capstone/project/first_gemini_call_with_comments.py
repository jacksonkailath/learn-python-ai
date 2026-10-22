"""Your first Gemini call — prompt in, text out.

The smallest possible script that talks to an AI model from Python. One
prompt goes in; one sentence comes back. Everything else in this section
is assembly around this call.

Run it (terminal in 9_ai_capstone/, venv activated — prompt shows (.venv)):
    python first_gemini_call.py

With no GEMINI_API_KEY set, it explains how to get a free one and exits
cleanly — no API call, no crash, no cost.
"""

import os 
#os is a module in Python's standard library — it ships with Python, so there's nothing to install.
#The name stands for "operating system": it's the toolbox for talking to the machine your script is running on (files, paths, processes, environment variables).
from pathlib import Path

from dotenv import load_dotenv
#This is the one third-party import in the file — hence the blank line above it, separating it from the stdlib group.
#load_dotenv is a function
#It opens the file you point it at, parses lines of the form KEY=value, and stuffs each pair into os.environ

# The key lives in project/.env (copy project/.env.example), never in code.
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
    #ensure requirements for this section are installed: uv pip install -r requirements.txt
    #google is a namespace package — a top-level name that several unrelated Google libraries share, with no code of its own. google-auth, google-cloud-storage, google-genai all install into it.
    #import google gets you an empty shell — nothing callable.
    #from google import genai pulls in the subpackage that the google-genai distribution contributed to that namespace.
    #pip install google-genai      # what you install 
    #but we we install using requirements.txt, which pins versions and installs all dependencies at once.

    client = genai.Client()  # picks up GEMINI_API_KEY from the environment
    # A client is a helper object that remembers everything that stays the same
    # between calls: your API key, where Google's servers are, how to talk to
    # them. Setting it up sends nothing over the internet — it just gets ready.
    #
    # Think of a phone with Google's number saved and your caller ID set. You
    # don't re-enter those every time; you just say what you want.
    #genai.Client() builds a configured HTTP client and hands you back a handle
    #No network call happens here. Nothing is sent until client.models.generate_content(...) on the next line.

    '''
    OPTIONAL — for the curious. Skip this on a first read.

    Under everything, a Gemini call is one HTTPS POST request — the same kind
    of request a browser makes when you submit a form. Written by hand with the
    `requests` library it's roughly:

        requests.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent",
            headers={"x-goog-api-key": "AIza...", "Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": PROMPT}]}]},
            timeout=60,
        )

    Reading it line by line:

    - The URL is the address on Google's servers that generates text. It names
      the API version (v1beta), the model, and the action (generateContent).
      Change the model name in the URL and you're talking to a different model.
    - headers are labels attached to the request, separate from its content.
      Here they carry two things: your API key, so Google knows who is asking
      (and whose quota to count), and a note saying "the body is JSON" so the
      server knows how to read it.
    - json is the body — the actual message. Google expects a specific nested
      shape: a list of contents, each with parts, each part holding text. Your
      prompt sits at the bottom of that nesting. The `requests` library turns
      the Python dict into JSON text and sends it.
    - model is in the url
    - timeout is how many seconds to wait for a reply before giving up. Without
      it, a stalled network could leave the script hanging forever.

    Notice how much of that is the same every time: the host, the version
    segment, the auth header, the timeout, the JSON shape. Only the model name
    and the prompt vary between calls.

    A client object is what you get when you factor out the constant parts and
    store them once. genai.Client() is that factoring. Afterwards,
    generate_content(model=..., contents=...) supplies only the two things that
    change.
    '''

    response = client.models.generate_content(model=MODEL, contents=PROMPT)
    print(f"\n{response.text}")


if __name__ == "__main__":
    main()
