import json
import urllib.request
import urllib.parse

def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """Converts a specific amount from one currency to another.
    
    Args:
        amount: The amount to convert.
        from_currency: The 3-letter currency code to convert from, e.g., 'USD' or 'EUR'.
        to_currency: The 3-letter currency code to convert to, e.g., 'JPY' or 'GBP'.
    """
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
        req = urllib.request.Request(url, headers={'User-Agent': 'JarvisAssistant/1.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))

        rates = data.get("rates", {})
        if to_currency not in rates:
            return f"Error: Currency code '{to_currency}' is not supported or invalid."

        rate = rates[to_currency]
        converted = float(amount) * rate
        return f"{amount} {from_currency} is equal to {converted:.2f} {to_currency} (Rate: {rate})."

    except Exception as e:
        return f"Error converting currency: {e}"
