import contextlib
import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from markdown_converter.converter import convert

app = FastAPI(title="Markdown Converter API", version="0.1.0")

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".pptx",
    ".xlsx",
    ".csv",
    ".html",
    ".htm",
    ".epub",
    ".txt",
    ".md",
}

MAX_FILE_SIZE = 50 * 1024 * 1024

origins_str = os.environ.get("ALLOWED_ORIGINS")
# Default to allow all origins for local dev.
# TODO: Lock down to the real frontend domain before going live.
origins = [o.strip() for o in origins_str.split(",") if o.strip()] if origins_str else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/convert")
async def convert_endpoint(file: UploadFile = File(...)):  # noqa: B008
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file type: {ext}."
                f" Supported: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            ),
        )

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum size is 50MB.",
        )

    tmp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(contents)
            tmp_path = tmp.name
        markdown = convert(tmp_path)
        return {"success": True, "markdown": markdown}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    finally:
        if tmp_path is not None:
            with contextlib.suppress(OSError):
                os.unlink(tmp_path)
