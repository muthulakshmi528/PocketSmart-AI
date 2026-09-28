from fastapi import APIRouter, HTTPException, Request

from config import SESSION_COOKIE
from database import get_connection


router = APIRouter(
    prefix="/api",
    tags=["Session"]
)


def current_user(request: Request):

    user_id = request.cookies.get(
        SESSION_COOKIE
    )

    if (
        not user_id
        or not user_id.isdigit()
    ):
        return None

    with get_connection() as connection:

        return connection.execute(
            """
            SELECT
                id,
                name,
                email,
                created_at
            FROM users
            WHERE id = ?
            """,
            (int(user_id),),
        ).fetchone()


@router.get("/session-info")
async def session_info(
    request: Request
):

    user = current_user(request)

    return {
        "logged_in": bool(user),
        "user": dict(user)
        if user
        else None,
    }


@router.get("/session-data")
async def session_data(
    request: Request
):

    user = current_user(request)

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Login required.",
        )

    return {
        "user": dict(user),
        "message": "Session is active.",
    }


@router.get("/history")
async def history(
    request: Request
):

    user = current_user(request)

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Login required.",
        )

    import json

    with get_connection() as connection:

        rows = connection.execute(
            """
            SELECT
                id,
                planner_type,
                request_json,
                response_json,
                created_at
            FROM recommendation_history
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT 50
            """,
            (user["id"],),
        ).fetchall()

    result = []

    for row in rows:

        result.append(
            {
                "id": row["id"],
                "planner_type": row[
                    "planner_type"
                ],
                "request": json.loads(
                    row["request_json"]
                ),
                "response": json.loads(
                    row["response_json"]
                ),
                "created_at": row[
                    "created_at"
                ],
            }
        )

    return {
        "history": result
    }