# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-06-19

### Added

- Structured DOCX parsing into a JSON-serializable document tree (`DocTree`)
- Template-driven document rebuild (`transform`)
- LaTeX export for headings, paragraphs, tables, and inline images
- Assist pipeline: Markdown review workspace and merge gate
- Optional FastAPI REST API for headless processing
- CLI entry point (`arbordoc`)
