import os

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.lexers.special import TextLexer
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound
from flask import Flask, abort, send_file, send_from_directory


app = Flask(__name__)

@app.route("/")
def list_rounds():
    o = ""
    for f in sorted(os.listdir("./config/code_guessing/"), key=int):
        o += f'<a href="{f}">round #{f}</a><br>'
    return o

@app.route("/<int:roundnum>/results.txt")
def show_results(roundnum):
    return send_file(f"./config/code_guessing/{roundnum}/results.txt")

@app.route("/<int:roundnum>/<filename>")
def download_round(roundnum, filename):
    return send_from_directory(f"./config/code_guessing/{roundnum}", filename, as_attachment=True, download_name=filename.split(":")[-1])

@app.route("/<int:roundnum>/")
def show_round(roundnum):
    entries = ""
    if not os.path.exists(f"./config/code_guessing/{roundnum}/people"):
        abort(404)
    with open(f"./config/code_guessing/{roundnum}/people") as f:
        people = "".join(f"<li>{name}</li>" for name in f)
    l = os.listdir(f"./config/code_guessing/{roundnum}")
    l.remove("people")
    if "results.txt" in l:
        l.remove("results.txt")
        t = f'<p>note: this round has ended! see the results <a href="results.txt">here</a></p>'
    else:
        t = ""
    if roundnum == 9:
        p = "<p>due to the nature of this round, code previews are disabled. please download the games to experience them.</p>"
    else:
        p = ""
    l.sort()
    formatter = HtmlFormatter(style="monokai")
    for idx, entry in enumerate(l, start=1):
        entries += f'<h2 id="{idx}">entry #{idx} (<a href="/{roundnum}/{entry}">{entry.split(":", 1)[1]}</a>)</h2>'
        try:
            lexer = get_lexer_by_name(entry.split(":", 1)[0].rsplit(".", 1)[-1])
        except ClassNotFound:
            lexer = TextLexer()
        with open(f"./config/code_guessing/{roundnum}/{entry}", encoding="utf-8", errors="replace") as f:
            y = f.read()
        if roundnum != 9:
            entries += highlight(y, lexer, formatter)
    style = formatter.get_style_defs()
    contents = "<br>".join(f'<a href="#{idx}">entry #{idx}</a>' for idx in range(1, len(l)+1))
    o = f"""
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <style>
      .highlight {{
        background-color: #3e3d32;
      }}
      {style}
    </style>
    <title>code guessing #{roundnum}</title>
  </head>
  <body>
    <h1>code guessing, round #{roundnum}</h1>
    <p>all the submissions received this round follow. naturally, they have been randomly shuffled.</p>
    {p}
    <p>the people who submitted solutions are:</p>
    <ul>
        {people}
    </ul>
    {t}
    <h2>"table" of "contents".</h2>
    {contents}
    {entries}
  </body>
</html>
"""
    return o
