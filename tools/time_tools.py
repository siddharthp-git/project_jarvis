import json
import urllib.request
import urllib.parse

def get_current_time(timezone: str) -> str:
    """Gets the current time for a specific timezone.
    
    Args:
        timezone: The timezone to get the time for, e.g., 'Europe/London' or 'America/New_York'.
    """
    # Sanitize input: Strip redundant LLM tokens if they leaked into the string
    timezone = timezone.replace('<|"|>', '').replace('<|', '').replace('|>', '').replace('"', '').strip()
    try:
        url = f"https://timeapi.io/api/Time/current/zone?timeZone={urllib.parse.quote(timezone)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'JarvisAssistant/1.0', 'Accept': 'application/json'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))

        time_str = data.get("time")
        date_str = data.get("date")

        if time_str and date_str:
            return f"The current time in {timezone} is {time_str} on {date_str}."
        return f"Could not fetch time for {timezone}."

    except Exception as e:
        return f"Error fetching time for {timezone}. API Error: {e}"
