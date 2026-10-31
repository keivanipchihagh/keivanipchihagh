#!/usr/bin/env python3
"""Generate the light and dark terminal-style profile cards."""

import json
import os
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

USERNAME = "keivanipchihagh"
ROOT = Path(__file__).resolve().parent.parent

FONT_SIZE = 14
LINE_HEIGHT = 18
CHAR_WIDTH = 8.45
ART_X = 20
INFO_X = 420
INFO_COLS = 66
TOP = 30

THEMES = {
    "dark": {"bg": "#0d1117", "text": "#c9d1d9", "key": "#ffa657", "value": "#a5d6ff", "dots": "#484f58"},
    "light": {"bg": "#f6f8fa", "text": "#24292f", "key": "#953800", "value": "#0a3069", "dots": "#afb8c1"},
}

ABOUT = [
    ("Role", "AI/ML Engineer"),
    ("Studying", "M.Sc. Computer Science, University of Bonn"),
    ("Experience", "4+ years of ML in production"),
    ("Looking For", "Working student role in AI/ML, Bonn"),
    None,
    ("Languages.Code", "Python, Go, C/C++, SQL, Java"),
    ("Languages.Human", "Persian, English (C1), German (A2)"),
    None,
    ("Skills.LLM", "LangGraph, LangSmith, Ragas, RAG"),
    ("Skills.ML", "PyTorch, TensorFlow, Transformers, RecSys"),
    ("Skills.Infra", "Docker, Kubernetes, Airflow, FastAPI, PostgreSQL"),
]

CONTACT = [
    ("Email", "keivanipchihagh@gmail.com"),
    ("Website", "keivanipchihagh.com"),
    ("LinkedIn", "in/keivanipchihagh"),
    ("Medium", "@keivanipchihagh"),
]


def fetch(path):
    request = urllib.request.Request(f"https://api.github.com/{path}")
    request.add_header("Accept", "application/vnd.github+json")
    request.add_header("User-Agent", USERNAME)
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def fetch_stats():
    user = fetch(f"users/{USERNAME}")
    commits = fetch(f"search/commits?q=author:{USERNAME}&per_page=1")["total_count"]

    stars = 0
    page = 1
    while True:
        repos = fetch(f"users/{USERNAME}/repos?per_page=100&page={page}")
        stars += sum(repo["stargazers_count"] for repo in repos if not repo["fork"])
        if len(repos) < 100:
            break
        page += 1

    return [
        ("Repos", f"{user['public_repos']:,}"),
        ("Stars", f"{stars:,}"),
        ("Commits", f"{commits:,}"),
        ("Followers", f"{user['followers']:,}"),
    ]


def row(key, value):
    dots = "." * max(1, INFO_COLS - len(key) - len(value) - 5)
    parts = "</tspan>.<tspan class='key'>".join(escape(part) for part in key.split("."))
    return (
        f"<tspan class='dots'>. </tspan><tspan class='key'>{parts}</tspan>:"
        f"<tspan class='dots'> {dots} </tspan><tspan class='value'>{escape(value)}</tspan>"
    )


def header(title):
    return f"{escape(title)} " + "-" * (INFO_COLS - len(title) - 1)


def info_lines(stats):
    rows = [header(f"{USERNAME}@github")]
    rows += ["" if item is None else row(*item) for item in ABOUT]
    rows += ["", header("- Contact")]
    rows += [row(*item) for item in CONTACT]
    rows += ["", header("- GitHub Stats")]
    rows += [row(*item) for item in stats]
    return rows


def text_block(lines, x, css_class):
    tspans = []
    for index, line in enumerate(lines):
        if line:
            tspans.append(f"<tspan x='{x}' y='{TOP + index * LINE_HEIGHT}'>{line}</tspan>")
    return f"<text class='{css_class}' xml:space='preserve'>{''.join(tspans)}</text>"


def render(theme, stats):
    colors = THEMES[theme]
    art = (ROOT / "assets" / f"ascii-{theme}.txt").read_text().splitlines()
    info = info_lines(stats)

    rows = max(len(art), len(info))
    width = round(INFO_X + INFO_COLS * CHAR_WIDTH + 20)
    height = TOP + rows * LINE_HEIGHT

    return f"""<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}' viewBox='0 0 {width} {height}' font-family='Consolas,Menlo,Monaco,monospace' font-size='{FONT_SIZE}'>
<style>
text {{ fill: {colors['text']}; white-space: pre; }}
.key {{ fill: {colors['key']}; }}
.value {{ fill: {colors['value']}; }}
.dots {{ fill: {colors['dots']}; }}
</style>
<rect width='100%' height='100%' rx='10' fill='{colors['bg']}'/>
{text_block([escape(line) for line in art], ART_X, 'art')}
{text_block(info, INFO_X, 'info')}
</svg>
"""


def main():
    stats = fetch_stats()
    for theme in THEMES:
        (ROOT / "assets" / f"profile-{theme}.svg").write_text(render(theme, stats))


if __name__ == "__main__":
    main()
