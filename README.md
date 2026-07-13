<div align="center">

# Markdown Converter

**Convert documents → Markdown → AI-ready chunks → Semantic search + LLM queries**

*Powered by Microsoft MarkItDown · ChromaDB · OpenRouter*

[![CI](https://github.com/deveshkolte/markdown-converter/actions/workflows/ci.yml/badge.svg)](https://github.com/deveshkolte/markdown-converter/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

</div>

---

## Features

| Capability | Command | Description |
|---|---|---|
| **Convert** | `mdconvert file doc.pdf` | Single document → Markdown |
| **Batch** | `mdconvert folder ./docs` | Entire directory → Markdown files |
| **Pipeline** | `mdconvert pipeline doc.pdf` | Document → Chunks → JSON |
| **Query** | `mdconvert rag doc.pdf "summarize"` | Ask questions about a document |
| **Benchmark** | `mdconvert benchmark ./docs` | Compare sequential vs concurrent speed |

### AI Pipeline (end-to-end)

```
Document ──→ MarkItDown ──→ Markdown ──→ Chunker ──→ Embeddings ──→ Vector DB ──→ LLM
                                                                          │
                                                                     "What does this say?"
```

## Quick Start

```bash
# Install
python3 -m venv venv && source venv/bin/activate
pip install markdown-converter

# Convert a document
mdconvert file resume.pdf

# Run the full AI pipeline
mdconvert pipeline resume.pdf

# Ask questions about a document
mdconvert rag resume.pdf "What are the key skills?"
```

## Installation

### From PyPI (coming soon)

```bash
pip install markdown-converter
```

### From source

```bash
git clone https://github.com/deveshkolte/markdown-converter.git
cd markdown-converter
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev,rag]"
```

## Usage

### Convert a single file

```bash
mdconvert file resume.pdf
mdconvert file notes.docx -o ./output
mdconvert file slides.pptx --overwrite
```

### Convert a folder

```bash
mdconvert folder ./documents
mdconvert folder ./documents -o ./markdown
mdconvert folder ./documents --recursive
```

### AI Preprocessing Pipeline

```bash
# Full pipeline: convert → chunk → embed → save JSON
mdconvert pipeline resume.pdf

# With custom chunking
mdconvert pipeline document.pdf --chunk-size 500 --chunk-overlap 50

# Output path
mdconvert pipeline notes.docx -o ./pipeline-output.json
```

The pipeline outputs structured JSON:

```json
{
  "title": "Resume.pdf",
  "file_type": "pdf",
  "word_count": 482,
  "markdown": "# DEVESH KOLTE\n\n...",
  "chunks": [
    {
      "id": "chunk_0001",
      "text": "DEVESH KOLTE\n\nEducation...",
      "metadata": { "page": 1, "section": "header" },
      "embedding": [0.012, -0.034, ...]
    }
  ]
}
```

### RAG — Ask Questions

```bash
# Requires OPENROUTER_API_KEY environment variable
export OPENROUTER_API_KEY="sk-..."

mdconvert rag resume.pdf "Summarize this document"
mdconvert rag report.docx "What are the key findings?"
mdconvert rag presentation.pptx "List all bullet points"
```

### Benchmark

```bash
mdconvert benchmark ./documents
```

Output:

```
Method           Duration    Speed-up
─────────────────────────────────────
Sequential        12.34s      1.00x
Threaded           4.56s      2.71x
Multiprocess       3.21s      3.84x
```

## Chunking Strategies

| Strategy | Description |
|---|---|
| **Fixed-size** | Split by character count with configurable overlap |
| **Recursive** | Split by paragraphs → sentences → characters (LLM-friendly) |
| **Semantic** | Split by Markdown headings and natural boundaries |

## RAG Architecture

```
┌──────────────┐    ┌─────────────┐    ┌──────────────┐
│  Document    │───→│  MarkItDown  │───→│  Chunker     │
└──────────────┘    └─────────────┘    └──────┬───────┘
                                              │
                                              ▼
┌──────────────┐    ┌─────────────┐    ┌──────────────┐
│  LLM Answer  │←───│  Vector DB  │←───│  Embedder    │
│  (OpenRouter)│    │  (ChromaDB) │    │  (MiniLM-L6) │
└──────────────┘    └─────────────┘    └──────────────┘
```

**Embedding model**: `all-MiniLM-L6-v2` — 384-dimensional, runs locally via ONNX, no GPU needed. Strong for semantic search while being 5× faster than BERT-based models.

**Vector database**: ChromaDB — local, persistent, zero-config. Stores embeddings + metadata + original text.

**LLM**: OpenRouter — unified API for 200+ models. Use any model (GPT-4, Claude, Gemini, Llama) with a single key.

## Project Structure

```
markdown_converter/
├── __init__.py         # Public API exports
├── cli.py              # Argparse CLI with subcommands
├── logger.py           # Singleton logger with level control
├── utils.py            # Path validation, file discovery, output paths
├── converter.py        # MarkItDown wrapper (lazy singleton)
├── models.py           # Document, Chunk, Metadata dataclasses
├── chunking.py         # Fixed, recursive, and semantic chunkers
├── pipeline.py         # End-to-end preprocessing pipeline
├── worker.py           # ThreadPoolExecutor, caching, concurrent processing
├── embeddings.py       # Embedding model wrapper (MiniLM-L6-v2 via ONNX)
├── vectordb.py         # ChromaDB client (local, persistent)
├── llm.py              # OpenRouter API client
├── rag.py              # RAG pipeline orchestrator
└── benchmark.py        # Performance benchmarking
```

## Development

```bash
pip install -e ".[dev,rag]"
pre-commit install
pytest tests/ --cov
ruff check .
```

## Supported Formats

PDF, DOCX, PPTX, XLSX, CSV, HTML, EPUB, images (OCR), audio (transcription),
Jupyter Notebooks, Outlook .msg files, ZIP archives, YouTube transcripts,
Wikipedia articles, RSS feeds.

## Roadmap

- [x] Document → Markdown conversion
- [x] Folder batch processing
- [x] AI preprocessing pipeline (chunking, embeddings, metadata)
- [x] RAG with vector DB and LLM
- [x] Benchmark mode
- [x] CI/CD, linting, pre-commit
- [ ] Desktop UI (PySide6)
- [ ] Web UI (Next.js + FastAPI)
- [ ] Multi-document RAG
- [ ] Streaming responses
- [ ] PDF OCR for scanned documents

## License

MIT © [Devesh Kolte](https://github.com/deveshkolte)
