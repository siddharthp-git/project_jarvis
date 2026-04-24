import json
import urllib.request
import urllib.parse
from config import NEWS_API_KEY

def get_current_news(topic: str = None) -> str:
    """Fetches the latest news headlines. Optionally provide a topic to search for specific news.
    
    Args:
        topic: The topic to search for in the news, e.g., 'Artificial Intelligence' or 'Tesla'.
    """
    if topic:
        # Sanitize input: Strip redundant LLM tokens if they leaked into the string
        topic = topic.replace('<|"|>', '').replace('<|', '').replace('|>', '').replace('"', '').strip()
    api_key = NEWS_API_KEY
    if not api_key or api_key == "YOUR_NEWS_API_KEY":
        return "Error: Please replace 'YOUR_NEWS_API_KEY' with your actual NewsAPI key in config.py."

    try:
        if topic and topic.strip():
            url = f"https://newsapi.org/v2/everything?q={urllib.parse.quote(topic)}&sortBy=publishedAt&pageSize=5&apiKey={api_key}"
        else:
            url = f"https://newsapi.org/v2/top-headlines?language=en&pageSize=5&apiKey={api_key}"

        req = urllib.request.Request(url, headers={'User-Agent': 'JarvisAssistant/1.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))

        if data.get("status") != "ok":
            return f"Error fetching news: {data.get('message', 'Unknown error')}"

        articles = data.get("articles", [])
        if not articles:
            return f"No news articles found{' for ' + topic if topic else ''}."

        results = [f"News{' on ' + topic if topic else ' Headlines'}:"]
        for i, article in enumerate(articles, 1):
            title = article.get("title", "No Title")
            source = article.get("source", {}).get("name", "Unknown Source")
            results.append(f"{i}. {title} ({source})")

        return "\n".join(results)

    except Exception as e:
        return f"Error fetching news: {e}"
