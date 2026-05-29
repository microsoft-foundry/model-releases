# =============================================================================
# s02_tools_mock.py — Mock tools (Steps 2, 5, 7)
# =============================================================================
# NARRATIVE ROLE
# In the real world, an agent would call live booking APIs and a policy
# retrieval system.  These mocks return plausible hard-coded data so the
# workshop runs offline, stays deterministic, and never charges a credit card.
#
# The four tools mirror the four tasks identified in Step 3's task
# decomposition: search_flights, search_hotels, check_policy, submit_booking.
# TOOL_SCHEMAS drives the Responses API tool-calling loop; DISPATCH maps
# function names to their Python implementations for local execution.
# =============================================================================
import random


def search_flights(origin: str, dest: str, depart_date: str) -> dict:
    return {
        "results": [
            {"carrier": "LH", "number": "LH457",
             "depart": f"{depart_date}T20:30",
             "arrive_local": "next-day 15:25",
             "price_usd": 1180, "stops": 1},
            {"carrier": "UA", "number": "UA962",
             "depart": f"{depart_date}T17:50",
             "arrive_local": "next-day 14:10",
             "price_usd": 1340, "stops": 1},
        ]
    }


def search_hotels(city: str, checkin: str, checkout: str,
                  area: str | None = None) -> dict:
    return {
        "results": [
            {"name": "Park Inn Alexanderplatz", "area": area or "central",
             "nightly_usd": 165, "total_usd": 495, "rating": 4.1},
            {"name": "H4 Hotel Berlin Alexanderplatz", "area": area or "central",
             "nightly_usd": 198, "total_usd": 594, "rating": 4.4},
        ]
    }


def check_policy(question: str) -> dict:
    return {
        "answer": "See travel policy sections 4.2, 6, and 7.1.",
        "policy_doc": "sample-data/travel-policy.md",
    }


def submit_booking(payload: dict = None, **kwargs) -> dict:
    # Accept either submit_booking(payload={...}) or submit_booking(field=val, ...)
    return {"booking_id": f"CT-{random.randint(10000, 99999)}",
            "status": "confirmed-mock"}


TOOL_SCHEMAS = [
    {"type": "function",
     "name": "search_flights",
     "description": "Search business-policy-compliant flights.",
     "parameters": {"type": "object", "properties": {
         "origin": {"type": "string"},
         "dest": {"type": "string"},
         "depart_date": {"type": "string", "description": "YYYY-MM-DD"},
     }, "required": ["origin", "dest", "depart_date"]}},
    {"type": "function",
     "name": "search_hotels",
     "description": "Search hotels in a city for given check-in/out dates.",
     "parameters": {"type": "object", "properties": {
         "city": {"type": "string"},
         "area": {"type": "string"},
         "checkin": {"type": "string"},
         "checkout": {"type": "string"},
     }, "required": ["city", "checkin", "checkout"]}},
    {"type": "function",
     "name": "check_policy",
     "description": "Ask a question against WWI policy.",
     "parameters": {"type": "object", "properties": {
         "question": {"type": "string"},
     }, "required": ["question"]}},
    {"type": "function",
     "name": "submit_booking",
     "description": "Submit a booking. Returns a confirmation id.",
     "parameters": {"type": "object", "properties": {
         "payload": {"type": "object"},
     }, "required": ["payload"]}},
]

DISPATCH = {
    "search_flights": search_flights,
    "search_hotels":  search_hotels,
    "check_policy":   check_policy,
    "submit_booking": submit_booking,
}
