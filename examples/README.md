# ArborDoc Examples

Minimal usage examples for the CLI. Replace `input.docx` and `template.docx` with your own files.

## Parse DOCX to JSON

```bash
arbordoc parse -i input.docx -o output.json
```

## Rebuild with a template

```bash
arbordoc transform -i input.docx -t template.docx -o result.docx
```

## Export to LaTeX

```bash
arbordoc export-latex -i input.docx -o output.tex
```

## Assist workspace (no LLM)

```bash
arbordoc assist prepare -i input.docx -w ./workspace --no-llm
arbordoc assist apply -w ./workspace
```

## Python API

```python
from arbordoc import parse_docx, transform_docx
from arbordoc.core.tree import write_json

tree = parse_docx("input.docx")
write_json(tree.root, "output.json")

transform_docx("input.docx", "template.docx", "result.docx")
```
