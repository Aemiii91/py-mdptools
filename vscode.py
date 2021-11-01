#!/usr/bin/env python3
import re
from os import path

at_root = lambda filename: path.join(path.dirname(__file__), filename)

with open(at_root("README.md"), encoding="utf-8") as f:
    readme = f.read()

vscode_files_re = (
    r"`\.vscode\/(.*?)\.json`\n+```(?:json|jsonc)\n((?:.|\n)*?)\n```"
)
vscode_files = re.findall(vscode_files_re, readme)

for filename, content in vscode_files:
    with open(
        at_root(f".vscode/{filename}.json"), "w+", encoding="utf-8"
    ) as f:
        f.write(content)
