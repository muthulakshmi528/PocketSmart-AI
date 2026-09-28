from typing import List, Literal

from pydantic import BaseModel, EmailStr, Field


PlannerType = Literal[
    "home",
    "party",
    "jewelry"
]


class RegisterRequest(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=80
    )

    email: EmailStr

    password: str = Field(
        min_length=6,
        max_length=128
    )


class LoginRequest(BaseModel):

    email: EmailStr

    password: str = Field(
        min_length=1,
        max_length=128
    )


class HomeItem(BaseModel):

    category: str = Field(
        min_length=1,
        max_length=80
    )

    quantity: int = Field(
        default=1,
        ge=1,
        le=50
    )


class HomeRequest(BaseModel):

    budget: float = Field(
        gt=0,
        le=10_000_000
    )

    rooms: List[str] = Field(
        min_length=1,
        max_length=10
    )

    style: str = Field(
        default="Modern",
        max_length=80
    )

    items: List[HomeItem] = Field(
        min_length=1,
        max_length=30
    )

    city: str = Field(
        default="Coimbatore",
        max_length=80
    )


class PartyRequest(BaseModel):

    budget: float = Field(
        gt=0,
        le=10_000_000
    )

    guests: int = Field(
        gt=0,
        le=10_000
    )

    event_type: str = Field(
        min_length=2,
        max_length=80
    )

    venue: str = Field(
        default="Home",
        max_length=120
    )

    city: str = Field(
        default="Coimbatore",
        max_length=80
    )

    preferences: str = Field(
        default="",
        max_length=1000
    )


class JewelryRequest(BaseModel):

    budget: float = Field(
        gt=0,
        le=10_000_000
    )

    occasion: str = Field(
        min_length=2,
        max_length=100
    )

    style: str = Field(
        default="Elegant",
        max_length=100
    )

    metal: str = Field(
        default="Any",
        max_length=60
    )

    outfit_description: str = Field(
        default="",
        max_length=1000
    )


class RecommendationItem(BaseModel):

    name: str
    category: str
    platform: str
    price: float
    reason: str
    url: str

    quantity: int = 1

    estimated_total: float


class BudgetAllocation(BaseModel):

    category: str
    amount: float
    percentage: float


class RecommendationResponse(BaseModel):

    planner: PlannerType

    summary: str

    budget: float

    estimated_total: float

    remaining_budget: float

    allocations: List[BudgetAllocation] = []

    recommendations: List[
        RecommendationItem
    ] = []

    ai_notes: List[str] = []

    source_mode: str