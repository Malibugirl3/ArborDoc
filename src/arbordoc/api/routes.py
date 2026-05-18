"""ArborDoc FastAPI endpoints."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse, Response

from arbordoc.core.parser import parse_docx
from arbordoc.core.styler import transform_docx

router = APIRouter()


def _rm(path: Path) -> None:
    """Remove a file or directory tree (for use with BackgroundTasks)."""
    if path.is_dir():
        shutil.rmtree(path, ignore_errors=True)
    else:
        path.unlink(missing_ok=True)


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.post("/parse")
async def parse_document(file: UploadFile = File(...)):
    """Upload a DOCX file and receive its JSON document tree."""
    if not file.filename or not file.filename.endswith(".docx"):
        return JSONResponse(
            status_code=400,
            content={"error": "Only .docx files are accepted."},
        )

    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = Path(tmp.name)

    try:
        root = parse_docx(tmp_path)
        return JSONResponse(content=root.model_dump())
    finally:
        tmp_path.unlink(missing_ok=True)


@router.post("/transform")
async def transform_document(
    background_tasks: BackgroundTasks,
    source: UploadFile = File(...),
    template: UploadFile = File(...),
):
    """Upload a source DOCX and a template DOCX, receive a styled output DOCX."""
    errors: list[str] = []
    if not source.filename or not source.filename.endswith(".docx"):
        errors.append("Source must be a .docx file.")
    if not template.filename or not template.filename.endswith(".docx"):
        errors.append("Template must be a .docx file.")
    if errors:
        return JSONResponse(status_code=400, content={"errors": errors})

    tmp_dir = Path(tempfile.mkdtemp(prefix="arbordoc_transform_"))
    src_path = tmp_dir / "source.docx"
    tpl_path = tmp_dir / "template.docx"
    out_path = tmp_dir / "output.docx"

    src_path.write_bytes(await source.read())
    tpl_path.write_bytes(await template.read())

    transform_docx(str(src_path), str(tpl_path), str(out_path))

    if not out_path.is_file():
        _rm(tmp_dir)
        return JSONResponse(
            status_code=500,
            content={"error": "Transform did not produce an output file."},
        )

    background_tasks.add_task(_rm, tmp_dir)

    return FileResponse(
        str(out_path),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=f"styled_{source.filename or 'output'}.docx",
    )
