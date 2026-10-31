---
description: Caption-first YouTube transcription with a faster-whisper fallback, plus transcript search, chapters and summaries as MCP tools.
---

# Transcription tools (MCP)

The optional `transcribe` extra adds a full transcription pipeline to
`ytscrape-mcp` (it was previously the separate *youtube-transcript-mcp*
server). It is **caption-first**: existing YouTube captions are used when
available, and a local [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
model transcribes the audio when they are not. Every transcript is cached, so
the search, chapter and summary tools work on it without fetching it again.

## Install

```bash
pip install "ytscrape[mcp,transcribe]"
ytscrape-mcp            # the transcription tools register automatically
```

Pass `--no-transcribe` to leave them out even when the extra is installed.

!!! note

    faster-whisper downloads its model on first use (`small` is ~500 MB) and
    transcribing on CPU is slow for long videos. Videos with captions never
    touch the model.

## Tools

| Tool | Purpose |
| ---- | ------- |
| `youtube_transcribe` | Entry point: caption-first transcript, cached. Options: language, model, word timestamps, format (`compact` / `detailed` / `json` / `srt` / `vtt`), `wait` for long jobs. |
| `youtube_get_transcript` | Cached transcript with `start` / `end` slicing and offset pagination. |
| `youtube_get_segment` | An exact interval, e.g. `01:22:15`–`01:27:30`. |
| `youtube_search_transcript` | Literal, regex or fuzzy search with context and `&t=` jump links. |
| `youtube_video_metadata` | Title, channel, duration, caption languages, cached versions, job status. |
| `youtube_list_chapters` | YouTube chapters, description timestamps, or labelled heuristic chapters. |
| `youtube_generate_summary` | Extractive summaries (executive, bullets, key takeaways, chapters, …). |
| `youtube_find_key_moments` | Conclusions, demos and announcements with timestamps. |
| `youtube_extract_topics` | Timestamped topic map. |
| `youtube_compare_transcripts` | Diff two cached versions (e.g. captions vs whisper). |
| `youtube_transcription_status` | Progress of running jobs. |
| `youtube_cancel_transcription` | Cancel a running job. |

The server also exposes the resources `youtube://video/{video_id}/transcript`,
`…/metadata` and `…/chapters`, and the prompts `analyze_youtube_video`,
`research_youtube_video` and `summarize_youtube_video`.

`get_transcript` (plain captions, no cache) stays available next to these tools
for quick one-off reads.

## Configuration

Settings come from environment variables, or a `.env` file in the working
directory. Every value has a default; see
[`.env.example`](https://github.com/rayhanasyraff/ytscrape/blob/main/.env.example)
for the full list. The most useful ones:

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `TRANSCRIPTION_PROVIDER` | `faster-whisper` | `faster-whisper`, `openai-compatible` (any `/audio/transcriptions` API) or `none` (captions only) |
| `WHISPER_MODEL` | `small` | `tiny`, `base`, `small`, `medium`, `large-v3` |
| `DEVICE` / `COMPUTE_TYPE` | `auto` | `cpu` / `cuda`, and `int8` / `float16` / … |
| `PREFER_CAPTIONS` | `true` | Use YouTube captions when available |
| `CACHE_DIR` / `TEMP_DIR` | `./data/cache` / `./data/tmp` | Relative to the working directory |
| `MAX_VIDEO_DURATION` | `14400` | Longest video (seconds) the pipeline accepts |
| `WHISPER_API_BASE_URL` / `WHISPER_API_KEY` | – | For `openai-compatible` |
| `HTTPS_PROXY` / `YTDLP_PROXY` | – | Proxy for YouTube requests (see below) |
| `YTDLP_COOKIES_FILE` / `YTDLP_COOKIES` | – | YouTube cookies for yt-dlp: a cookies.txt path, or its contents |
| `YTDLP_POT_PROVIDER_URL` | – | bgutil PO-token server, e.g. `http://host:4416` (see below) |

## Hosting

On a small cloud instance, set `TRANSCRIPTION_PROVIDER=none` to serve captions
only, or `WHISPER_MODEL=tiny` / `base` with `DEVICE=cpu` and `COMPUTE_TYPE=int8`
to keep memory and CPU use down. Point `CACHE_DIR` at a persistent volume if you
want transcripts to survive redeploys.

## "Sign in to confirm you're not a bot"

YouTube often flags cloud IPs (Railway, Fly, AWS, …), and then every transcript
request fails with `BOT_CHECK`. Two fixes:

- **Proxy (most reliable):** set `HTTPS_PROXY=http://user:pass@host:port`. Both
  ytscrape's own requests and yt-dlp use it. Residential proxies work best.
- **Cookies (free):** export YouTube cookies from a logged-in browser as a
  Netscape `cookies.txt` (e.g. with a "Get cookies.txt" extension), then set
  `YTDLP_COOKIES_FILE` to its path, or paste the contents into `YTDLP_COOKIES`.
  This covers the transcription tools only. Use a throwaway Google account:
  cookies expire, and YouTube can restrict accounts used for automation.
- **PO-token provider (free, no cookies):** run the
  [bgutil server](https://github.com/Brainicism/bgutil-ytdlp-pot-provider)
  (Docker image `brainicism/bgutil-ytdlp-pot-provider`, port 4416) next to the
  app and set `YTDLP_POT_PROVIDER_URL` to it. The `transcribe` extra already
  installs the yt-dlp plugin and a Deno runtime. Often enough on cloud IPs, but
  not guaranteed; combine with a proxy if YouTube still blocks.

## Web UI

The transcript page has a player-synced transcript, search, chapters and
summaries. It shares the cache with the MCP tools.

- **Hosted:** `ytscrape-mcp --transport streamable-http` serves it under
  `/transcribe/` next to `/mcp` (`/` redirects there). Open a video directly by
  appending any YouTube link:

  ```
  https://your-host/transcribe/result?url=https://www.youtube.com/watch?v=VIDEO_ID
  ```

  Links with extra parameters (`&t=`, `&si=`) work as-is; `?v=VIDEO_ID` works
  too. Pass `--no-web` to serve `/mcp` only.
- **Local:** `ytscrape-transcribe-ui` runs the page alone at
  <http://127.0.0.1:8765>.

!!! warning

    The hosted page is public, like `/mcp`: anyone with the URL can start
    transcriptions on your server.
