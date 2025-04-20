import os
from flask import Flask, render_template, request, redirect, url_for, session
import random
from data import QUOTES, NOVICE_QUOTES

app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config["SESSION_TYPE"] = "filesystem"

from flask_session import Session
Session(app)

@app.route("/", methods=["GET", "POST"])
def index():
    # initialize
    session.setdefault("score", 0)
    session.setdefault("mode", None)
    session.setdefault("quote", random.choice(NOVICE_QUOTES if session["mode"]=="Novice" else QUOTES))

    if request.method == "POST":
        case = request.form["case"]
        use  = request.form["use"]
        correct_case = session["quote"]["case"]
        correct_use  = session["quote"]["use"]

        points = 10 if session["mode"]=="Novice" else 15
        if case == correct_case and use in correct_use:
            session["score"] += points
            result = "✅ Correct!"
        else:
            session["score"] -= points
            # show all acceptable uses in the key
            result = f"❌ Wrong! Correct answer: {correct_case}, {', '.join(correct_use)}"

        return render_template("index.html",
                               quote=session["quote"]["quote"],
                               score=session["score"],
                               result=result,
                               submitted=True)

    return render_template("index.html",
                           quote=session["quote"]["quote"],
                           score=session["score"],
                           submitted=False)

@app.route("/next")
def next_quote():
    session["quote"] = random.choice(NOVICE_QUOTES if session["mode"]=="Novice" else QUOTES)
    return redirect(url_for("index"))

@app.route("/choose_mode", methods=["POST"])
def choose_mode():
    session["mode"] = request.form["mode"]
    session["score"] = 0
    # immediately pick a first quote in that mode
    session["quote"] = random.choice(NOVICE_QUOTES if session["mode"]=="Novice" else QUOTES)
    return redirect(url_for("index"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
