"""FastAPI application instance."""

from __future__ import annotations

from fastapi import FastAPI

app = FastAPI(
    title="ArborDoc",
    description="Structured DOCX parsing and style transformation API.",
    version="0.1.0",
)

from arbordoc.api.routes import router  # noqa: E402

app.include_router(router)
