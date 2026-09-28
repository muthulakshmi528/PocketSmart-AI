from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


router = APIRouter(
    tags=["Pages"]
)


templates = Jinja2Templates(
    directory=(
        Path(__file__)
        .resolve()
        .parents[1]
        / "templates"
    )
)


@router.get(
    "/",
    response_class=HTMLResponse
)
async def home(request: Request):

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request
        }
    )


@router.get(
    "/login",
    response_class=HTMLResponse
)
async def login_page(
    request: Request
):

    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "mode": "login",
        }
    )


@router.get(
    "/register",
    response_class=HTMLResponse
)
async def register_page(
    request: Request
):

    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "mode": "register",
        }
    )


@router.get(
    "/dashboard",
    response_class=HTMLResponse
)
async def dashboard(
    request: Request
):

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request
        }
    )


@router.get(
    "/planner/{planner}",
    response_class=HTMLResponse
)
async def planner(
    request: Request,
    planner: str,
):

    if planner not in {
        "home",
        "party",
        "jewelry",
    }:

        return templates.TemplateResponse(
            "404.html",
            {
                "request": request
            },
            status_code=404,
        )

    return templates.TemplateResponse(
        f"{planner}.html",
        {
            "request": request,
            "planner": planner,
        }
    )