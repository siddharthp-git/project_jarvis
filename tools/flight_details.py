from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import urllib.request
import urllib.parse
import json
from typing import Any, Dict, List, Optional

from config import get_settings

# AviationStack base URL — free plan requires HTTP (not HTTPS)
_BASE_URL = "http://api.aviationstack.com/v1/flights"


class FlightService:
    """Fetches live flight data from AviationStack."""

    def __init__(self) -> None:
        settings = get_settings()
        self._api_key = settings.aviationstack_api_key

    def search_flights(
        self,
        dep_iata: str,
        arr_iata: Optional[str] = None,
        flight_iata: Optional[str] = None,
        airline_iata: Optional[str] = None,
        flight_status: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Search for flights using AviationStack.

        Args:
            dep_iata:       Departure airport IATA code, e.g. "DEL"
            arr_iata:       Arrival airport IATA code, e.g. "BOM"
            flight_iata:    Specific flight number, e.g. "AI101"
            airline_iata:   Filter by airline IATA code, e.g. "AI"
            flight_status:  "scheduled" | "active" | "landed" | "cancelled" | "incident" | "diverted"
            limit:          Max number of results (default 10)

        Returns:
            List of raw flight dicts from AviationStack.
        """
        params: Dict[str, Any] = {
            "access_key": self._api_key,
            "dep_iata": dep_iata.upper(),
            "limit": limit,
        }
        if arr_iata:
            params["arr_iata"] = arr_iata.upper()
        if flight_iata:
            params["flight_iata"] = flight_iata.upper()
        if airline_iata:
            params["airline_iata"] = airline_iata.upper()
        if flight_status:
            params["flight_status"] = flight_status

        url = f"{_BASE_URL}?{urllib.parse.urlencode(params)}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "JarvisAssistant/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())
        except Exception as e:
            return [{"error": f"Network error: {e}"}]

        if "error" in data:
            err = data["error"]
            return [{"error": f"AviationStack error {err.get('code')}: {err.get('message')}"}]

        return data.get("data", [])

    def format_flights(self, flights: List[Dict[str, Any]]) -> str:
        """Return a human-readable summary of a list of flights."""
        if not flights:
            return "No flights found."

        if "error" in flights[0]:
            return flights[0]["error"]

        lines: List[str] = []
        for f in flights:
            airline   = (f.get("airline") or {}).get("name", "Unknown Airline")
            flight_no = (f.get("flight") or {}).get("iata", "?")
            status    = f.get("flight_status", "unknown")

            dep       = f.get("departure") or {}
            arr       = f.get("arrival") or {}
            dep_ap    = dep.get("iata", "?")
            arr_ap    = arr.get("iata", "?")
            dep_time  = dep.get("scheduled", dep.get("actual", "N/A"))
            arr_time  = arr.get("scheduled", arr.get("actual", "N/A"))

            lines.append(
                f"✈  {airline} {flight_no} | {dep_ap} → {arr_ap} | "
                f"Dep: {dep_time} | Arr: {arr_time} | Status: {status}"
            )
        return "\n".join(lines)


def get_flight_details(
    dep_iata: str,
    arr_iata: Optional[str] = None,
    flight_iata: Optional[str] = None,
    flight_status: Optional[str] = None,
) -> str:
    """
    Tool function called by Jarvis to look up live flight information.

    Args:
        dep_iata:      Departure airport IATA code (e.g. "DEL", "JFK").
        arr_iata:      Arrival airport IATA code (optional).
        flight_iata:   Specific flight number to look up (e.g. "AI101").
        flight_status: Filter by status: scheduled | active | landed | cancelled.

    Returns:
        A plain-text formatted summary of matching flights.
    """
    svc = FlightService()
    flights = svc.search_flights(
        dep_iata=dep_iata,
        arr_iata=arr_iata,
        flight_iata=flight_iata,
        flight_status=flight_status,
    )
    return svc.format_flights(flights)


if __name__ == "__main__":
    result = get_flight_details(dep_iata="DEL", arr_iata="BOM")
    print(result)