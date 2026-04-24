import json
import importlib
import sys
import os

try:
    from tavily import TavilyClient as _TavilyClient
    _TAVILY_AVAILABLE = True
    _IMPORT_ERROR = None
except ImportError as e:
    _TAVILY_AVAILABLE = False
    _IMPORT_ERROR = str(e)

_client = None


def _get_client():
    """Return a TavilyClient, creating it lazily with diagnostic checks."""
    global _client
    
    if not _TAVILY_AVAILABLE:
        return None, f"Package 'tavily-python' not found. Error: {_IMPORT_ERROR}"

    try:
        # Reload config to ensure we see disk changes
        import config
        importlib.reload(config)
        key = getattr(config, "TAVILY_API_KEY", None)
    except Exception as e:
        return None, f"Failed to load config.py: {str(e)}"

    if not key:
        return None, "TAVILY_API_KEY is missing or empty in config.py"

    if _client is None:
        try:
            _client = _TavilyClient(api_key=key)
        except Exception as e:
            return None, f"Failed to initialize TavilyClient: {str(e)}"
            
    return _client, None


def _error_response(tool: str, message: str) -> str:
    return json.dumps({
        "status": "error",
        "message": f"[{tool}] {message}",
        "action_required": "Please verify your TAVILY_API_KEY in config.py and ensure 'pip3 install tavily-python' was successful."
    })


def web_search(query: str, max_results: int = 5) -> str:
    """Search the web for general knowledge, facts, and broad information.
    
    IMPORTANT: Do NOT use this for current weather, news, or time if a specialized tool exists.
    Only use this as a fallback if specialized tools fail or if the information is not covered by them.
    """
    client, error = _get_client()
    if error:
        return _error_response("web_search", error)

    try:
        response = client.search(
            query=query,
            max_results=max_results,
            search_depth="basic",
            include_answer=True,
        )

        results = response.get("results", [])
        answer  = response.get("answer", "")

        summary_lines = []
        if answer:
            summary_lines.append(f"DIRECT ANSWER: {answer}")
        
        for i, r in enumerate(results, 1):
            title = r.get("title", "No Title")
            snippet = r.get("content", "")
            url = r.get("url", "")
            summary_lines.append(f"SOURCE {i} [{title}]: {snippet} (URL: {url})")

        concise_summary = "\n\n".join(summary_lines)

        return json.dumps({
            "status": "success",
            "query": query,
            "info_for_ai": concise_summary,
            "num_results": len(results),
        })

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Tavily search failed: {str(e)}",
        })


def read_webpage(url: str) -> str:
    """Extract clean text content from a URL using Tavily's extract endpoint."""
    client, error = _get_client()
    if error:
        return _error_response("read_webpage", error)

    try:
        response = client.extract(urls=[url])
        results  = response.get("results", [])

        if not results:
            return json.dumps({
                "status": "no_content",
                "message": "No extractable content found.",
            })

        text = results[0].get("raw_content", "")

        if len(text) > 3000:
            text = text[:3000] + "\n\n... [content truncated for brevity]"

        return json.dumps({
            "status": "success",
            "url": url,
            "page_text": text,
        })

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Tavily extract failed: {str(e)}",
        })
