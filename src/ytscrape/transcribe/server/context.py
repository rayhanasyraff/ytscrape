"""Application wiring: singletons shared by all MCP tools/resources/prompts."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from ytscrape.transcribe.cache.repository import TranscriptRepository
from ytscrape.transcribe.config.settings import Settings
from ytscrape.transcribe.jobs.manager import JobManager
from ytscrape.transcribe.server import INSTRUCTIONS  # noqa: F401  (re-export)
from ytscrape.transcribe.transcription.pipeline import TranscriptionPipeline
from ytscrape.transcribe.utils.logging import setup_logging
from ytscrape.transcribe.youtube.client import YouTubeClient

settings = Settings.from_env()
setup_logging(settings.log_level)

client = YouTubeClient(settings)
repo = TranscriptRepository(settings)
pipeline = TranscriptionPipeline(settings, client, repo)
jobs = JobManager()


class ToolRegistry:
    """Collects tools, resources and prompts declared with the FastMCP-style decorators.

    The tool modules decorate their functions at import time; :func:`register` in
    ``ytscrape.transcribe.server`` then adds everything to ytscrape's MCP server.
    """

    def __init__(self) -> None:
        self.entries: list[tuple[str, tuple, dict, Callable[..., Any]]] = []

    def _collect(self, kind: str, args: tuple, kwargs: dict):
        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self.entries.append((kind, args, kwargs, fn))
            return fn

        return decorator

    def tool(self, *args, **kwargs):
        return self._collect("tool", args, kwargs)

    def resource(self, *args, **kwargs):
        return self._collect("resource", args, kwargs)

    def prompt(self, *args, **kwargs):
        return self._collect("prompt", args, kwargs)


mcp = ToolRegistry()
