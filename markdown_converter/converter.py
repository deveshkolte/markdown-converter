from pathlib import Path

from markitdown import MarkItDown

from .logger import get_logger

_converter: MarkItDown | None = None
logger = get_logger()


def _get_converter() -> MarkItDown:
    global _converter
    if _converter is None:
        logger.debug("Initialising MarkItDown engine")
        _converter = MarkItDown()
    return _converter


def convert(input_path: str | Path) -> str:
    """Convert a document to Markdown and return the text content.

    The file type is automatically detected by MarkItDown based on
    its content (magika) or, as a fallback, its extension.

    Args:
        input_path: Path to the source document (PDF, DOCX, PPTX, …).

    Returns:
        The full Markdown representation of the document.

    Raises:
        FileNotFoundError: If the file does not exist.
        markitdown.FileConversionException: If conversion fails.
    """
    path = Path(input_path)
    logger.info("Converting %s …", path.name)
    md = _get_converter()

    result = md.convert(str(path.resolve()))

    logger.info("Converted %s (%d chars)", path.name, len(result.text_content))
    return result.text_content
