"""
@file app.py
@brief FastAPI application entry point for ArborDoc REST API.

@author Ma PingChuan, Shi Kaibo
@copyright Copyright (c) 2026 Ma PingChuan, Shi Kaibo. SPDX-License-Identifier: MIT
@date 2026
"""

from __future__ import annotations

from fastapi import FastAPI

app = FastAPI(
    title="ArborDoc",
    description="Structured DOCX parsing and style transformation API.",
    version="0.1.0",
)

from arbordoc.api.routes import router  # noqa: E402

app.include_router(router)
