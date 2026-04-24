from tools.search_tools import web_search, read_webpage
from tools.browser_tools import open_in_chrome
from tools.weather_tools import get_current_weather
from tools.news_tools import get_current_news
from tools.time_tools import get_current_time
from tools.currency_tools import convert_currency
from tools.macos_tools import open_application
from tools.email_tools import send_email_macos as send_email

# ─── Tool Definitions (JSON Schema for Ollama) ───────────────────

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": (
                "SEARCH THE INTERNET for general knowledge, complex facts, or broad information. "
                "Do NOT use this for weather, news, time, or currency conversion if a specialized tool is available. "
                "Use this ONLY as a secondary tool or fallback. "
                "It returns text results ONLY. It does NOT open any browser window."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to look up on the web",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_webpage",
            "description": (
                "READ A SPECIFIC PAGE. Fetches the full text content of a URL. "
                "Use this if a search result snippet isn't enough and you need "
                "to read the whole article or page content to answer the user accurately. "
                "It returns text ONLY. It does NOT open a browser."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The exact URL of the webpage to read",
                    }
                },
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "open_in_chrome",
            "description": (
                "VISUAL BROWSER OPENING. Opens a URL or performs a search in the Chrome app. "
                "ONLY use this tool if the user explicitly says 'open', "
                "'show me the website', 'open chrome and search', or 'visualize in browser'. "
                "If the user wants a search, provide the 'query' parameter. "
                "If they want a specific site, provide the 'url' parameter."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Optional: Full URL to open in Chrome.",
                    },
                    "query": {
                        "type": "string",
                        "description": "Optional: Search query to perform on Google in Chrome.",
                    }
                }
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Gets the current temperature for a given city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city name, e.g. Tokyo"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The temperature unit, either 'celsius' or 'fahrenheit'"
                    }
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_news",
            "description": "Fetches the latest news headlines. Optionally provide a topic to search for specific news.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "The topic to search for in the news, e.g., 'Artificial Intelligence' or 'Tesla'."
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Gets the current time for a specific timezone.",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "The timezone to get the time for, e.g., 'Europe/London' or 'America/New_York'."
                    }
                },
                "required": ["timezone"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "convert_currency",
            "description": "Converts a specific amount from one currency to another.",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {
                        "type": "number",
                        "description": "The amount to convert."
                    },
                    "from_currency": {
                        "type": "string",
                        "description": "The 3-letter currency code to convert from, e.g., 'USD' or 'EUR'."
                    },
                    "to_currency": {
                        "type": "string",
                        "description": "The 3-letter currency code to convert to, e.g., 'JPY' or 'GBP'."
                    }
                },
                "required": ["amount", "from_currency", "to_currency"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_application",
            "description": (
                "OPEN MACBOOK APPS. Launches a specific desktop application on macOS by its name. "
                "Use this to open apps like 'Spotify', 'Calendar', 'Slack', 'Zoom', 'Mail', etc."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {
                        "type": "string",
                        "description": "The name of the application to open, e.g. 'Spotify' or 'Calculator'."
                    }
                },
                "required": ["app_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": (
                "SEND EMAIL AUTOMATICALLY. Uses direct Gmail SMTP to send an email immediately. "
                "This is fully automated and does not require opening any apps."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "recipient": {
                        "type": "string",
                        "description": "The email address to send to."
                    },
                    "subject": {
                        "type": "string",
                        "description": "The subject line of the email."
                    },
                    "body": {
                        "type": "string",
                        "description": "The main text content of the email."
                    }
                },
                "required": ["recipient"]
            }
        }
    }
]

# ─── Tool Registry mapping names to functions ───────────────────

TOOL_REGISTRY = {
    "web_search": web_search,
    "read_webpage": read_webpage,
    "open_in_chrome": open_in_chrome,
    "get_current_weather": get_current_weather,
    "get_current_news": get_current_news,
    "get_current_time": get_current_time,
    "convert_currency": convert_currency,
    "open_application": open_application,
    "send_email": send_email,
}
