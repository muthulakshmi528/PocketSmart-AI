import json

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
)

from database import get_connection
from models.schemas import (
    HomeRequest,
    JewelryRequest,
    PartyRequest,
)
from routes.session import current_user
from services.gemini_service import (
    recommend_home,
    recommend_jewelry,
    recommend_party,
)


router = APIRouter(
    prefix="/api",
    tags=["Planners"]
)


def save_history(
    request: Request,
    planner: str,
    request_data,
    response_data,
):
    user = current_user(request)

    if not user:
        return

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO recommendation_history
            (
                user_id,
                planner_type,
                request_json,
                response_json
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                user["id"],
                planner,
                json.dumps(
                    request_data,
                    default=str,
                ),
                json.dumps(
                    response_data,
                    default=str,
                ),
            ),
        )

        connection.commit()


@router.post("/generate-home")
async def generate_home(
    payload: HomeRequest,
    request: Request,
):
    result = await recommend_home(
        payload
    )

    save_history(
        request,
        "home",
        payload.model_dump(),
        result,
    )

    return result


@router.post("/generate-party")
async def generate_party(
    payload: PartyRequest,
    request: Request,
):
    result = await recommend_party(
        payload
    )

    save_history(
        request,
        "party",
        payload.model_dump(),
        result,
    )

    return result


@router.post("/generate-jewelry")
async def generate_jewelry(
    request: Request,
    budget: float = Form(...),
    occasion: str = Form(...),
    style: str = Form("Elegant"),
    metal: str = Form("Any"),
    outfit_description: str = Form(""),
    outfit_image: UploadFile | None = File(None),
):
    try:
        payload = JewelryRequest(
            budget=budget,
            occasion=occasion,
            style=style,
            metal=metal,
            outfit_description=outfit_description,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        )

    image_bytes = None
    mime_type = None

    # Image is optional.
    # Only validate it when an actual file was selected.
    if outfit_image and outfit_image.filename:
        allowed_types = {
            "image/jpeg",
            "image/png",
            "image/webp",
        }

        if outfit_image.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Only JPG, PNG, or WEBP "
                    "images are supported."
                ),
            )

        image_bytes = await outfit_image.read()

        if len(image_bytes) > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail=(
                    "Image must be 5 MB or smaller."
                ),
            )

        mime_type = outfit_image.content_type

    result = await recommend_jewelry(
        payload,
        image_bytes,
        mime_type,
    )

    save_history(
        request,
        "jewelry",
        payload.model_dump(),
        result,
    )

    return result
