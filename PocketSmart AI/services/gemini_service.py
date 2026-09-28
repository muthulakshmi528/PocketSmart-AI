import json
import time
from typing import Optional

from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
)
from services.catalog import search_catalog


_client = None


# ============================================================
# GEMINI STRUCTURED RESPONSE MODELS
# ============================================================

class Recommendation(BaseModel):
    name: str
    category: str = "general"
    platform: str = ""
    price: float = 0
    reason: str = ""
    url: str = ""
    quantity: int = 1
    estimated_total: float = 0


class Allocation(BaseModel):
    category: str
    amount: float
    percentage: float


class GeminiPlannerResponse(BaseModel):
    summary: str
    allocations: list[Allocation] = Field(
        default_factory=list
    )
    recommendations: list[Recommendation] = Field(
        default_factory=list
    )
    ai_notes: list[str] = Field(
        default_factory=list
    )


# ============================================================
# GEMINI CLIENT
# ============================================================

def get_client():

    global _client

    if (
        _client is None
        and GEMINI_API_KEY
    ):

        _client = genai.Client(
            api_key=GEMINI_API_KEY
        )

    return _client


# ============================================================
# GEMINI GENERATION WITH RETRY
# ============================================================

def generate_with_gemini(
    prompt: str,
    image_bytes: Optional[bytes] = None,
    mime_type: Optional[str] = None,
):

    client = get_client()

    if not client:

        print(
            "GEMINI ERROR: Client not created. "
            "Check GEMINI_API_KEY."
        )

        return None

    contents = [
        prompt
    ]

    if image_bytes:

        contents.append(
            types.Part.from_bytes(
                data=image_bytes,
                mime_type=(
                    mime_type
                    or "image/jpeg"
                ),
            )
        )

    max_attempts = 3

    for attempt in range(
        1,
        max_attempts + 1,
    ):

        try:

            response = (
                client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=contents,
                    config=(
                        types.GenerateContentConfig(
                            temperature=0.2,
                            max_output_tokens=2500,
                            response_mime_type=(
                                "application/json"
                            ),
                            response_schema=(
                                GeminiPlannerResponse
                            ),
                        )
                    ),
                )
            )

            if not response.text:

                print(
                    "GEMINI ERROR: Empty response."
                )

                return None

            print(
                "GEMINI RESPONSE RECEIVED"
            )

            result = (
                GeminiPlannerResponse
                .model_validate_json(
                    response.text
                )
            )

            return result.model_dump()

        except Exception as exc:

            error_text = str(exc)

            print(
                f"GEMINI ATTEMPT "
                f"{attempt}/{max_attempts} ERROR:",
                repr(exc),
            )

            is_temporary_error = (
                "503" in error_text
                or "UNAVAILABLE" in error_text
                or "high demand"
                in error_text.lower()
            )

            if (
                is_temporary_error
                and attempt < max_attempts
            ):

                wait_seconds = 3 * attempt

                print(
                    "Gemini temporarily "
                    "unavailable. Retrying "
                    f"in {wait_seconds} seconds..."
                )

                time.sleep(
                    wait_seconds
                )

                continue

            return None

    print(
        "GEMINI ERROR: All retry attempts failed."
    )

    return None


# ============================================================
# HOME PLANNER PROMPT
# ============================================================

def build_home_prompt(
    data,
    catalog,
):

    return f"""
You are PocketSmart AI,
a smart budget planning assistant.

Return ONLY valid JSON matching
the provided response schema.

User budget:
INR {data.budget:.2f}

Rooms:
{", ".join(data.rooms)}

Style:
{data.style}

City:
{data.city}

Requested items:
{json.dumps(
    [
        item.model_dump()
        for item in data.items
    ]
)}

Grounding catalog:
{json.dumps(catalog)}

Rules:

1. Keep estimated spending within
the user's budget.

2. Prefer the supplied catalog.

3. Never invent product prices.

4. Never invent product URLs.

5. Every recommendation should contain:
name
category
platform
price
reason
url
quantity
estimated_total

6. Allocations should contain:
category
amount
percentage

7. Do not claim live availability.

8. Use only products and prices
from the supplied catalog.

9. If there are not enough suitable
catalog products, return fewer
recommendations instead of inventing
products.

10. Keep the response concise.
"""


# ============================================================
# PARTY PLANNER PROMPT
# ============================================================

def build_party_prompt(
    data,
    catalog,
):

    return f"""
You are PocketSmart AI,
a party budget planner.

Return ONLY valid JSON matching
the provided response schema.

Budget:
INR {data.budget:.2f}

Guests:
{data.guests}

Event:
{data.event_type}

Venue:
{data.venue}

City:
{data.city}

Preferences:
{data.preferences}

Grounding catalog:
{json.dumps(catalog)}

Allocate spending across:

catering
venue
decoration
contingency

Rules:

1. Stay within the supplied budget.

2. Use only catalog prices.

3. Use only catalog URLs.

4. Never invent prices.

5. Never invent URLs.

6. Never claim live inventory.

7. If suitable products are not
available in the catalog, return
fewer recommendations.

8. Every recommendation should contain:
name
category
platform
price
reason
url
quantity
estimated_total.
"""


# ============================================================
# JEWELRY PLANNER PROMPT
# ============================================================

def build_jewelry_prompt(
    data,
    catalog,
    has_image: bool,
):

    return f"""
You are PocketSmart AI,
a jewelry recommendation assistant.

Return ONLY valid JSON matching
the provided response schema.

Budget:
INR {data.budget:.2f}

Occasion:
{data.occasion}

Style:
{data.style}

Metal:
{data.metal}

Outfit description:
{data.outfit_description}

Outfit image attached:
{"YES" if has_image else "NO"}

Grounding catalog:
{json.dumps(catalog)}

Rules:

1. Stay within the user's budget.

2. Use only supplied catalog
prices and URLs.

3. Never invent product prices.

4. Never invent product URLs.

5. If an image is attached,
discuss only general color and
style coordination.

6. Do not identify the person.

7. Do not make claims about
identity or personal attributes.

8. Never claim live inventory.

9. If suitable products are not
available in the catalog, return
fewer recommendations.

10. Every recommendation should contain:
name
category
platform
price
reason
url
quantity
estimated_total.
"""


# ============================================================
# NORMALIZE GEMINI RESULT
# ============================================================

def _normalize(
    result,
    planner,
    budget,
):

    result = result or {}

    recommendations = result.get(
        "recommendations",
        [],
    )

    allocations = result.get(
        "allocations",
        [],
    )

    clean_recommendations = []

    for item in recommendations:

        try:

            price = float(
                item.get(
                    "price",
                    0,
                )
            )

            quantity = max(
                1,
                int(
                    item.get(
                        "quantity",
                        1,
                    )
                ),
            )

            clean_recommendations.append(
                {
                    "name": str(
                        item.get(
                            "name",
                            "Product",
                        )
                    ),
                    "category": str(
                        item.get(
                            "category",
                            "general",
                        )
                    ),
                    "platform": str(
                        item.get(
                            "platform",
                            "",
                        )
                    ),
                    "price": price,
                    "reason": str(
                        item.get(
                            "reason",
                            "Fits your budget "
                            "and preferences.",
                        )
                    ),
                    "url": str(
                        item.get(
                            "url",
                            "",
                        )
                    ),
                    "quantity": quantity,
                    "estimated_total": (
                        price * quantity
                    ),
                }
            )

        except (
            KeyError,
            ValueError,
            TypeError,
        ):

            continue

    total = sum(
        item["estimated_total"]
        for item in clean_recommendations
    )

    return {
        "planner": planner,

        "summary": str(
            result.get(
                "summary",
                "Recommendations prepared "
                "from your budget and preferences.",
            )
        ),

        "budget": budget,

        "estimated_total": round(
            total,
            2,
        ),

        "remaining_budget": round(
            budget - total,
            2,
        ),

        "allocations": allocations,

        "recommendations": (
            clean_recommendations
        ),

        "ai_notes": [
            str(note)
            for note in result.get(
                "ai_notes",
                [],
            )
        ][:8],

        "source_mode": "gemini",
    }


# ============================================================
# FALLBACK HOME
# ============================================================

def fallback_home(data):

    terms = [
        item.category
        for item in data.items
    ]

    catalog = search_catalog(
        "home",
        terms,
    )

    recommendations = []

    remaining = data.budget

    for requested in data.items:

        matches = [
            item
            for item in catalog
            if any(
                keyword
                in requested.category.lower()
                for keyword in item["keywords"]
            )
        ]

        item = (
            matches[0]
            if matches
            else catalog[0]
        )

        quantity = requested.quantity

        total = (
            item["price"]
            * quantity
        )

        if total <= remaining:

            recommendations.append(
                {
                    **item,
                    "reason": (
                        f"Selected for your "
                        f"{data.style} style and "
                        f"requested category."
                    ),
                    "quantity": quantity,
                    "estimated_total": total,
                }
            )

            remaining -= total

    return _normalize(
        {
            "summary": (
                "Fallback recommendations "
                "were selected from the "
                "built-in catalog."
            ),

            "recommendations": (
                recommendations
            ),

            "allocations": [
                {
                    "category": "Home items",
                    "amount": round(
                        data.budget
                        - remaining,
                        2,
                    ),
                    "percentage": round(
                        (
                            (
                                data.budget
                                - remaining
                            )
                            / data.budget
                        )
                        * 100,
                        2,
                    )
                    if data.budget
                    else 0,
                }
            ],

            "ai_notes": [
                "Connect GEMINI_API_KEY "
                "for AI-personalized reasoning."
            ],
        },
        "home",
        data.budget,
    )


# ============================================================
# FALLBACK PARTY
# ============================================================

def fallback_party(data):

    catalog = search_catalog(
        "party",
        [
            data.event_type,
            data.preferences,
        ],
    )

    recommendations = []

    for item in catalog[:3]:

        quantity = (
            data.guests
            if item["category"]
            == "catering"
            else 1
        )

        total = (
            item["price"]
            * quantity
        )

        if total <= data.budget:

            recommendations.append(
                {
                    **item,
                    "reason": (
                        f"Fits the "
                        f"{data.event_type} "
                        "planning scenario."
                    ),
                    "quantity": quantity,
                    "estimated_total": total,
                }
            )

    return _normalize(
        {
            "summary": (
                "Fallback party options "
                "were selected from the "
                "built-in catalog."
            ),

            "recommendations": (
                recommendations
            ),

            "allocations": [
                {
                    "category": "Catering",
                    "amount": (
                        data.budget * 0.50
                    ),
                    "percentage": 50,
                },
                {
                    "category": "Decoration",
                    "amount": (
                        data.budget * 0.20
                    ),
                    "percentage": 20,
                },
                {
                    "category": "Venue",
                    "amount": (
                        data.budget * 0.20
                    ),
                    "percentage": 20,
                },
                {
                    "category": "Contingency",
                    "amount": (
                        data.budget * 0.10
                    ),
                    "percentage": 10,
                },
            ],

            "ai_notes": [
                "Catering quantity is estimated. "
                "Verify vendor pricing before purchase."
            ],
        },
        "party",
        data.budget,
    )


# ============================================================
# FALLBACK JEWELRY
# ============================================================

def fallback_jewelry(data):

    terms = [
        data.style,
        data.metal,
        data.occasion,
    ]

    catalog = search_catalog(
        "jewelry",
        terms,
    )

    recommendations = []

    remaining = data.budget

    for item in catalog:

        if item["price"] <= remaining:

            recommendations.append(
                {
                    **item,
                    "reason": (
                        f"Matches the requested "
                        f"{data.style.lower()} style "
                        f"for the "
                        f"{data.occasion.lower()} "
                        "occasion."
                    ),
                    "quantity": 1,
                    "estimated_total": (
                        item["price"]
                    ),
                }
            )

            remaining -= item["price"]

        if len(recommendations) == 4:
            break

    return _normalize(
        {
            "summary": (
                "Fallback jewelry options "
                "were selected from the "
                "built-in catalog."
            ),

            "recommendations": (
                recommendations
            ),

            "allocations": [
                {
                    "category": "Jewelry",
                    "amount": (
                        data.budget
                        - remaining
                    ),
                    "percentage": round(
                        (
                            (
                                data.budget
                                - remaining
                            )
                            / data.budget
                        )
                        * 100,
                        2,
                    )
                    if data.budget
                    else 0,
                }
            ],

            "ai_notes": [
                "For image-aware recommendations, "
                "connect GEMINI_API_KEY."
            ],
        },
        "jewelry",
        data.budget,
    )


# ============================================================
# HOME RECOMMENDATION
# ============================================================

async def recommend_home(data):

    catalog = search_catalog(
        "home",
        [
            item.category
            for item in data.items
        ],
    )

    try:

        result = generate_with_gemini(
            build_home_prompt(
                data,
                catalog,
            )
        )

        if result:

            return _normalize(
                result,
                "home",
                data.budget,
            )

        print(
            "GEMINI HOME: Using fallback."
        )

        return fallback_home(data)

    except Exception as exc:

        print(
            "GEMINI HOME ERROR:",
            repr(exc),
        )

        return fallback_home(data)


# ============================================================
# PARTY RECOMMENDATION
# ============================================================

async def recommend_party(data):

    catalog = search_catalog(
        "party",
        [
            data.event_type,
            data.preferences,
        ],
    )

    try:

        result = generate_with_gemini(
            build_party_prompt(
                data,
                catalog,
            )
        )

        if result:

            return _normalize(
                result,
                "party",
                data.budget,
            )

        print(
            "GEMINI PARTY: Using fallback."
        )

        return fallback_party(data)

    except Exception as exc:

        print(
            "GEMINI PARTY ERROR:",
            repr(exc),
        )

        return fallback_party(data)


# ============================================================
# JEWELRY RECOMMENDATION
# ============================================================

async def recommend_jewelry(
    data,
    image_bytes=None,
    mime_type=None,
):

    catalog = search_catalog(
        "jewelry",
        [
            data.style,
            data.metal,
            data.occasion,
        ],
    )

    try:

        result = generate_with_gemini(
            build_jewelry_prompt(
                data,
                catalog,
                bool(image_bytes),
            ),
            image_bytes=image_bytes,
            mime_type=mime_type,
        )

        if result:

            return _normalize(
                result,
                "jewelry",
                data.budget,
            )

        print(
            "GEMINI JEWELRY: Using fallback."
        )

        return fallback_jewelry(data)

    except Exception as exc:

        print(
            "GEMINI JEWELRY ERROR:",
            repr(exc),
        )

        return fallback_jewelry(data)
