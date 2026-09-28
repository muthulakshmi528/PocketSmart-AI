"""
Grounded recommendation catalog.

These are provider search links rather than claims
about live inventory or current prices.
"""


CATALOG = [

    # HOME

    {
        "name": "LED Ceiling Light",
        "category": "lighting",
        "platform": "Amazon",
        "price": 1299,
        "keywords": [
            "light",
            "lighting",
            "lamp",
        ],
        "url": (
            "https://www.amazon.in/"
            "s?k=led+ceiling+light"
        ),
    },

    {
        "name": "Decorative Floor Lamp",
        "category": "lighting",
        "platform": "IKEA",
        "price": 2999,
        "keywords": [
            "light",
            "lamp",
        ],
        "url": (
            "https://www.ikea.com/in/en/"
            "search/?q=floor%20lamp"
        ),
    },

    {
        "name": "Ceiling Fan",
        "category": "fan",
        "platform": "Amazon",
        "price": 2399,
        "keywords": [
            "fan",
            "ceiling fan",
        ],
        "url": (
            "https://www.amazon.in/"
            "s?k=ceiling+fan"
        ),
    },

    {
        "name": "Compact Dining Table",
        "category": "furniture",
        "platform": "IKEA",
        "price": 8999,
        "keywords": [
            "dining",
            "table",
        ],
        "url": (
            "https://www.ikea.com/in/en/"
            "search/?q=dining%20table"
        ),
    },

    {
        "name": "Accent Wall Art",
        "category": "decor",
        "platform": "Amazon",
        "price": 1499,
        "keywords": [
            "wall art",
            "decor",
            "art",
        ],
        "url": (
            "https://www.amazon.in/"
            "s?k=wall+art"
        ),
    },

    {
        "name": "Storage Cabinet",
        "category": "storage",
        "platform": "IKEA",
        "price": 6999,
        "keywords": [
            "storage",
            "cabinet",
        ],
        "url": (
            "https://www.ikea.com/in/en/"
            "search/?q=storage%20cabinet"
        ),
    },

    # PARTY

    {
        "name": "Party Catering Search",
        "category": "catering",
        "platform": "Swiggy",
        "price": 250,
        "keywords": [
            "food",
            "catering",
            "catering per person",
        ],
        "url": (
            "https://www.swiggy.com/"
        ),
    },

    {
        "name": "Restaurant & Catering Search",
        "category": "catering",
        "platform": "Zomato",
        "price": 300,
        "keywords": [
            "food",
            "catering",
            "restaurant",
        ],
        "url": (
            "https://www.zomato.com/"
        ),
    },

    {
        "name": "Hotel & Stay Search",
        "category": "venue",
        "platform": "OYO",
        "price": 2500,
        "keywords": [
            "hotel",
            "stay",
            "venue",
        ],
        "url": (
            "https://www.oyorooms.com/"
        ),
    },

    {
        "name": "Party Decoration Kit",
        "category": "decoration",
        "platform": "Amazon",
        "price": 1999,
        "keywords": [
            "decor",
            "decoration",
            "balloon",
        ],
        "url": (
            "https://www.amazon.in/"
            "s?k=party+decoration+kit"
        ),
    },

    # JEWELRY

    {
        "name": "Minimal Gold-Tone Necklace",
        "category": "necklace",
        "platform": "Amazon",
        "price": 999,
        "keywords": [
            "necklace",
            "minimal",
            "elegant",
        ],
        "url": (
            "https://www.amazon.in/"
            "s?k=gold+tone+necklace"
        ),
    },

    {
        "name": "Statement Earrings",
        "category": "earrings",
        "platform": "Flipkart",
        "price": 799,
        "keywords": [
            "earrings",
            "statement",
        ],
        "url": (
            "https://www.flipkart.com/"
            "search?q=statement+earrings"
        ),
    },

    {
        "name": "Classic Bracelet",
        "category": "bracelet",
        "platform": "Amazon",
        "price": 1299,
        "keywords": [
            "bracelet",
            "classic",
        ],
        "url": (
            "https://www.amazon.in/"
            "s?k=classic+bracelet"
        ),
    },

    {
        "name": "Pearl-Style Earrings",
        "category": "earrings",
        "platform": "Flipkart",
        "price": 899,
        "keywords": [
            "earrings",
            "pearl",
            "elegant",
        ],
        "url": (
            "https://www.flipkart.com/"
            "search?q=pearl+earrings"
        ),
    },
]


def search_catalog(
    planner: str,
    terms: list[str],
    max_items: int = 10,
):

    terms = [
        term.lower()
        for term in terms
        if term
    ]

    if planner == "home":

        allowed = {
            "lighting",
            "fan",
            "furniture",
            "decor",
            "storage",
        }

    elif planner == "party":

        allowed = {
            "catering",
            "venue",
            "decoration",
        }

    else:

        allowed = {
            "necklace",
            "earrings",
            "bracelet",
        }

    candidates = [
        item
        for item in CATALOG
        if item["category"] in allowed
    ]

    scored = []

    for item in candidates:

        score = sum(
            1
            for term in terms
            if any(
                term in keyword
                for keyword in item["keywords"]
            )
        )

        scored.append(
            (
                score,
                item,
            )
        )

    scored.sort(
        key=lambda pair: (
            -pair[0],
            pair[1]["price"],
        )
    )

    return [
        item
        for _, item in scored[:max_items]
    ]