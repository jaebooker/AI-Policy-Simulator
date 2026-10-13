"""Build the web app from web/app.html, web/model.js and data/scenarios.json.

Writes:
  docs/index.html, docs/model.js, docs/scenarios.js
      Static site for Vercel (see vercel.json) or GitHub Pages.
  build/artifact.html
      Single self-contained file with everything inlined.
"""
import json
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_TAG = "<script>\n/*MODEL*/\n</script>"
SPEC_LINE = "var SPEC = /*SCENARIOS*/;"

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="Will governments coordinate or compete as they build transformative AI? Move policy levers and watch thousands of simulated futures.">
<meta property="og:title" content="AI Policy Simulator">
<meta property="og:description" content="A game-theoretic model of governments coordinating or racing toward AGI, calibrated to October 2026.">
<meta property="og:type" content="website">
<style>body{margin:0}[hidden]{display:none!important}img{max-width:100%}</style>
</head>
<body>
"""
FOOT = "\n</body>\n</html>\n"


def read(*p):
    with open(os.path.join(ROOT, *p)) as f:
        return f.read()


def write(text, *p):
    path = os.path.join(ROOT, *p)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)


def main():
    app = read("web", "app.html")
    model = read("web", "model.js")
    spec = json.dumps(json.loads(read("data", "scenarios.json")), separators=(",", ":"))
    assert MODEL_TAG in app and SPEC_LINE in app, "placeholders missing from web/app.html"

    inline = app.replace(MODEL_TAG, "<script>\n" + model + "\n</script>").replace(SPEC_LINE, "var SPEC = " + spec + ";")
    write(inline, "build", "artifact.html")

    site = app.replace(MODEL_TAG, '<script src="model.js"></script>\n<script src="scenarios.js"></script>')
    site = site.replace(SPEC_LINE, "var SPEC = window.POLICYSIM_SPEC;")
    # Move the leading <title> and font <link> tags into <head>.
    lines = site.split("\n")
    k = 0
    while k < len(lines) and (lines[k].startswith("<title>") or lines[k].startswith("<link ")):
        k += 1
    head = HEAD.replace("</head>", "\n".join(lines[:k]) + "\n</head>")
    write(head + "\n".join(lines[k:]) + FOOT, "docs", "index.html")
    shutil.copyfile(os.path.join(ROOT, "web", "model.js"), os.path.join(ROOT, "docs", "model.js"))
    write("window.POLICYSIM_SPEC = " + spec + ";\n", "docs", "scenarios.js")
    print("built docs/ (index.html, model.js, scenarios.js) and build/artifact.html")


if __name__ == "__main__":
    main()
