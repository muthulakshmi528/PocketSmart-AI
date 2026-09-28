from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from database import init_db
from routes.auth import router as auth_router
from routes.pages import router as pages_router
from routes.planners import router as planner_router
from routes.session import router as session_router


BASE_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="PocketSmart AI",
    description="Smart Budget & Recommendation Assistant",
    version="1.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)


app.include_router(pages_router)
app.include_router(auth_router)
app.include_router(planner_router)
app.include_router(session_router)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "PocketSmart AI",
    }


@app.exception_handler(Exception)
async def unhandled_exception(request: Request, exc: Exception):

    if request.url.path.startswith("/api/") or request.method != "GET":
        return JSONResponse(
            status_code=500,
            content={
                "detail": "An unexpected server error occurred."
            },
        )

    return HTMLResponse(
        "Internal server error",
        status_code=500,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )