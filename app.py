from flask import Flask, render_template, request, redirect, url_for, session
import random
from data import QUOTES

app = Flask(__name__)
app.secret_key = "supersecretkey"

@app.route("/", methods=["GET", "POST"])
def index():
    if "score" not in session:
        session["score"] = 0
    if "quote" not in session:
        session["quote"] = random.choice(QUOTES)

    if request.method == "POST":
        case = request.form.get("case")
        use = request.form.get("use")

        correct_case = session["quote"]["case"]
        correct_use = session["quote"]["use"]

        if case == correct_case and use == correct_use:
            session["score"] += 10
            result = "Correct!"
        else:
            session["score"] -= 10
            result = f"Wrong! Correct answer: {correct_case}, {correct_use}"

        return render_template("index.html", quote=session["quote"]["text"],
                               score=session["score"], result=result,
                               submitted=True)

    return render_template("index.html", quote=session["quote"]["text"],
                           score=session["score"], result=None, submitted=False)

@app.route("/next")
def next_quote():
    session["quote"] = random.choice(QUOTES)
    return redirect(url_for("index"))