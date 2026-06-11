"""FastAPI application instance."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(
    title="ArborDoc",
    description="Structured DOCX parsing and style transformation API.",
    version="0.1.0",
)

from arbordoc.api.routes import router  # noqa: E402

app.include_router(router)

_DEMO_PATH = Path(__file__).parent / "static" / "index.html"


@app.get("/demo", response_class=HTMLResponse, include_in_schema=False)
@app.get("/demo/", response_class=HTMLResponse, include_in_schema=False)
async def demo_page():
    if not _DEMO_PATH.is_file():
        return HTMLResponse("<h1>Demo page not found</h1>", status_code=404)
    return HTMLResponse(_DEMO_PATH.read_text(encoding="utf-8"))
