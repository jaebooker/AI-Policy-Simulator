"""Inline web/model.js and data/scenarios.json into the web app.

Writes:
  docs/index.html      standalone page (GitHub Pages ready)
  build/artifact.html  same page without the document skeleton
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(*p):
    with open(os.path.join(ROOT, *p)) as f:
        return f.read()


def main():
    app = read("web", "app.html")
    model = read("web", "model.js")
    spec = json.dumps(json.loads(read("data", "scenarios.json")), separators=(",", ":"))
    body = app.replace("/*MODEL*/", model).replace("/*SCENARIOS*/", spec)
    os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
    with open(os.path.join(ROOT, "build", "artifact.html"), "w") as f:
        f.write(body)
    page = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            '<style>body{margin:0}[hidden]{display:none!important}img{max-width:100%}</style>\n</head>\n<body>\n'
            + body + '\n</body>\n</html>\n')
    with open(os.path.join(ROOT, "docs", "index.html"), "w") as f:
        f.write(page)
    print("built docs/index.html and build/artifact.html", len(page), "bytes")


if __name__ == "__main__":
    main()
