# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.2.0] — 2024-07-12

### Added

- AI preprocessing pipeline with Document, Chunk, and Metadata models
- Chunking strategies: fixed-size, recursive, and semantic (header-based)
- Full RAG pipeline: embeddings (all-MiniLM-L6-v2), vector DB (ChromaDB), LLM (OpenRouter)
- Concurrent processing with ThreadPoolExecutor
- Disk-based caching with diskcache
- Benchmark mode comparing sequential vs threaded vs multiprocess
- Professional project infrastructure (CI, pre-commit, linting, coverage)
- Rich terminal output with progress bars and summary tables
- `pipeline` subcommand for end-to-end AI preprocessing
- `rag` subcommand for querying documents with natural language
- `benchmark` subcommand for performance analysis
- This changelog, contributing guide, and issue templates

### Changed

- Refactored CLI to use argparse subcommands
- Updated pyproject.toml with ruff, black, and pytest configuration
- Rewrote README with comprehensive documentation

## [0.1.0] — 2024-07-12

### Added

- Initial release with MarkItDown integration
- Single file and folder conversion
- Output directory and verbosity options
- Backward-compatible CLI
