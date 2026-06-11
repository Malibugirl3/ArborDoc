"""ArborDoc FastAPI endpoints."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, File, Form, UploadFile
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse

from arbordoc.assist.llm import analyse_with_llm
from arbordoc.assist.review import build_assist_review_markdown
from arbordoc.converters.latex import LatexExporter
from arbordoc.core.parser import parse_docx
from arbordoc.core.styler import transform_docx

router = APIRouter()

_TEMPLATES_DIR = Path(__file__).parent / "templates"

TEMPLATE_INFO = {
    "minimal": {"name": "Minimal", "name_zh": "简约风格",
                "desc": "Clean Calibri 11pt", "desc_zh": "简洁 Calibri 11pt"},
    "business": {"name": "Business", "name_zh": "商务报告",
                 "desc": "Arial 10.5pt, report structure", "desc_zh": "Arial 10.5pt，商务结构"},
    "academic": {"name": "Academic", "name_zh": "学术论文",
                 "desc": "Times New Roman 12pt, 1.5 spacing", "desc_zh": "Times New Roman 12pt，1.5 倍行距"},
}


def _rm(path: Path) -> None:
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
        return JSONResponse(status_code=400, content={"error": "Only .docx files are accepted."})
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
    template: UploadFile = File(None),
    template_key: Optional[str] = Form(None),
):
    """Upload a source DOCX and either a template file or a built-in template key."""
    errors: list[str] = []
    if not source.filename or not source.filename.endswith(".docx"):
        errors.append("Source must be a .docx file.")
    if not template and not template_key:
        errors.append("Either template file or template_key is required.")
    if errors:
        return JSONResponse(status_code=400, content={"errors": errors})

    tmp_dir = Path(tempfile.mkdtemp(prefix="arbordoc_transform_"))
    src_path = tmp_dir / "source.docx"
    tpl_path = tmp_dir / "template.docx"
    out_path = tmp_dir / "output.docx"
    src_path.write_bytes(await source.read())

    if template_key:
        builtin = _TEMPLATES_DIR / f"{template_key}.docx"
        if not builtin.is_file():
            return JSONResponse(status_code=400, content={"error": f"Unknown template key: {template_key}"})
        shutil.copy(str(builtin), str(tpl_path))
    else:
        tpl_path.write_bytes(await template.read())

    transform_docx(str(src_path), str(tpl_path), str(out_path))
    if not out_path.is_file():
        _rm(tmp_dir)
        return JSONResponse(status_code=500, content={"error": "Transform did not produce an output file."})
    background_tasks.add_task(_rm, tmp_dir)
    return FileResponse(str(out_path),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=f"styled_{source.filename or 'output'}.docx")


@router.post("/export-latex")
async def export_latex(file: UploadFile = File(...), fragment: bool = Form(False)):
    """Upload a DOCX file and receive its LaTeX export."""
    if not file.filename or not file.filename.endswith(".docx"):
        return JSONResponse(status_code=400, content={"error": "Only .docx files are accepted."})
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = Path(tmp.name)
    try:
        root = parse_docx(tmp_path)
        latex = LatexExporter(standalone=not fragment).export(root)
        return PlainTextResponse(content=latex, media_type="text/plain; charset=utf-8")
    finally:
        tmp_path.unlink(missing_ok=True)


@router.post("/assist/prepare")
async def assist_prepare(
    file: UploadFile = File(...),
    use_llm: bool = Form(False),
    api_key: Optional[str] = Form(None),
):
    """Upload a DOCX and get the assist review + tree data + optional AI analysis."""
    if not file.filename or not file.filename.endswith(".docx"):
        return JSONResponse(status_code=400, content={"error": "Only .docx files are accepted."})
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = Path(tmp.name)
    try:
        tree = parse_docx(tmp_path)
        review_md = build_assist_review_markdown(tree)
        base_json = tree.model_dump()
        result: dict = {"review_md": review_md, "base_tree": base_json}
        if use_llm and api_key:
            try:
                review_md, ai_analysis = analyse_with_llm(tree, api_key=api_key)
                result["review_md"] = review_md
                result["ai_analysis"] = ai_analysis
            except Exception as exc:
                result["llm_error"] = str(exc)
        return JSONResponse(content=result)
    finally:
        tmp_path.unlink(missing_ok=True)


@router.get("/templates")
async def list_templates():
    """List available built-in templates."""
    items = []
    for key, info in TEMPLATE_INFO.items():
        tpl_path = _TEMPLATES_DIR / f"{key}.docx"
        if tpl_path.is_file():
            items.append({"key": key, **info, "size": tpl_path.stat().st_size})
    return JSONResponse(content={"templates": items})


@router.get("/templates/{name}")
async def download_template(name: str):
    """Download a built-in template by key."""
    tpl_path = _TEMPLATES_DIR / f"{name}.docx"
    if not tpl_path.is_file():
        return JSONResponse(status_code=404, content={"error": f"Template '{name}' not found."})
    return FileResponse(str(tpl_path),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=f"{name}.docx")
