# FastAPI Backend

Deployed at `https://markdown-converter-0jsu.onrender.com`.

## Local dev

```bash
pip install -r api/requirements.txt
uvicorn api.main:app --reload --port 8000
```

API at `http://localhost:8000`. Swagger UI at `http://localhost:8000/docs`.

## Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/convert` | Upload file → Markdown (multipart/form-data, field: `file`) |

See [root README](/README.md#api) for full API docs.
