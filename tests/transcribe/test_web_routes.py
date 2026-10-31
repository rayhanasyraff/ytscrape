"""The transcript web UI served next to /mcp by ``ytscrape-mcp``."""

import pytest
from mcp.server import MCPServer
from starlette.testclient import TestClient

from ytscrape.mcp_server import http_app
from ytscrape.transcribe.server import register


@pytest.fixture(scope="module")
def client():
    server = MCPServer("test")
    register(server)
    with TestClient(http_app(server)) as c:
        yield c


def test_root_redirects_to_web_ui(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/transcribe/"


def test_result_page_takes_a_full_youtube_link(client):
    response = client.get(
        "/transcribe/result?url=https://www.youtube.com/watch?v=_0gtiMi5AzI&t=42"
    )
    assert response.status_code == 200
    assert 'src="static/app.js"' in response.text


def test_relative_assets_and_api_resolve_under_prefix(client):
    assert client.get("/transcribe/static/app.js").status_code == 200
    assert client.get("/transcribe/api/health").json()["ok"] is True


def test_mcp_endpoint_still_mounted(client):
    assert any(getattr(route, "path", None) == "/mcp" for route in client.app.routes)
