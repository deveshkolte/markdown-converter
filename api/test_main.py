"""Tests for the Markdown Converter API."""

import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent))

from main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_convert_txt(tmp_path: Path):
    txt = tmp_path / "test.txt"
    txt.write_text("Hello, world!")
    with open(txt, "rb") as f:
        response = client.post("/convert", files={"file": ("test.txt", f, "text/plain")})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "markdown" in data
