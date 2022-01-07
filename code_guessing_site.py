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

@app.route("/10/games/<filename>")
def send_game(filename):
    return send_from_directory(f"./config/cg10_soft/", filename)

@app.route("/<int:roundnum>/")
def show_round(roundnum):
    entries = ""
    if not os.path.exists(f"./config/code_guessing/{roundnum}/people"):
        abort(404)
    with open(f"./config/code_guessing/{roundnum}/people") as f:
        people = "".join(f"<li>{name}</li>" for name in f)
    l = os.listdir(f"./config/code_guessing/{roundnum}")
    l.remove("people")
    parsed_results = None
    if "results.txt" in l:
        l.remove("results.txt")
        parsed_results = []
        with open("./config/code_guessing/{roundnum}/result.txt") as f:
            next(f)
            for line in f:
                p = line.strip()
                if not p:
                    break
                parsed_results.append(p.split(": ")[1])
        t = f'<p>note: this round has ended! see the results <a href="results.txt">here</a></p>'
    else:
        t = f"<p>the people who submitted solutions are:</p><ul>{people}</ul>"
    if roundnum == 9:
        p = "<p>due to the nature of this round, code previews are disabled. please download the games to experience them.</p>"
    elif roundnum == 10:
        p = "<p>due to the nature of this round, code previews are disabled. go to the games' pages with your browser to experience them. separate source code links are also provided"
    else:
        p = ""
    l.sort()
    formatter = HtmlFormatter(style="monokai")
    for idx, entry in enumerate(l, start=1):
        if roundnum == 10:
            if idx == 1:
                link = "/10/games/beaste.html"
            elif idx == 2:
                link = "http://180.148.106.119:10701/"
            elif idx == 3:
                link = "/10/games/tetris_trademark_2022.html"
            elif idx == 4:
                link = "/10/games/index.html"
            elif idx == 5:
                link = "/10/games/quickmaths.html"
            elif idx == 6:
                link = "/10/games/xii.html"
            elif idx == 7:
                link = "/10/games/main.html"
            entries += f'<h2 id="{idx}"><a href="{link}">entry #{idx}</a> (source: <a href="/{roundnum}/{entry}">{entry.split(":", 1)[1]}</a>)</h2>'
        else:
            by = " by " + parsed_results[idx-1] if parsed_results else ""
            entries += f'<h2 id="{idx}">entry #{idx} (<a href="/{roundnum}/{entry}">{entry.split(":", 1)[1]}</a>{by})</h2>'
        try:
            lexer = get_lexer_by_name(entry.split(":", 1)[0].rsplit(".", 1)[-1])
        except ClassNotFound:
            lexer = TextLexer()
        with open(f"./config/code_guessing/{roundnum}/{entry}", encoding="utf-8", errors="replace") as f:
            y = f.read()
        if roundnum not in (9, 10):
            entries += highlight(y, lexer, formatter)
    style = formatter.get_style_defs()
    if roundnum not in (9, 10):
        if parsed_results:
            contents = "<br>".join(f'<a href="#{idx}">entry #{idx} by {r}</a>' for idx, r in enumerate(parsed_results, start=1))
        else:
            contents = "<br>".join(f'<a href="#{idx}">entry #{idx}</a>' for idx in range(1, len(l)+1))
    else:
        contents = "(no table. just look down)"
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
    {t}
    <h2>"table" of "contents".</h2>
    {contents}
    {entries}
  </body>
</html>
"""
    return o
