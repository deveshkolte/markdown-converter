# Markdown Converter API

FastAPI wrapper around the `markdown_converter` Python package. Replaces the Next.js `execFile` pattern with an in-process import — no subprocess overhead.

## Run locally

```bash
# From the project root (~/markdown_converter/)
pip install -r api/requirements.txt
uvicorn api.main:app --reload --port 8000
```

The API is available at `http://localhost:8000`.

- **Health check**: `GET /health` → `{"status": "ok"}`
- **Convert**: `POST /convert` with a `multipart/form-data` file field

## Deploy to Render

1. Push the repo (the `api/` subfolder is part of the `markdown-converter` repo).
2. In the Render dashboard, create a **New Web Service** and connect your repo.
3. Render will auto-detect `render.yaml` in the root. Alternatively, manually configure:
   - **Build Command**: `pip install -r api/requirements.txt`
   - **Start Command**: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path**: `/health`

### Cold starts

The Render free tier spins down after 15 minutes of inactivity. The first request after idle will take 30–60 seconds to cold-start.
