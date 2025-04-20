import os
from flask import Flask, render_template, request, redirect, url_for, session
import random
from data import QUOTES, NOVICE_QUOTES

app = Flask(__name__)
app.secret_key = "supersecretkey"

@app.route("/", methods=["GET", "POST"])
def mode_selection():
    return render_template("mode.html")

@app.route("/set_mode/<mode>")
def set_mode(mode):
    session["mode"] = mode
    session["score"] = 0
    session["correct"] = 0
    session["incorrect"] = 0
    session["quote"] = get_random_quote()
    return redirect(url_for("index"))

def get_random_quote():
    if session.get("mode") == "novice":
        return random.choice(NOVICE_QUOTES)
    else:
        return random.choice(QUOTES)

@app.route("/quiz", methods=["GET", "POST"])
def index():
    if "mode" not in session:
        return redirect(url_for("mode_selection"))

    if request.method == "POST":
        case = request.form.get("case")
        use = request.form.get("use")

        correct_case = session["quote"]["case"]
        correct_use = session["quote"]["use"]

        if case == correct_case and use == correct_use:
            result = "✅ Correct!"
            session["correct"] += 1
            session["score"] += 10 if session["mode"] == "novice" else 15
        else:
            result = f"❌ Wrong! Correct answer: {correct_case}, {correct_use}"
            session["incorrect"] += 1
            session["score"] -= 10 if session["mode"] == "novice" else 15

        return render_template("index.html",
                               quote=session["quote"]["text"],
                               score=session["score"],
                               correct=session["correct"],
                               incorrect=session["incorrect"],
                               result=result,
                               submitted=True)

    return render_template("index.html",
                           quote=session["quote"]["text"],
                           score=session["score"],
                           correct=session["correct"],
                           incorrect=session["incorrect"],
                           result=None,
                           submitted=False)

@app.route("/next")
def next_quote():
    session["quote"] = get_random_quote()
    return redirect(url_for("index"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)