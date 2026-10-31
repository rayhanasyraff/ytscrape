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


def test_cookies_file_path_is_used_as_is(tmp_path):
    s = make_settings(tmp_path, YTDLP_COOKIES_FILE="/data/cookies.txt")
    assert str(s.cookies_file).replace("\\", "/") == "/data/cookies.txt"
