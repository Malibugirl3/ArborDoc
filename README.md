# ArborDoc

ArborDoc is a Python toolkit for structured DOCX parsing and format-oriented rebuilding.

Phase 1 focuses on a minimal, testable workflow:

1. Parse a `.docx` file into a logical document tree.
2. Export the parsed tree as JSON.
3. Rebuild headings and paragraphs into a template-driven `.docx`.

## Installation

```bash
poetry install
```

## CLI

Parse a DOCX file into JSON:

```bash
poetry run arbordoc parse -i input.docx -o output.json
```

Rebuild a parsed document into a template:

```bash
poetry run arbordoc transform -i input.docx -t template.docx -o result.docx
```

## Package Layout

```text
src/arbordoc/
  core/
  converters/
  models/
  utils/
tests/
examples/
```

## Current Scope

The current implementation supports:

- heading detection based on Word heading styles
- paragraph extraction with preserved body order
- basic table capture
- inline image detection and relationship registration
- minimal template reconstruction for headings and paragraphs

More advanced fidelity features such as OMML, complex tables, and LaTeX export are intentionally postponed to later phases.
