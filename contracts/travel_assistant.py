# { "Depends": "py-genlayer:test" }

import json
from dataclasses import dataclass
from genlayer import *


@allow_storage
@dataclass
class TravelOption:
    destination: str
    description: str
    price: str
    duration: str
    rating: str
    is_booked: bool


class AI_Travel_Assistant(gl.Contract):
    profiles: TreeMap[Address, str]
    histories: TreeMap[Address, DynArray[TravelOption]]

    def __init__(self):
        pass

    @gl.public.write
    def request_trip(
        self, budget: int, destination: str, dates: str, preferences: str
    ) -> None:
        sender = gl.message.sender_address

        self.profiles[sender] = preferences

        def _build_recommendation() -> str:
            # ── Web Fetch 1: destination data from REST Countries ──
            dest_url = (
                f"https://restcountries.com/v3.1/name/{destination}"
                f"?fields=name,capital,region,languages,currencies"
            )
            try:
                dest_response = gl.nondet.web.get(dest_url)
                destination_info = dest_response.body.decode("utf-8")[:300]
            except Exception:
                destination_info = f'{{"name": "{destination}"}}'

            # ── Web Fetch 2: live USD exchange rates ──
            rates_url = "https://open.er-api.com/v6/latest/USD"
            try:
                rates_response = gl.nondet.web.get(rates_url)
                raw = rates_response.body.decode("utf-8")[:200]
                exchange_rates = raw
            except Exception:
                exchange_rates = "{}"

            # ── Non-deterministic AI execution ──
            prompt = f"""Travel planner. Budget ${budget}, destination {destination}, dates {dates}, preferences: {preferences}.
Destination data: {destination_info}
Exchange rates: {exchange_rates}
Generate 3 options (economy/standard/premium) within budget.
Return ONLY JSON: {{"best_option_index": 0, "options": [{{"description": "...", "price": 800, "duration": "8h", "rating": 4.2}}, {{"description": "...", "price": 1100, "duration": "6h", "rating": 4.5}}, {{"description": "...", "price": 1400, "duration": "5h", "rating": 4.8}}]}}"""

            return gl.nondet.exec_prompt(prompt)

        # ── Equivalence principle: comparative consensus ──
        result_raw = gl.eq_principle.prompt_comparative(
            _build_recommendation,
            "Equivalent if both have 3 travel options with economy/standard/premium tiers and prices within budget.",
        )

        # ── Parse AI result and store on-chain ──
        try:
            # Clean up potential markdown or whitespace wrapping
            clean = result_raw.strip()
            # Find the first { and last }
            start = clean.find("{")
            end = clean.rfind("}")
            if start >= 0 and end > start:
                clean = clean[start : end + 1]
            result = json.loads(clean)
            options = result.get("options", [])
            best_idx = result.get("best_option_index", 0)
            if not isinstance(best_idx, int) or best_idx >= len(options):
                best_idx = 0
        except Exception:
            options = []
            best_idx = 0

        user_history = self.histories.get_or_insert_default(sender)

        if options:
            best = options[best_idx]
            travel_opt = TravelOption(
                destination=destination,
                description=str(best.get("description", f"{destination} trip")),
                price=str(best.get("price", budget)),
                duration=str(best.get("duration", "N/A")),
                rating=str(best.get("rating", "4.0")),
                is_booked=False,
            )
        else:
            travel_opt = TravelOption(
                destination=destination,
                description=f"{destination} trip (fallback)",
                price=str(budget),
                duration="N/A",
                rating="4.0",
                is_booked=False,
            )

        user_history.append(travel_opt)
        self.histories[sender] = user_history

    @gl.public.write
    def update_preferences(self, preferences: str) -> None:
        sender = gl.message.sender_address
        self.profiles[sender] = preferences

    @gl.public.view
    def get_history(self, user: str) -> str:
        addr = Address(user)
        if addr not in self.histories:
            return "[]"
        history_array = self.histories[addr]
        result = []
        for i in range(len(history_array)):
            item = history_array[i]
            result.append(
                {
                    "destination": item.destination,
                    "description": item.description,
                    "price": item.price,
                    "duration": item.duration,
                    "rating": item.rating,
                    "is_booked": item.is_booked,
                }
            )
        return json.dumps(result)

    @gl.public.view
    def get_history_len(self, user: str) -> int:
        addr = Address(user)
        if addr not in self.histories:
            return 0
        return len(self.histories[addr])

    @gl.public.view
    def get_profile(self, user: str) -> str:
        addr = Address(user)
        return self.profiles.get(addr, "")

    @gl.public.view
    def get_all_histories(self) -> dict:
        return {k.as_hex: len(v) for k, v in self.histories.items()}
