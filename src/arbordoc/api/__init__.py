"""FastAPI application for ArborDoc document processing."""

from arbordoc.api.app import app
from arbordoc.api.routes import router

__all__ = ["app", "router"]
