"""Bridge script called by Next.js API route to convert documents via markdown_converter.

Usage:
    python3 scripts/convert.py <input_file_path>

Outputs JSON to stdout: {"success": true, "markdown": "..."} or {"success": false, "error": "..."}
"""

import json
import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "No input file provided"}))
        sys.exit(1)

    input_path = Path(sys.argv[1])
    if not input_path.exists():
        print(json.dumps({"success": False, "error": f"File not found: {input_path}"}))
        sys.exit(1)

    try:
        from markdown_converter.converter import convert

        markdown = convert(input_path)
        print(json.dumps({"success": True, "markdown": markdown}))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
