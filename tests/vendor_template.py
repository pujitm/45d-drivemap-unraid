#!/usr/bin/env python3
import ast
import json
import pathlib
import re
import sys


def extract_alias_template(text: str):
    marker = re.search(r"alias_template\s*=\s*{", text)
    if marker is None:
        return None

    start = marker.end() - 1
    depth = 0
    end = None
    for idx in range(start, len(text)):
        ch = text[idx]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = idx + 1
                break

    if end is None:
        return None

    snippet = text[start:end]
    return ast.literal_eval(snippet)


def main():
    if len(sys.argv) != 4:
        print("null")
        return 1

    script_path = pathlib.Path(sys.argv[1])
    style = sys.argv[2]
    chassis = sys.argv[3]

    try:
        text = script_path.read_text(encoding="utf-8")
        template = extract_alias_template(text)
    except Exception:
        print("null")
        return 0

    if not isinstance(template, dict):
        print("null")
        return 0

    value = template.get(style, {}).get(chassis)
    print(json.dumps(value))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
