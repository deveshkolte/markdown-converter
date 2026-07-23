import contextlib
import logging
import os
import tempfile
import traceback
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

# Allow all origins (no credentials — frontend sends plain fetch without cookies).
# TODO: Before going live lock down `allow_origins` to the real frontend domain
#       (e.g. ["https://markdown-converter.vercel.app"]).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
        logging.error("Conversion failed:\n%s", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e)) from e
    finally:
        if tmp_path is not None:
            with contextlib.suppress(OSError):
                os.unlink(tmp_path)
