import re

_SECTION_TITLES = {
    "professional summary",
    "summary",
    "experience",
    "work experience",
    "employment",
    "education",
    "skills",
    "technical skills",
    "projects",
    "certifications",
    "languages",
    "awards",
    "publications",
    "references",
    "interests",
    "profile",
    "objective",
    "career objective",
    "qualifications",
    "achievements",
    "accomplishments",
    "leadership",
    "volunteer",
    "contact",
    "personal",
    "training",
    "coursework",
    "honors",
    "builder track record",
}


def clean_markdown(text: str) -> str:
    lines = text.split("\n")
    result: list[str] = []

    for i, line in enumerate(lines):
        raw = line

        raw = _replace_bullets(raw)

        prev_blank = i == 0 or lines[i - 1].strip() == ""

        raw = _maybe_heading(raw, prev_blank)

        raw = raw.replace("\x0c", "")

        result.append(raw)

    result = _normalize_blank_lines(result)

    return "\n".join(result)


_BULLET_CHARS = "\u2022\u2023\u2043\u25cb\u25cf\u25d8\u25d9" "\u25e6\u25a0\u25aa\u25b6\u25c6\u25d0"


def _replace_bullets(line: str) -> str:
    line = re.sub(r"^(\s*)\(cid:\d+\)\s*", r"\1- ", line)

    line = re.sub(
        rf"^(\s*)[{_BULLET_CHARS}](\s)",
        r"\1-\2",
        line,
    )

    line = re.sub(r"(?<=\S)\s*\(cid:\d+\)\s*", " • ", line)

    line = re.sub(
        rf"(?<=\S)\s*[{_BULLET_CHARS}]\s*",
        " • ",
        line,
    )

    return line


def _maybe_heading(line: str, prev_blank: bool) -> str:
    stripped = line.strip()
    if not stripped:
        return line

    if not prev_blank:
        return line

    if len(stripped) > 80:
        return line

    if stripped.startswith("##") or stripped.startswith("#"):
        return line

    lower = stripped.lower()
    if lower in _SECTION_TITLES:
        return line.replace(stripped, f"## {stripped}", 1)

    return line


def _normalize_blank_lines(lines: list[str]) -> list[str]:
    result: list[str] = []
    prev_empty = False
    for line in lines:
        is_empty = line.strip() == ""
        if is_empty and prev_empty:
            continue
        result.append(line)
        prev_empty = is_empty
    return result
