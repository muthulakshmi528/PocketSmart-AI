import hashlib
import hmac
import secrets
import sqlite3

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from config import SESSION_COOKIE
from database import get_connection
from models.schemas import (
    LoginRequest,
    RegisterRequest,
)


router = APIRouter(
    prefix="/api",
    tags=["Authentication"]
)


def hash_password(password: str) -> str:

    salt = secrets.token_bytes(16)

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt,
        120_000,
    )

    return (
        f"{salt.hex()}${digest.hex()}"
    )


def verify_password(
    password: str,
    stored: str
) -> bool:

    try:

        salt_hex, digest_hex = stored.split(
            "$",
            1
        )

        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            bytes.fromhex(salt_hex),
            120_000,
        )

        return hmac.compare_digest(
            digest.hex(),
            digest_hex,
        )

    except Exception:

        return False


@router.post("/register")
async def register(
    payload: RegisterRequest
):

    try:

        with get_connection() as connection:

            cursor = connection.execute(
                """
                INSERT INTO users
                (name, email, password_hash)
                VALUES (?, ?, ?)
                """,
                (
                    payload.name.strip(),
                    payload.email.lower(),
                    hash_password(
                        payload.password
                    ),
                ),
            )

            connection.commit()

            return {
                "message": "Registration successful",
                "user_id": cursor.lastrowid,
            }

    except sqlite3.IntegrityError:

        raise HTTPException(
            status_code=409,
            detail=(
                "An account with this email "
                "already exists."
            ),
        )


@router.post("/login")
async def login(
    payload: LoginRequest
):

    with get_connection() as connection:

        user = connection.execute(
            """
            SELECT *
            FROM users
            WHERE email = ?
            """,
            (
                payload.email.lower(),
            ),
        ).fetchone()

    if (
        not user
        or not verify_password(
            payload.password,
            user["password_hash"],
        )
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    response = JSONResponse(
        {
            "message": "Login successful",
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
            },
        }
    )

    response.set_cookie(
        key=SESSION_COOKIE,
        value=str(user["id"]),
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
    )

    return response


@router.post("/logout")
async def logout():

    response = JSONResponse(
        {
            "message": "Logged out"
        }
    )

    response.delete_cookie(
        SESSION_COOKIE
    )

    return response