"""Tests for the Markdown Converter API."""

import sys
import tempfile
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent))

from main import ALLOWED_EXTENSIONS, MAX_FILE_SIZE, app

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


def test_convert_invalid_extension(tmp_path: Path):
    exe = tmp_path / "test.exe"
    exe.write_text("nonsense")
    with open(exe, "rb") as f:
        response = client.post("/convert", files={"file": ("test.exe", f, "application/octet-stream")})
    assert response.status_code == 400
    data = response.json()
    assert "unsupported" in data["detail"].lower()


def test_convert_oversized_file():
    payload = b"\x00" * (MAX_FILE_SIZE + 1)
    response = client.post(
        "/convert",
        files={"file": ("large.txt", payload, "text/plain")},
    )
    assert response.status_code == 400
    data = response.json()
    assert "too large" in data["detail"].lower()


def test_convert_conversion_failure(monkeypatch, tmp_path):
    import main

    temp_paths = []
    original_ntf = tempfile.NamedTemporaryFile

    def tracking_ntf(*args, **kwargs):
        ntf = original_ntf(*args, **kwargs)
        temp_paths.append(ntf.name)
        return ntf

    monkeypatch.setattr(tempfile, "NamedTemporaryFile", tracking_ntf)

    def failing_convert(path):
        raise RuntimeError("Simulated conversion failure")

    monkeypatch.setattr(main, "convert", failing_convert)

    txt = tmp_path / "test.txt"
    txt.write_text("Hello")
    with open(txt, "rb") as f:
        response = client.post("/convert", files={"file": ("test.txt", f, "text/plain")})

    assert response.status_code == 500
    data = response.json()
    assert "detail" in data
    assert "Simulated conversion failure" in data["detail"]
    assert len(temp_paths) == 1
    assert not Path(temp_paths[0]).exists()
