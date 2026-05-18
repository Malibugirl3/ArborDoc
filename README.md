# ArborDoc

ArborDoc is a Python toolkit for structured DOCX parsing and format-oriented rebuilding.

Phase 1 focuses on a minimal, testable workflow:

1. Parse a `.docx` file into a logical document tree.
2. Export the parsed tree as JSON.
3. Rebuild content into a template-driven `.docx`.

Phase 1 **assist** (optional, LLM-ready scaffolding):

- `assist prepare` writes **human-readable** `assist_review.md`, baseline `tree.base.json`, and `merge_instructions.json`.
- You may add `tree.proposed.json` (from tooling or a future LLM adapter), flip `merge_instructions.json` to `"tree_source": "proposed"`, then run `assist apply` to emit **`tree.merged.json`**.
- Default behaviour stays **local-only**: no API calls unless you opt in via config and extend the codebase later.

## Installation

```bash
poetry install
```

Or use pip / venv with `PYTHONPATH=src` during development.

## CLI

Parse a DOCX file into JSON:

```bash
poetry run arbordoc parse -i input.docx -o output.json
```

Rebuild a parsed document into a template:

```bash
poetry run arbordoc transform -i input.docx -t template.docx -o result.docx
```

Export a DOCX file to baseline LaTeX:

```bash
poetry run arbordoc export-latex -i input.docx -o output.tex
poetry run arbordoc export-latex -i input.docx -o fragment.tex --fragment
```

Assist workspace (review + merge gate):

```bash
poetry run arbordoc assist prepare -i input.docx -w ./assist_workspace --no-llm
poetry run arbordoc assist apply -w ./assist_workspace
```

Config search paths for defaults (optional): `./.arbordoc/config.json`, `~/.arbordoc/config.json`, or `ARBORDOC_CONFIG`.

Example JSON:

```json
{
  "llm_enabled_default": false,
  "profiles": {}
}
```

## Package Layout

```text
src/arbordoc/
  assist/
  core/
  converters/
  models/
  utils/
tests/
examples/
```

## Current Scope

The current implementation supports:

- extractor/parser separation (`DocBlock` → `DocTree`)
- heading detection based on Word heading styles and outline levels where present
- paragraph extraction with preserved body order
- table capture and basic reconstruction into templates
- inline images with optional embedding during rebuild when source DOCX is available
- baseline LaTeX export (`export-latex`) for headings/paragraphs/tables with image TODO markers
- **assist**: Markdown structural review, `merge_instructions` gate, `tree.merged.json`

More advanced fidelity features such as OMML → LaTeX, merged-cell-perfect tables, and remote template galleries are documented in `计划书` for later phases.
