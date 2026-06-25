"""FastAPI entry point for Day 3 — JWT Auth."""
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
## Day 3 — JWT Authentication

Full JWT auth flow:
1. `POST /auth/register` — create account
2. `POST /auth/login` — get **access token** (30 min) + **refresh token** (7 days)
3. Add `Authorization: Bearer <access_token>` to protected requests
4. `POST /auth/refresh` — get a new access token (rotates the refresh token)
5. `POST /auth/logout` — blacklist the access token
""",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "message": "Validation failed",
            "errors": [
                {
                    "field":   " → ".join(str(l) for l in e["loc"]),
                    "message": e["msg"],
                    "type":    e["type"],
                }
                for e in exc.errors()
            ],
        },
    )


app.include_router(api_router)


@app.get("/", tags=["Health"])
async def root():
    return {
        "status":  "ok",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs":    "/docs",
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}
