"""Base interfaces for future export backends."""

from __future__ import annotations

from abc import ABC, abstractmethod

from arbordoc.models.schema import DocNode


class BaseExporter(ABC):
    """Minimal exporter contract for future format converters."""

    @abstractmethod
    def export(self, root: DocNode) -> str:
        """Render a document tree into the target format."""
