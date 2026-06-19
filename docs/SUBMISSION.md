# ArborDoc 实验报告

**武汉大学开源软件与技术课程 2026（OSSTA）**

---

## 1. 基本信息

| 字段 | 内容 |
|------|------|
| 项目名称 | ArborDoc |
| 作者 | 马平川（Ma PingChuan）、石凯博（Shi Kaibo） |
| 学号 | *（请填写，提交文件夹命名：学号+姓名）* |
| Git 仓库地址 | https://github.com/Malibugirl3/ArborDoc |
| 许可证 | MIT License（见仓库根目录 `LICENSE`） |

---

## 2. 项目概述

ArborDoc 是一个 Python 开源工具包，用于将 Microsoft Word `.docx` 文件**结构化解析**为逻辑文档树（`DocTree`），并支持按模板**重建**文档、**导出 LaTeX**、以及可选的 **REST API** 与 **Assist 审阅流水线**。

### 2.1 核心功能

1. **解析（parse）** — DOCX → JSON 文档树
2. **重建（transform）** — 按模板 DOCX 替换内容、保留样式
3. **LaTeX 导出（export-latex）** — 标题、段落、表格、内联图片
4. **Assist 流水线** — Markdown 审阅 + 合并关卡（本地优先）
5. **REST API**（可选）— FastAPI 无头批处理

### 2.2 技术栈

- Python 3.9+
- python-docx、lxml、Pydantic
- FastAPI / uvicorn（可选 server 扩展）
- pytest（测试）

---

## 3. 项目结构

```text
ArborDoc/
├── LICENSE                 # MIT 许可证
├── README.md               # 项目主文档（中英文）
├── CHANGELOG.md            # 版本变更记录
├── CONTRIBUTING.md         # 贡献指南
├── CODE_OF_CONDUCT.md      # 行为准则
├── pyproject.toml          # Poetry 包配置
├── docs/
│   └── SUBMISSION.md       # 本实验报告
├── examples/
│   └── README.md           # 使用示例
├── src/arbordoc/
│   ├── cli.py              # 命令行入口
│   ├── core/               # 解析器、提取器、样式器、树模型
│   ├── models/             # Pydantic 数据模型
│   ├── converters/         # LaTeX 等格式转换
│   ├── assist/             # 审阅 + 合并流水线
│   └── api/                # 可选 FastAPI 服务
└── tests/                  # 单元测试
```

---

## 4. 安装与运行

### 4.1 环境要求

- Python `>=3.9, <4.0`
- Poetry（推荐）或 pip

### 4.2 安装

```bash
git clone https://github.com/Malibugirl3/ArborDoc.git
cd ArborDoc
poetry install --extras server
```

### 4.3 验证安装

```bash
poetry run arbordoc --help
poetry run pytest
```

### 4.4 基本使用

```bash
# 解析 DOCX 为 JSON
arbordoc parse -i input.docx -o output.json

# 按模板重建
arbordoc transform -i input.docx -t template.docx -o result.docx

# 导出 LaTeX
arbordoc export-latex -i input.docx -o output.tex
```

---

## 5. 开源规范说明

本项目按照 OSSTA 课程要求配置为完整开源仓库：

| 要求 | 落实情况 |
|------|----------|
| 代码可无错误运行 | 提供 CLI、API；CI 自动跑 pytest |
| 注释规范（Doxygen） | 核心模块含 `@file` / `@brief` / `@author` 文档头 |
| 注明作者与课程 | 本文件 + README 顶部 |
| Git 仓库文档完整 | README、CONTRIBUTING、CHANGELOG、examples |
| 许可证合理 | MIT License |
| Git 库地址提交 | https://github.com/Malibugirl3/ArborDoc |

---

## 6. 架构简述

```text
DOCX 文件
   │
   ▼
extractor（提取 DocBlock 线性块）
   │
   ▼
parser（构建 DocTree 逻辑树）
   │
   ├──► JSON 导出
   ├──► styler（按模板重建 DOCX）
   ├──► LatexExporter（导出 .tex）
   └──► Assist pipeline（审阅 + 合并）
```

数据模型定义于 `src/arbordoc/models/schema.py`，与 `python-docx` 底层对象解耦，便于序列化与扩展。

---

## 7. 许可证

Copyright (c) 2026 Ma PingChuan, Shi Kaibo

本项目采用 [MIT License](../LICENSE) 发布。

---

## 8. 口头报告要点（演示建议）

1. 演示 `arbordoc parse` 将 DOCX 转为 JSON
2. 演示 `arbordoc transform` 模板重建效果
3. 展示 GitHub 仓库：README、LICENSE、CI 状态
4. 说明开源协作文件：CONTRIBUTING、Issue/PR 模板
