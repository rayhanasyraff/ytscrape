"""Register the transcription tools, resources and prompts on an MCP server."""

from __future__ import annotations

from typing import Any

from mcp.types import ToolAnnotations

INSTRUCTIONS = """\
YouTube transcription & research server.

Core flow: youtube_transcribe(url) once per video -> then use youtube_get_transcript /
youtube_search_transcript / youtube_get_segment / youtube_list_chapters on the cached
transcript. Transcription is caption-first: existing YouTube captions are preferred
(fast, free); local faster-whisper is the fallback when captions are missing.

Timestamps appear as [HH:MM:SS]. Long transcripts are chunked; responses include
instructions for fetching the remaining sections. Clickable timestamps use
https://www.youtube.com/watch?v=VIDEO_ID&t=SECONDSs
"""

# Tools that change server state beyond filling the cache.
_MUTATING_TOOLS = {"youtube_cancel_transcription"}


def _annotations(name: str) -> ToolAnnotations:
    mutating = name in _MUTATING_TOOLS
    return ToolAnnotations(
        title=name.removeprefix("youtube_").replace("_", " ").capitalize(),
        read_only_hint=not mutating,
        destructive_hint=False,
        idempotent_hint=not mutating,
        open_world_hint=True,
    )


def register(server: Any) -> None:
    """Add every transcription tool, resource and prompt to ``server``.

    Importing this package's tool modules builds the shared settings, cache and
    pipeline (from environment variables / ``.env``), so call it once per process.
    """
    from ytscrape.transcribe.server import context, prompts, resources, tools  # noqa: F401

    for kind, args, kwargs, fn in context.mcp.entries:
        if kind == "tool":
            kwargs = {"annotations": _annotations(fn.__name__), **kwargs}
        getattr(server, kind)(*args, **kwargs)(fn)
