import json
import subprocess
import webbrowser
import urllib.parse
def open_in_chrome(url: str = None, query: str = None) -> str:
    """Open a URL or search query specifically for the user to see in Chrome."""
    if query:
        url = f"https://www.google.com/search?q={urllib.parse.quote_plus(query)}"
    
    if not url:
        return json.dumps({"status": "error", "message": "No URL or query provided."})

    try:
        # On macOS, use 'open -a "Google Chrome"'
        subprocess.run(["open", "-a", "Google Chrome", url], check=True)
        return json.dumps({"status": "success", "message": f"Chrome opened to: {url}"})
    except Exception:
        # Fallback to default browser
        webbrowser.open(url)
        return json.dumps({"status": "success", "message": f"Default browser opened to: {url}"})
