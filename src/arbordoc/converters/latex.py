"""Placeholder for future LaTeX export support."""

from arbordoc.converters.base import BaseExporter
from arbordoc.models.schema import DocNode


class LatexExporter(BaseExporter):
    """Reserved Phase 2 exporter."""

    def export(self, root: DocNode) -> str:
        raise NotImplementedError("LaTeX export is planned for a later phase.")
