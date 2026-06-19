# ArborDoc

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![CI](https://github.com/Malibugirl3/ArborDoc/actions/workflows/ci.yml/badge.svg)](https://github.com/Malibugirl3/ArborDoc/actions/workflows/ci.yml)

[English](#english) | [中文](#chinese)

---

<a id="english"></a>
## English

### Overview

ArborDoc is a Python toolkit for **structured DOCX parsing** and **format-oriented rebuilding**. It extracts `.docx` files into a logical document tree (`DocTree`), exports them as JSON or LaTeX, and rebuilds content into template-driven `.docx` files.

Key features:

- **Parse** Word documents into a structured, JSON-serializable tree model
- **Rebuild** parsed documents against a template `.docx` (preserve styles, swap content)
- **Export to LaTeX** with support for headings, paragraphs, tables, and inline images
- **Assist pipeline** — human-readable Markdown review + merge gate for LLM-assisted editing (local-first, no API calls by default)
- **Optional REST API** via FastAPI for headless batch processing

### Installation

#### Prerequisites

- **Python** `>=3.9, <4.0`
- **Poetry** (recommended) or **pip**

#### Install via Poetry (recommended)

```bash
# Clone the repository
git clone https://github.com/Malibugirl3/ArborDoc.git && cd ArborDoc

# Install dependencies and the package in editable mode
poetry install

# (Optional) install the server extras for REST API support
poetry install --extras server
```

#### Install via pip (user / system-wide package)

```bash
# Install directly from the source directory
pip install .

# Or in editable (development) mode
pip install -e .

# With server extras
pip install ".[server]"
```

#### Verify installation

```bash
arbordoc --help
```

### Linux Configuration

#### System Dependencies

On a minimal Linux system, ensure the following are installed:

```bash
# Debian / Ubuntu
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git

# RHEL / CentOS / Fedora
sudo dnf install -y python3 python3-pip python3-virtualenv git
```

#### Setup with virtualenv + pip

```bash
# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install ArborDoc
cd ArborDoc
pip install .

# Verify
arbordoc --help
```

#### Setup with Poetry on Linux

```bash
# Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# Ensure ~/.local/bin is on PATH
export PATH="$HOME/.local/bin:$PATH"

# Install ArborDoc
cd ArborDoc
poetry install
poetry run arbordoc --help
```

#### Configuration File (optional)

ArborDoc looks for configuration in these locations (checked in order):

1. `./.arbordoc/config.json` (project-local)
2. `~/.arbordoc/config.json` (user-global)
3. `ARBORDOC_CONFIG` environment variable (custom path)

Example `config.json`:

```json
{
  "llm_enabled_default": false,
  "profiles": {}
}
```

### CLI Usage

#### Parse a DOCX file into JSON

```bash
arbordoc parse -i input.docx -o output.json
```

#### Rebuild a document into a template

```bash
arbordoc transform -i input.docx -t template.docx -o result.docx
```

#### Export to LaTeX

```bash
# Full document (with documentclass / begin / end document)
arbordoc export-latex -i input.docx -o output.tex

# Body fragment only
arbordoc export-latex -i input.docx -o fragment.tex --fragment
```

#### Assist workspace (review + merge gate)

```bash
# Prepare a human-readable review workspace
arbordoc assist prepare -i input.docx -w ./workspace --no-llm

# Apply merge instructions and emit tree.merged.json
arbordoc assist apply -w ./workspace
```

### REST API (optional)

Start the API server:

```bash
# With extras installed
uvicorn arbordoc.api.app:app --host 0.0.0.0 --port 8000

# Or via poetry
poetry run uvicorn arbordoc.api.app:app --host 0.0.0.0 --port 8000
```

The API docs are available at `http://localhost:8000/docs`.

### API Usage (Python)

```python
from arbordoc import parse_docx, transform_docx
from arbordoc.core.tree import write_json

# Parse a document
tree = parse_docx("input.docx")
write_json(tree.root, "output.json")

# Transform a document
transform_docx("input.docx", "template.docx", "result.docx")
```

### Package Layout

```text
src/arbordoc/
  __init__.py      # Public API exports
  cli.py           # CLI entry point
  api/             # Optional FastAPI server
  assist/          # Review + merge pipeline
  converters/      # Format converters (LaTeX, etc.)
  core/            # Parser, extractor, styler, tree model
  models/          # Pydantic schema definitions
  utils/           # Shared utilities
tests/
examples/
```

### Current Scope

- Heading detection based on Word heading styles and outline levels
- Paragraph extraction with preserved body order
- Table capture and basic template reconstruction
- Inline images with optional embedding during rebuild
- Baseline LaTeX export (headings, paragraphs, tables, image TODO markers)
- Assist: Markdown structural review, merge gate, `tree.merged.json`

### License

ArborDoc is released under the [MIT License](LICENSE).

Copyright (c) 2026 Ma PingChuan

### Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

---

<a id="chinese"></a>
## 中文

### 概述

ArborDoc 是一个 Python 工具包，用于 **DOCX 结构化解析** 和 **基于格式的重建**。它将 `.docx` 文件提取为逻辑文档树 (`DocTree`)，可导出为 JSON 或 LaTeX，并将内容重建到模板驱动的 `.docx` 文件中。

核心功能：

- **解析** Word 文档为结构化的、可 JSON 序列化的树模型
- **重建** 将解析后的文档按模板 `.docx` 重建（保留样式，替换内容）
- **导出 LaTeX** 支持标题、段落、表格和内联图片
- **Assist 流水线** — 可读的 Markdown 审阅 + 合并关卡，支持 LLM 辅助编辑（本地优先，默认无 API 调用）
- **可选 REST API** 基于 FastAPI，用于无头批处理

### 安装

#### 环境要求

- **Python** `>=3.9, <4.0`
- **Poetry**（推荐）或 **pip**

#### 通过 Poetry 安装（推荐）

```bash
# 克隆仓库
git clone https://github.com/Malibugirl3/ArborDoc.git && cd ArborDoc

# 安装依赖并以可编辑模式安装包
poetry install

# （可选）安装 server 扩展以支持 REST API
poetry install --extras server
```

#### 通过 pip 安装（用户/系统级包）

```bash
# 从源码目录直接安装
pip install .

# 或以开发模式安装
pip install -e .

# 包含 server 扩展
pip install ".[server]"
```

#### 验证安装

```bash
arbordoc --help
```

### Linux 环境配置

#### 系统依赖

在最小化 Linux 系统上，请确保安装以下依赖：

```bash
# Debian / Ubuntu
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git

# RHEL / CentOS / Fedora
sudo dnf install -y python3 python3-pip python3-virtualenv git
```

#### 使用 virtualenv + pip 配置

```bash
# 创建并激活虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 安装 ArborDoc
cd ArborDoc
pip install .

# 验证
arbordoc --help
```

#### 在 Linux 上使用 Poetry 配置

```bash
# 安装 Poetry（如尚未安装）
curl -sSL https://install.python-poetry.org | python3 -

# 确保 ~/.local/bin 在 PATH 中
export PATH="$HOME/.local/bin:$PATH"

# 安装 ArborDoc
cd ArborDoc
poetry install
poetry run arbordoc --help
```

#### 配置文件（可选）

ArborDoc 按以下顺序查找配置文件：

1. `./.arbordoc/config.json`（项目本地）
2. `~/.arbordoc/config.json`（用户全局）
3. `ARBORDOC_CONFIG` 环境变量（自定义路径）

示例 `config.json`：

```json
{
  "llm_enabled_default": false,
  "profiles": {}
}
```

### CLI 用法

#### 解析 DOCX 文件为 JSON

```bash
arbordoc parse -i input.docx -o output.json
```

#### 按模板重建文档

```bash
arbordoc transform -i input.docx -t template.docx -o result.docx
```

#### 导出为 LaTeX

```bash
# 完整文档（含 documentclass / begin / end document）
arbordoc export-latex -i input.docx -o output.tex

# 仅正文片段
arbordoc export-latex -i input.docx -o fragment.tex --fragment
```

#### Assist 工作区（审阅 + 合并关卡）

```bash
# 准备可读的审阅工作区
arbordoc assist prepare -i input.docx -w ./workspace --no-llm

# 应用合并指令，生成 tree.merged.json
arbordoc assist apply -w ./workspace
```

### REST API（可选）

启动 API 服务：

```bash
# 安装 extras 后
uvicorn arbordoc.api.app:app --host 0.0.0.0 --port 8000

# 或通过 poetry
poetry run uvicorn arbordoc.api.app:app --host 0.0.0.0 --port 8000
```

API 文档可在 `http://localhost:8000/docs` 查看。

### API 用法（Python）

```python
from arbordoc import parse_docx, transform_docx
from arbordoc.core.tree import write_json

# 解析文档
tree = parse_docx("input.docx")
write_json(tree.root, "output.json")

# 转换文档
transform_docx("input.docx", "template.docx", "result.docx")
```

### 包结构

```text
src/arbordoc/
  __init__.py      # 公开 API 导出
  cli.py           # CLI 入口
  api/             # 可选 FastAPI 服务
  assist/          # 审阅 + 合并流水线
  converters/      # 格式转换器（LaTeX 等）
  core/            # 解析器、提取器、样式器、树模型
  models/          # Pydantic 模式定义
  utils/           # 共享工具
tests/
examples/
```

### 当前范围

- 基于 Word 标题样式和大纲级别的标题检测
- 保留正文顺序的段落提取
- 表格捕获与基础模板重建
- 重建时可选嵌入的内联图片
- 基础 LaTeX 导出（标题、段落、表格、图片 TODO 标记）
- Assist：Markdown 结构审阅、合并关卡、`tree.merged.json`

### 许可证

ArborDoc 采用 [MIT 许可证](LICENSE) 发布。

版权所有 (c) 2026 Ma PingChuan

### 贡献

请参阅 [CONTRIBUTING.md](CONTRIBUTING.md) 与 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)。
