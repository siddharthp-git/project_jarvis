import json
import sys
import urllib.request
import urllib.error
from config import OLLAMA_URL, MODEL, TIMEOUT
from tools import TOOLS

def chat_request_stream(messages: list, use_tools: bool = True):
    """Generator that yields streamed chunks from Ollama."""
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": True,
    }
    if use_tools:
        payload["tools"] = TOOLS

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_URL,
        data=data,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            for line in resp:
                if line:
                    chunk = json.loads(line.decode("utf-8"))
                    yield chunk
    except Exception as e:
        print(f"\n  ❌ Streaming Error: {e}")
        return

def chat_request(messages: list, use_tools: bool = True) -> dict:
    """Send a non-streaming chat request (useful for tool-calling rounds)."""
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
    }
    if use_tools:
        payload["tools"] = TOOLS

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_URL,
        data=data,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        print(f"\n  ❌ Cannot reach Ollama at {OLLAMA_URL}")
        print(f"     Error: {e}")
        sys.exit(1)
