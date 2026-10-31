"""Proxy and cookie settings that get yt-dlp past YouTube's bot check."""

from conftest import make_settings

from ytscrape.transcribe.youtube.client import YouTubeClient


def test_no_proxy_or_cookies_by_default(tmp_path):
    opts = YouTubeClient(make_settings(tmp_path))._base_opts()
    assert "proxy" not in opts
    assert "cookiefile" not in opts


def test_ytdlp_proxy_wins_over_standard_variables(tmp_path):
    s = make_settings(tmp_path, YTDLP_PROXY="http://a:1", HTTPS_PROXY="http://b:2")
    assert YouTubeClient(s)._base_opts()["proxy"] == "http://a:1"


def test_https_proxy_is_used_when_ytdlp_proxy_unset(tmp_path):
    s = make_settings(tmp_path, HTTPS_PROXY="http://b:2")
    assert s.proxy == "http://b:2"


def test_cookies_pasted_into_a_variable_become_a_private_file(tmp_path):
    s = make_settings(
        tmp_path, YTDLP_COOKIES="# Netscape HTTP Cookie File\n.youtube.com\tTRUE"
    )
    assert s.cookies_file is not None
    assert s.cookies_file.read_text(encoding="utf-8").splitlines() == [
        "# Netscape HTTP Cookie File",
        ".youtube.com\tTRUE",
    ]
    assert YouTubeClient(s)._base_opts()["cookiefile"] == str(s.cookies_file)


def _capture_ytdlp_opts(monkeypatch):
    seen: list[dict] = []

    class FakeYDL:
        def __init__(self, opts):
            seen.append(opts)

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def extract_info(self, url, download):
            return {"id": "_0gtiMi5AzI", "title": "t"}

    monkeypatch.setattr(
        "ytscrape.transcribe.youtube.client.yt_dlp.YoutubeDL", FakeYDL
    )
    return seen


def test_metadata_does_not_fail_when_no_formats_are_returned(tmp_path, monkeypatch):
    from ytscrape.transcribe.youtube.url_parser import parse_video_ref

    seen = _capture_ytdlp_opts(monkeypatch)
    YouTubeClient(make_settings(tmp_path)).fetch_metadata(
        parse_video_ref("_0gtiMi5AzI")
    )
    assert seen[0]["ignore_no_formats_error"] is True


def test_audio_download_still_requires_a_format(tmp_path, monkeypatch):
    from ytscrape.transcribe.youtube.url_parser import parse_video_ref

    seen = _capture_ytdlp_opts(monkeypatch)
    client = YouTubeClient(make_settings(tmp_path))
    client._extract(parse_video_ref("_0gtiMi5AzI"), {"format": "bestaudio"}, True)
    assert "ignore_no_formats_error" not in seen[0]


def test_cookies_file_path_is_used_as_is(tmp_path):
    s = make_settings(tmp_path, YTDLP_COOKIES_FILE="/data/cookies.txt")
    assert str(s.cookies_file).replace("\\", "/") == "/data/cookies.txt"
