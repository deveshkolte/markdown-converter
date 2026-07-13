# Contributing to Markdown Converter

Thank you for considering contributing! This project aims to be a polished open-source tool for document-to-markdown conversion and AI preprocessing.

## Getting Started

1. Fork the repository.
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/markdown-converter.git
   cd markdown-converter
   ```
3. Create a virtual environment and install development dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -e ".[dev,rag]"
   ```
4. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Development Workflow

1. Create a feature branch: `git checkout -b feat/my-feature`
2. Make your changes.
3. Run linting: `ruff check . && black --check .`
4. Run tests: `pytest tests/ --cov`
5. Commit using conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, etc.
6. Push and open a pull request.

## Code Standards

- **Type hints**: All public functions must have type annotations.
- **Docstrings**: Google-style docstrings for all public APIs.
- **Line length**: 100 characters.
- **Formatting**: Black (default) + Ruff for linting.

## Pull Request Guidelines

- Keep PRs focused on a single concern.
- Include tests for new functionality.
- Update the CHANGELOG.md.
- Update documentation if the public API changes.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
