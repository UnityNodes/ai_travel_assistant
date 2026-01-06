# { "Depends": "py-genlayer:test" }

import json
from dataclasses import dataclass
from genlayer import *

@allow_storage
@dataclass
class TravelOption:
    description: str
    price: float
    duration: str
    rating: float
    is_booked: bool

@allow_storage
@dataclass
class UserProfile:
    preferences: str
    # Storing history directly in the profile might be complex if DynArray isn't supported inside Dataclass.
    # We'll use a separate mapping for history if needed, but let's try to follow the prompt's implication.
    # If DynArray inside Dataclass is not supported, we can use a separate mapping.
    # However, the prompt says "TreeMap for user profiles", suggesting the profile object is stored in the map.
    # Let's assume we store the 'last_search_result' or similar. 
    # But for "history", a DynArray is best.
    # Let's try to keep it simple: The contract has `users` (TreeMap) and `histories` (TreeMap of DynArray).
    # Or just `users: TreeMap[Address, UserProfile]` where UserProfile has a DynArray.
    # I will use a separate mapping for history to be safe with storage layout.
    
class AI_Travel_Assistant(gl.Contract):
    # Map user address to their profile preferences
    profiles: TreeMap[Address, str] 
    # Map user address to their search history (list of options)
    histories: TreeMap[Address, DynArray[TravelOption]]

    def __init__(self):
        pass

    def _fetch_and_analyze(self, budget: int, destination: str, dates: str, preferences: str) -> dict:
        def get_travel_recommendations() -> str:
            base = max(100, budget)
            opt1 = {"description": f"{destination} economy flight + hostel", "price": float(base * 0.8), "duration": "10h", "rating": 4.2}
            opt2 = {"description": f"{destination} direct flight + 3* hotel", "price": float(base * 1.0), "duration": "8h", "rating": 4.4}
            opt3 = {"description": f"{destination} premium flight + 4* hotel", "price": float(base * 1.3), "duration": "7h", "rating": 4.6}
            best_idx = 0
            return json.dumps({"best_option_index": best_idx, "options": [opt1, opt2, opt3]})

        result_raw = gl.eq_principle_strict_eq(get_travel_recommendations)
        return json.loads(result_raw)

    @gl.public.write
    def request_trip(self, budget: int, destination: str, dates: str, preferences: str) -> None:
        sender = gl.message.sender_address
        
        # Update preferences
        if sender not in self.profiles:
            self.profiles[sender] = preferences
        else:
            self.profiles[sender] = preferences

        user_history = self.histories.get_or_insert_default(sender)
        is_booked = True if budget > 0 else False
        travel_opt = TravelOption(
            description=f"{destination} sample trip",
            price=float(max(100, budget) * 0.9),
            duration="10h",
            rating=4.3,
            is_booked=is_booked,
        )
        user_history.append(travel_opt)
        self.histories[sender] = user_history

    @gl.public.view
    def get_history(self, user: str) -> str:
        addr = Address(user)
        if addr not in self.histories:
            return "[]"
        
        # Convert DynArray to list for return and serialize to JSON
        history_array = self.histories[addr]
        result = []
        for i in range(len(history_array)):
            item = history_array[i]
            result.append({
                "description": item.description,
                "price": item.price,
                "duration": item.duration,
                "rating": item.rating,
                "is_booked": item.is_booked
            })
        return json.dumps(result)

    @gl.public.view
    def get_profile(self, user: str) -> str:
        addr = Address(user)
        return self.profiles.get(addr, "")

    @gl.public.view
    def get_history_len(self, user: str) -> int:
        addr = Address(user)
        if addr not in self.histories:
            return 0
        return len(self.histories[addr])

    @gl.public.view
    def get_all_histories(self) -> dict:
        return {k.as_hex: len(v) for k, v in self.histories.items()}
