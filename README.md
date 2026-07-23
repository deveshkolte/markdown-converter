<div align="center">

# Markdown Converter

**Convert PDF, DOCX, PPTX, XLSX, and more to clean Markdown.**

Engineered for LLM workflows, RAG pipelines, and documentation automation.

[![Live Demo](https://img.shields.io/badge/demo-markitdown--web.vercel.app-blue?style=flat&logo=vercel)](https://markitdown-web.vercel.app)
[![API](https://img.shields.io/badge/API-markdown--converter--0jsu.onrender.com-green?style=flat&logo=render)](https://markdown-converter-0jsu.onrender.com/docs)
[![CI](https://github.com/deveshkolte/markdown-converter/actions/workflows/ci.yml/badge.svg)](https://github.com/deveshkolte/markdown-converter/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

</div>

---

## Live Demo

Try the web app without installing anything:

**→ [markitdown-web.vercel.app](https://markitdown-web.vercel.app)**

Drag-and-drop a document and get clean Markdown in seconds. Powered by the FastAPI backend on Render.

---

## What This Is

Two things in one repo:

| Layer | Stack | Deployed At |
|---|---|---|
| **Python SDK** | MarkItDown + ChromaDB + OpenRouter | `pip install markdown-converter` |
| **Web API** | FastAPI + Uvicorn | [`docs`](https://markdown-converter-0jsu.onrender.com/docs) |
| **Web UI** | Next.js 16 + Tailwind + shadcn/ui | [`markitdown-web.vercel.app`](https://markitdown-web.vercel.app) |

---

## Web UI

A drag-and-drop interface that calls the FastAPI backend:

```
Drop a file ──→ Upload to /convert ──→ FastAPI parses with MarkItDown ──→ Clean Markdown
```

### Supported Formats

| Category | Formats |
|---|---|
| Documents | PDF, DOCX, PPTX, XLSX |
| Web | HTML, EPUB, CSV |
| Code | MD, TXT |

---

## API

**Base URL:** `https://markdown-converter-0jsu.onrender.com`

### Convert a file

```
POST /convert
Content-Type: multipart/form-data

file: <binary>
```

**Example:**

```bash
curl -X POST https://markdown-converter-0jsu.onrender.com/convert \
  -F "file=@resume.pdf"
```

**Response:**

```json
{
  "success": true,
  "markdown": "# Resume\n\n..."
}
```

### Health check

```
GET /health
```

### Interactive docs

Open [the Swagger UI](https://markdown-converter-0jsu.onrender.com/docs) to test endpoints from the browser.

---

## Python SDK

Install from source:

```bash
git clone https://github.com/deveshkolte/markdown-converter.git
cd markdown-converter
python3 -m venv venv && source venv/bin/activate
pip install -e ".[dev,rag]"
```

### CLI Commands

| Command | Description |
|---|---|
| `mdconvert file doc.pdf` | Single document → Markdown |
| `mdconvert folder ./docs` | Entire directory → Markdown files |
| `mdconvert pipeline doc.pdf` | Document → Chunks → JSON |
| `mdconvert rag doc.pdf "summarize"` | Ask questions about a document |
| `mdconvert benchmark ./docs` | Compare sequential vs concurrent speed |

### Examples

```bash
mdconvert file resume.pdf
mdconvert folder ./documents -o ./markdown
mdconvert pipeline document.pdf --chunk-size 500 --chunk-overlap 50
mdconvert rag report.docx "What are the key findings?"
```

### Pipeline Output

```json
{
  "title": "Resume.pdf",
  "markdown": "# DEVESH KOLTE\n\n...",
  "chunks": [
    {
      "id": "chunk_0001",
      "text": "DEVESH KOLTE\n\nEducation...",
      "embedding": [0.012, -0.034, ...]
    }
  ]
}
```

---

## RAG Pipeline

```
Document ──→ MarkItDown ──→ Chunker ──→ Embedder ──→ ChromaDB ──→ LLM (OpenRouter)
```

Components:

| Component | Technology |
|---|---|
| Conversion | Microsoft MarkItDown |
| Chunking | Fixed-size / Recursive / Semantic |
| Embeddings | all-MiniLM-L6-v2 (ONNX, 384-d) |
| Vector DB | ChromaDB (local, persistent) |
| LLM | OpenRouter (200+ models) |

---

## Project Structure

```
markdown_converter/          ← Python package
├── converter.py             MarkItDown wrapper
├── cli.py                  Argparse CLI
├── pipeline.py             Conversion + chunking + embedding pipeline
├── chunking.py             Fixed, recursive, semantic chunkers
├── embeddings.py           MiniLM-L6-v2 via ONNX
├── vectordb.py             ChromaDB client
├── llm.py                  OpenRouter API client
├── rag.py                  RAG orchestrator
├── worker.py               Concurrent processing
└── benchmark.py            Performance benchmarks

api/                         ← FastAPI service
├── main.py
└── requirements.txt

frontend/                    ← Next.js web UI
├── app/
├── components/
└── vercel.json
```

---

## Development

```bash
pip install -e ".[dev,rag]"
pre-commit install
pytest tests/ --cov
ruff check .
```

---

## Roadmap

- [x] Document → Markdown conversion (CLI)
- [x] Folder batch processing
- [x] AI preprocessing pipeline (chunking, embeddings, metadata)
- [x] RAG with vector DB and LLM
- [x] Benchmark mode
- [x] CI/CD, linting, pre-commit
- [x] **Web API (FastAPI)**
- [x] **Web UI (Next.js)**
- [ ] Desktop UI (PySide6)
- [ ] Multi-document RAG
- [ ] Streaming responses
- [ ] PDF OCR for scanned documents

---

## License

MIT © [Devesh Kolte](https://github.com/deveshkolte)
